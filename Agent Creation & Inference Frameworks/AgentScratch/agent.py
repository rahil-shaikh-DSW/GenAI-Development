import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Initialize the Groq client with your API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define the initial chat history with a system message setting the therapist persona
chat_history = [
    {
        "role": "system",
        "content": (
            "You are a compassionate therapist who listens carefully, "
            "engages empathetically, and provides thoughtful, supportive advice. "
            "Your responses should help the user reflect on their feelings and thoughts "
            "in a non-judgmental manner."
        )
    }
]

# Start the conversation with an initial greeting from the therapist
print("Therapist: Hello, I'm here to listen. How are you feeling today? (Type 'exit' to quit.)")

while True:
    # Get user input
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Therapist: Goodbye, take care!")
        break

    chat_history.append({"role": "user", "content": user_input})

    chat_completion = client.chat.completions.create(
        messages=chat_history,
        model="llama-3.3-70b-versatile"  
    )

    # Extract the therapist's (assistant's) response
    therapist_response = chat_completion.choices[0].message.content
    print("Therapist:", therapist_response)

    # Append the assistant's response to the chat history for future context
    chat_history.append({"role": "assistant", "content": therapist_response})
