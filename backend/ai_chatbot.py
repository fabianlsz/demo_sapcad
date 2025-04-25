import openai

# Set your OpenAI API key

def chat_with_ai(user_input: str):
    """
    Send user input to an AI chatbot and return the response.
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{user_input}",
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"