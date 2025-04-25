from fastapi import FastAPI, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
from ifc_handler import process_ifc_file
from ai_chatbot import chat_with_ai
import shutil

app = FastAPI()

@app.get("/")
async def read_root():
    return HTMLResponse(
        """
        <h1>Backend is Running</h1>
        <p>Use the API to upload files and interact with the chatbot.</p>
        """
    )

@app.post("/upload/")
async def upload_file(file: UploadFile):
    # Save the uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse and process the IFC file
    metadata = process_ifc_file(file_location)

    return {"filename": file.filename, "metadata": metadata}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = chat_with_ai(data)
        await websocket.send_text(f"AI Response: {response}")