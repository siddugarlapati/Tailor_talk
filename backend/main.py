from fastapi import FastAPI, Request
from agent import conversational_agent

app = FastAPI()

# This endpoint handles chat messages from the frontend
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data["message"]
    # Get the response from the agent
    response = conversational_agent(user_message)
    return {"response": response} 