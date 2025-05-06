from llama_cpp import Llama
import os
import json

# Path to Llama 3.2 model (update this path to where your model is installed)
MODEL_PATH = "C:/Users/Fabian/Downloads/Llama-3.2-3B-Instruct-Q6_K_L.gguf"  # Update this to your actual model path

# Initialize the Llama model
model = None

def initialize_model():
    global model
    if model is None and os.path.exists(MODEL_PATH):
        model = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,  # Context window
            n_gpu_layers=-1  # Use all available GPU layers
        )
    return model is not None

def chat_with_ai(user_input: str, context: str = ""):
    """
    Send user input to Llama 3.2 and return the response.
    
    Args:
        user_input: The user's message
        context: Additional context about the IFC file
    """
    try:
        if not initialize_model():
            return "Error: Model not initialized. Please check if the model file exists."

        # Create a prompt with context about the IFC file if provided
        if context:
            prompt = f"""Context about the IFC model:
{context}

User request: {user_input}

Based on the IFC model information above, please provide a detailed response to the user's request.
If the user wants to modify the IFC model, explain what needs to be changed and how.
"""
        else:
            prompt = f"User: {user_input}\nAssistant: "

        # Get response from Llama model
        response = model.create_completion(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            stop=["User:", "\n\n"]
        )

        return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

def parse_modification_request(user_input: str, ifc_data: dict):
    """
    Parse a user request to determine what modifications to make to the IFC file.
    
    Args:
        user_input: The user's request
        ifc_data: Dictionary containing information about IFC entities
        
    Returns:
        Dictionary with modification instructions
    """
    try:
        if not initialize_model():
            return {"error": "Model not initialized"}

        # Create a structured prompt to extract modification details
        entities_json = json.dumps(ifc_data, indent=2)
        prompt = f"""
Here is information about IFC entities in a building model:
{entities_json}

User request: "{user_input}"

Based on the user request, extract the following information in JSON format:
{{
  "entity_type": "The type of entity to modify (e.g., 'IfcWall', 'IfcWindow', etc.)",
  "entity_ids": ["List of specific entity IDs to modify, or 'all' for all entities of this type"],
  "property": "The property to modify (e.g., 'color', 'material', 'dimension')",
  "new_value": "The new value for the property",
  "confidence": "A number between 0 and 1 indicating confidence in this interpretation"
}}

JSON response:
"""

        # Get structured response from model
        response = model.create_completion(
            prompt,
            max_tokens=256,
            temperature=0.2,  # Lower temperature for more deterministic output
            top_p=0.95,
            stop=["\n\n"]
        )

        result_text = response["choices"][0]["text"].strip()

        # Try to parse the JSON response
        try:
            modification = json.loads(result_text)
            return modification
        except json.JSONDecodeError:
            # If JSON parsing fails, return a basic response
            return {
                "entity_type": "unknown",
                "entity_ids": ["all"],
                "property": "unknown",
                "new_value": "unknown",
                "confidence": 0.0,
                "raw_response": result_text
            }

    except Exception as e:
        return {"error": str(e)}