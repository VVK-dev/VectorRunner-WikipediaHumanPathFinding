import os
import openai
from dotenv import load_dotenv, find_dotenv

#Initailize environment variables
_ = load_dotenv(find_dotenv(filename = "Keys.env"))

#Set client
client = openai.OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

#Get embedding for a string. 
def get_embedding(input_str: str) -> list[float]:

    response = client.embeddings.create(
        input = input_str,
        dimensions = 1536,
        model="text-embedding-3-small"
    )
    
    return response.data[0].embedding
