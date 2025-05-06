from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from ifc_handler import process_ifc_file, modify_ifc_entities, get_entity_summary
from ai_chatbot import chat_with_ai, parse_modification_request
import shutil
import os
import json
import asyncio
from typing import List
from datetime import datetime
import uuid

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Dictionary to store information about uploaded files
uploaded_files = {}

# Dictionary to store active WebSocket connections
connected_clients = {}

@app.get("/")
async def read_root():
    return HTMLResponse(
        """
        <h1>SAPCAD Backend is Running</h1>
        <p>Use the API to upload IFC files and interact with the chatbot.</p>
        """
    )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload an IFC file.
    The file will be saved in the uploads directory.
    """
    try:
        # Generate unique filename to prevent overwrites
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        original_filename = file.filename
        safe_filename = f"{timestamp}_{unique_id}_{original_filename}"

        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the IFC file to extract metadata
        metadata = process_ifc_file(file_path)

        # Store reference to the uploaded file
        file_info = {
            "original_filename": original_filename,
            "stored_filename": safe_filename,
            "file_path": file_path,
            "upload_time": timestamp,
            "metadata": metadata
        }

        file_id = unique_id
        uploaded_files[file_id] = file_info

        # Return success response with file ID and metadata
        return JSONResponse({
            "status": "success",
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": original_filename,
            "metadata": metadata
        })

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/files/")
async def list_files():
    """Get a list of all uploaded files"""
    files_list = []
    for file_id, file_info in uploaded_files.items():
        files_list.append({
            "file_id": file_id,
            "filename": file_info["original_filename"],
            "upload_time": file_info["upload_time"]
        })
    return {"files": files_list}

@app.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get detailed information about a specific file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    return {
        "file_id": file_id,
        "filename": file_info["original_filename"],
        "upload_time": file_info["upload_time"],
        "metadata": file_info["metadata"]
    }

@app.post("/modify/{file_id}")
async def modify_file(file_id: str, instruction: str = Form(...)):
    """
    Modify an IFC file based on a natural language instruction.
    """
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    # Parse the modification request using AI
    metadata = file_info.get("metadata", {})
    modification_data = parse_modification_request(instruction, metadata)

    # Modify the IFC file
    result = modify_ifc_entities(file_path, modification_data)

    # Update reference if modification was successful
    if "error" not in result and "modified_file" in result:
        # Update the file path reference
        new_file_path = result["modified_file"]

        # Generate a new ID for the modified file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_file_id = uuid.uuid4().hex[:8]

        # Process the new file to update metadata
        new_metadata = process_ifc_file(new_file_path)

        # Store reference to the modified file
        new_file_info = {
            "original_filename": f"modified_{file_info['original_filename']}",
            "stored_filename": os.path.basename(new_file_path),
            "file_path": new_file_path,
            "upload_time": timestamp,
            "metadata": new_metadata,
            "parent_file_id": file_id
        }

        uploaded_files[new_file_id] = new_file_info
        result["new_file_id"] = new_file_id

    return result

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket

    # Keep track of current file context
    current_file_id = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                # Try to parse as JSON to handle structured messages
                message_data = json.loads(data)

                # Check if this is a file selection message
                if "set_file_context" in message_data:
                    file_id = message_data["set_file_context"]
                    if file_id in uploaded_files:
                        current_file_id = file_id
                        file_summary = get_entity_summary(uploaded_files[file_id]["file_path"])
                        response = {
                            "type": "file_context",
                            "file_id": file_id,
                            "filename": uploaded_files[file_id]["original_filename"],
                            "summary": file_summary
                        }
                        await websocket.send_json(response)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"File with ID {file_id} not found"
                        })

                # Handle normal chat message
                elif "message" in message_data:
                    user_message = message_data["message"]

                    # Get file context if available
                    context = ""
                    if current_file_id and current_file_id in uploaded_files:
                        context = get_entity_summary(uploaded_files[current_file_id]["file_path"])

                    # Get AI response
                    ai_response = chat_with_ai(user_message, context)

                    # Check if this might be a modification request
                    if current_file_id and any(kw in user_message.lower() for kw in ["change", "modify", "update", "make", "set", "color", "change to"]):
                        # Try to parse as modification request
                        metadata = uploaded_files[current_file_id].get("metadata", {})
                        modification_data = parse_modification_request(user_message, metadata)

                        # If confidence is reasonable, suggest modification
                        confidence = modification_data.get("confidence", 0)
                        if confidence > 0.6:
                            modification_summary = {
                                "type": "modification_suggestion",
                                "entity_type": modification_data.get("entity_type", "unknown"),
                                "property": modification_data.get("property", "unknown"),
                                "new_value": modification_data.get("new_value", "unknown"),
                                "file_id": current_file_id
                            }

                            # Add modification suggestion to AI response
                            await websocket.send_json({
                                "type": "chat_response",
                                "message": ai_response,
                                "modification": modification_summary
                            })
                        else:
                            # Just send normal response
                            await websocket.send_json({
                                "type": "chat_response",
                                "message": ai_response
                            })
                    else:
                        # Just send normal response
                        await websocket.send_json({
                            "type": "chat_response",
                            "message": ai_response
                        })

                # Handle modification request
                elif "modify_file" in message_data:
                    if not current_file_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No file selected for modification"
                        })
                    else:
                        instruction = message_data["modify_file"]
                        file_path = uploaded_files[current_file_id]["file_path"]

                        # Parse the modification request
                        metadata = uploaded_files[current_file_id].get("metadata", {})
                        modification_data = parse_modification_request(instruction, metadata)

                        # Modify the file
                        result = modify_ifc_entities(file_path, modification_data)

                        # Handle successful modification
                        if "error" not in result and "modified_file" in result:
                            # Generate new file ID and store reference
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            new_file_id = uuid.uuid4().hex[:8]
                            new_file_path = result["modified_file"]

                            # Process the new file
                            new_metadata = process_ifc_file(new_file_path)

                            # Store reference to the modified file
                            new_file_info = {
                                "original_filename": f"modified_{uploaded_files[current_file_id]['original_filename']}",
                                "stored_filename": os.path.basename(new_file_path),
                                "file_path": new_file_path,
                                "upload_time": timestamp,
                                "metadata": new_metadata,
                                "parent_file_id": current_file_id
                            }

                            uploaded_files[new_file_id] = new_file_info

                            # Update current file context to the new file
                            current_file_id = new_file_id

                            # Send success response
                            await websocket.send_json({
                                "type": "modification_result",
                                "status": "success",
                                "message": f"File modified successfully. {result.get('entities_modified', 0)} entities updated.",
                                "new_file_id": new_file_id,
                                "details": result
                            })
                        else:
                            # Send error response
                            await websocket.send_json({
                                "type": "modification_result",
                                "status": "error",
                                "message": result.get("error", "Unknown error during modification"),
                                "details": result
                            })

            except json.JSONDecodeError:
                # Treat as plain text message if not JSON
                context = ""
                if current_file_id and current_file_id in uploaded_files:
                    context = get_entity_summary(uploaded_files[current_file_id]["file_path"])

                ai_response = chat_with_ai(data, context)
                await websocket.send_json({
                    "type": "chat_response",
                    "message": ai_response
                })

    except WebSocketDisconnect:
        # Remove client from connected clients
        if client_id in connected_clients:
            del connected_clients[client_id]
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"An error occurred: {str(e)}"
        })

# Serve static files for testing
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    # Print startup message
    print(f"Starting SAPCAD Backend server")
    print(f"Upload directory: {UPLOAD_DIR}")
    print(f"Visit http://localhost:8000 to verify the server is running")

    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)