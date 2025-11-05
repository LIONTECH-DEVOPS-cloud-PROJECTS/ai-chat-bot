
## 3. WhatsApp Utility (utils/whatsapp.py)

```python
import requests
import json

class WhatsAppClient:
    def __init__(self):
        self.phone_number_id = "835054533029845"
        self.access_token = "EAAMNEyYzWCkBP5LXadTZB1DgxwfOO8PIoqo0KvZAQ9SYxkZCNaQkirrwEpT6W74luXkEY8aboWCwh4MVEMfaLVMZC4s69u2R0U7nXmyN0kZAr27ogGj2AjR2qZBIO21xcPTCwMZBf6XoXUZCzI71UNoIQcQl0OPHITzW8ZAHJCAiKgicnBzdaWCuXP5vf6HVQpjB3hAZCvS2NypdWl0ZC4TyuZCuv9oqF2mfZBZAxLUMnAz3Mo"
        self.url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
    def send_text_message(self, to, message):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message}
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()
    
    def send_interactive_message(self, to, message, buttons):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        button_components = []
        for i, button in enumerate(buttons, 1):
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": f"btn_{i}",
                    "title": button
                }
            })
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": message},
                "action": {
                    "buttons": button_components
                }
            }
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()
    
    def send_list_message(self, to, message, button_text, sections):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": message},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()