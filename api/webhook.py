from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os

from utils.whatsapp import WhatsAppClient
from utils.chat_engine import ChatEngine

app = FastAPI()
whatsapp_client = WhatsAppClient()
chat_engine = ChatEngine()

VERIFY_TOKEN = "liontech-nyonga-2024"

@app.get("/webhook")
async def verify_webhook(request: Request):
    # Parse params from the webhook verification request
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return JSONResponse(content=int(challenge))
        else:
            # Respond with '403 Forbidden' if verify tokens do not match
            raise HTTPException(status_code=403)
    raise HTTPException(status_code=400)

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        body = await request.json()
        print(f"Incoming webhook: {json.dumps(body, indent=2)}")
        
        # Check if it's a WhatsApp API event
        if 'entry' in body:
            for entry in body['entry']:
                for change in entry.get('changes', []):
                    if 'value' in change and 'messages' in change['value']:
                        for message in change['value']['messages']:
                            await process_message(message)
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return JSONResponse(content={"status": "error"}, status_code=500)

async def process_message(message):
    try:
        user_id = message['from']
        message_type = message['type']
        
        if message_type == 'text':
            user_message = message['text']['body']
            print(f"Processing message from {user_id}: {user_message}")
            
            # Get response from chat engine
            response = chat_engine.handle_message(user_id, user_message)
            
            # Send response via WhatsApp
            if response['type'] == 'text':
                if 'buttons' in response:
                    # Send interactive message with buttons
                    whatsapp_client.send_interactive_message(
                        user_id, 
                        response['message'],
                        response['buttons']
                    )
                else:
                    # Send simple text message
                    whatsapp_client.send_text_message(
                        user_id,
                        response['message']
                    )
            
        elif message_type in ['button', 'interactive']:
            # Handle button responses
            if 'button_reply' in message.get('interactive', {}):
                user_message = message['interactive']['button_reply']['title']
                response = chat_engine.handle_message(user_id, user_message)
                
                if response['type'] == 'text':
                    whatsapp_client.send_text_message(user_id, response['message'])
        
    except Exception as e:
        print(f"Error processing message: {e}")
        # Send error message to user
        try:
            whatsapp_client.send_text_message(
                user_id,
                "I apologize, but I'm experiencing technical difficulties. Please try again in a moment or contact us directly at +1647-381-8836"
            )
        except:
            pass

@app.get("/")
async def root():
    return {"message": "Nyonga Chatbot is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nyonga-chatbot"}