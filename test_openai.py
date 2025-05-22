import openai
import os

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    # List available models
    response = client.models.list()
    print("API key is working! Available models:")
    for model in response.data:
        print(model.id)
except openai.AuthenticationError:
    print("Authentication failed: Invalid API key or token.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
