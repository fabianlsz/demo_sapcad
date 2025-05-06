usage: - create 2 terminals, one for backend purposes, one for frontend.
Backend terminal: run "pip install -r req.txt"
                  uvicorn main:app --reload

Frontend terminal: npm run dev

Upon opening the web application you will be able to chat with the bot (TODO, need server-sided AI Model implementation)
if you do not have llama3.2.gguf installed it will be impossible to connect and chat (FOR NOW!!)

Upload file lets you visualize the IFC file. Chat with the bot to apply changes to your IFC file. Visualize the changes upon completion.
Files are stored in a folder called uploads, they can also be viewed from backend url.
