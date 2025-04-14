# chainlit_app.py
import os
import chainlit as cl
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(
    api_key=os.environ.get("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")  # Replace with your env var name if different
)

# Default model - adjust as needed
DEFAULT_MODEL = "llama3-70b-8192"

@cl.on_chat_start
def on_chat_start():
    # Send an initial greeting message
    cl.send_message("Hello! I'm a chatbot powered by Groq. How can I help you today?")
    
    # Initialize conversation history in the session
    cl.session.set("messages", [])

@cl.on_message
def on_message(message: cl.Message):
    # Retrieve the conversation history from the session
    messages = cl.session.get("messages")
    
    # Append the user's message to the history
    messages.append({"role": "user", "content": message.content})
    
    # Send a placeholder message to indicate processing
    thinking_msg = cl.send_message("Thinking...")
    
    try:
        # Call the Groq API with the conversation history as context
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )
        
        # Extract the assistant's response from the API result
        assistant_response = response.choices[0].message.content
        
        # Append the assistant's response to the history
        messages.append({"role": "assistant", "content": assistant_response})
        cl.session.set("messages", messages)
        
        # Update the placeholder message with the actual response
        cl.update_message(thinking_msg, assistant_response)
    except Exception as e:
        # Update the placeholder message in case of error
        cl.update_message(thinking_msg, f"Error: {str(e)}")

@cl.on_settings_update
def on_settings_update(settings):
    # Optionally handle settings updates (model selection, temperature, etc.)
    cl.send_message(f"Settings updated: {settings}")
