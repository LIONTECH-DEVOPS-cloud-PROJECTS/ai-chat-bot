from data.programs import PROGRAMS, AI_PATHWAYS, SUPPORT_NUMBER
from datetime import datetime
import json

class ChatEngine:
    def __init__(self):
        self.user_sessions = {}
    
    def get_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'stage': 'welcome',
                'program_interest': None,
                'pathway_interest': None,
                'eligibility_answers': {},
                'created_at': datetime.now().isoformat()
            }
        return self.user_sessions[user_id]
    
    def handle_message(self, user_id, message):
        session = self.get_session(user_id)
        current_stage = session['stage']
        
        if current_stage == 'welcome':
            return self.handle_welcome(user_id, message)
        elif current_stage == 'student_type':
            return self.handle_student_type(user_id, message)
        elif current_stage == 'program_selection':
            return self.handle_program_selection(user_id, message)
        elif current_stage == 'pathway_selection':
            return self.handle_pathway_selection(user_id, message)
        elif current_stage == 'eligibility_laptop':
            return self.handle_eligibility_laptop(user_id, message)
        elif current_stage == 'eligibility_payment':
            return self.handle_eligibility_payment(user_id, message)
        elif current_stage == 'eligibility_education':
            return self.handle_eligibility_education(user_id, message)
        elif current_stage == 'eligibility_online_study':
            return self.handle_eligibility_online_study(user_id, message)
        elif current_stage == 'schedule_call':
            return self.handle_schedule_call(user_id, message)
        else:
            return self.get_welcome_message()
    
    def handle_welcome(self, user_id, message):
        session = self.get_session(user_id)
        session['stage'] = 'student_type'
        
        welcome_msg = """Welcome to LionTech! 🦁 I hope you are having a good day!

Are you a:
1️⃣ New student
2️⃣ Existing student

Please reply with 1 or 2"""
        
        return {
            'type': 'text',
            'message': welcome_msg,
            'buttons': ['1', '2']
        }
    
    def handle_student_type(self, user_id, message):
        session = self.get_session(user_id)
        
        if message.strip() == '2':
            session['stage'] = 'existing_student'
            support_msg = f"""Thank you for reaching out! As an existing student, you'll get dedicated support from our team.

Please contact our student support team directly at:
📞 {SUPPORT_NUMBER}

They'll help you with:
• Course materials
• Technical issues  
• Progress tracking
• Any other concerns

Is there anything else I can help you with?"""
            
            return {
                'type': 'text', 
                'message': support_msg
            }
        
        elif message.strip() == '1':
            session['stage'] = 'program_selection'
            return self.get_program_selection_message()
        else:
            return {
                'type': 'text',
                'message': "Please choose 1 for New student or 2 for Existing student:",
                'buttons': ['1', '2']
            }
    
    def get_program_selection_message(self):
        program_list = "\n".join([f"{key}. {value}" for key, value in PROGRAMS.items()])
        
        message = f"""Great! Let's find the perfect program for you. 🎓

Please choose your program of interest:

{program_list}

Reply with the number (1-4) of your chosen program."""
        
        return {
            'type': 'text',
            'message': message,
            'buttons': ['1', '2', '3', '4']
        }
    
    def handle_program_selection(self, user_id, message):
        session = self.get_session(user_id)
        
        if message.strip() in PROGRAMS:
            session['program_interest'] = PROGRAMS[message.strip()]
            
            if message.strip() == '4':  # AI and Pathways
                session['stage'] = 'pathway_selection'
                return self.get_pathway_selection_message()
            else:
                session['stage'] = 'eligibility_laptop'
                acknowledgment = f"""Excellent choice! 🎯 You've selected: {PROGRAMS[message.strip()]}

Now, let me ask you a few quick eligibility questions to ensure this program is the right fit for you."""
                
                return {
                    'type': 'text',
                    'message': acknowledgment,
                    'next_stage': 'eligibility_laptop'
                }
        else:
            return {
                'type': 'text', 
                'message': "Please select a valid program number (1-4):",
                'buttons': ['1', '2', '3', '4']
            }
    
    def get_pathway_selection_message(self):
        pathway_list = "\n".join([f"{key}. {value}" for key, value in AI_PATHWAYS.items()])
        
        message = f"""You've selected AI and Pathways. Which specific pathway interests you?

{pathway_list}

Reply with the number (1-4) of your chosen pathway."""
        
        return {
            'type': 'text',
            'message': message,
            'buttons': ['1', '2', '3', '4']
        }
    
    def handle_pathway_selection(self, user_id, message):
        session = self.get_session(user_id)
        
        if message.strip() in AI_PATHWAYS:
            session['pathway_interest'] = AI_PATHWAYS[message.strip()]
            session['stage'] = 'eligibility_laptop'
            
            acknowledgment = f"""Perfect! 🚀 You've selected: {AI_PATHWAYS[message.strip()]}

Now, let me ask you a few quick eligibility questions to ensure this pathway is the right fit for you."""
            
            return {
                'type': 'text',
                'message': acknowledgment,
                'next_stage': 'eligibility_laptop'
            }
        else:
            return {
                'type': 'text',
                'message': "Please select a valid pathway number (1-4):",
                'buttons': ['1', '2', '3', '4']
            }
    
    def handle_eligibility_laptop(self, user_id, message):
        session = self.get_session(user_id)
        session['stage'] = 'eligibility_payment'
        
        message_text = """💻 Do you have access to a laptop or computer with reliable internet connection?

This is essential for our online learning platform.

Please reply:
✅ Yes - I have a laptop and internet
❌ No - I don't have consistent access"""
        
        return {
            'type': 'text',
            'message': message_text,
            'buttons': ['Yes', 'No']
        }
    
    def handle_eligibility_payment(self, user_id, message):
        session = self.get_session(user_id)
        session['eligibility_answers']['laptop'] = message
        session['stage'] = 'eligibility_education'
        
        message_text = """💰 Do you have the ability to pay the program fees, or would you like information about payment plans and financing options?

Please reply:
✅ Yes - I can pay the fees
💳 Maybe - I need payment plan info
❌ No - I need financing options"""
        
        return {
            'type': 'text',
            'message': message_text,
            'buttons': ['Yes', 'Maybe', 'No']
        }
    
    def handle_eligibility_education(self, user_id, message):
        session = self.get_session(user_id)
        session['eligibility_answers']['payment'] = message
        session['stage'] = 'eligibility_online_study'
        
        message_text = """🎓 What is your highest level of education completed?

Please reply with:
• High School
• Diploma 
• Bachelor's
• Master's
• Other"""
        
        return {
            'type': 'text',
            'message': message_text
        }
    
    def handle_eligibility_online_study(self, user_id, message):
        session = self.get_session(user_id)
        session['eligibility_answers']['education'] = message
        session['stage'] = 'schedule_call'
        
        message_text = """🌐 Have you studied online before?

This helps us understand how to best support your learning journey.

Please reply:
✅ Yes - I have online learning experience
🆕 No - This is my first time
🔄 Somewhat - Limited experience"""
        
        return {
            'type': 'text',
            'message': message_text,
            'buttons': ['Yes', 'No', 'Somewhat']
        }
    
    def handle_schedule_call(self, user_id, message):
        session = self.get_session(user_id)
        session['eligibility_answers']['online_study'] = message
        
        # Check eligibility (basic check)
        is_eligible = self.check_eligibility(session)
        
        if is_eligible:
            program_info = session['program_interest']
            if session.get('pathway_interest'):
                program_info += f" - {session['pathway_interest']}"
                
            message_text = f"""🎉 Excellent! Based on your responses, you appear to be a great candidate for our {program_info}!

Let's schedule a call to discuss:
• Program details and curriculum
• Payment options that work for you
• Start dates and schedule
• Any questions you have

📅 Click the link below to schedule your consultation call:
https://calendly.com/liontech-admissions/30min

Alternatively, you can reply with your preferred date and time, and we'll coordinate with you.

Welcome to the LionTech family! 🦁"""
        else:
            message_text = """Thank you for your interest in LionTech! Based on your responses, we recommend discussing alternative options with our admissions team.

Please contact us at {SUPPORT_NUMBER} to explore how we can help you achieve your tech career goals.

We have various programs and support options available!"""
        
        return {
            'type': 'text',
            'message': message_text
        }
    
    def check_eligibility(self, session):
        # Basic eligibility check - can be customized
        laptop_access = session['eligibility_answers'].get('laptop', '').lower()
        payment = session['eligibility_answers'].get('payment', '').lower()
        
        # Minimum eligibility: has laptop and some payment capability
        if 'yes' in laptop_access and ('yes' in payment or 'maybe' in payment):
            return True
        return False
    
    def get_welcome_message(self):
        return {
            'type': 'text',
            'message': "Welcome to LionTech! 🦁 I hope you are having a good day! How can I assist you today?"
        }