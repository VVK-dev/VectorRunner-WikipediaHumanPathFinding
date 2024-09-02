import os
from pinecone import Pinecone, ServerlessSpec, Index
from OpenAI_utils import get_embedding
from dotenv import load_dotenv, find_dotenv
import time

#Initailize environment variables
_ = load_dotenv(find_dotenv(filename = "Keys.env"))

#Set client
pinecone_client = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

#Check if an index exists

def index_exists(index_name : str) -> bool:
    
    if index_name in pinecone_client.list_indexes().names():
        
        return True
    else:
        
        return False

#Create starter index

def create_pinecone_index(index_name : str) -> Index:

    if (not index_exists(index_name)):
        
        #if the index doesn't already exist, create it
        pinecone_client.create_index(
        
            name = index_name,
            dimension = 1536,
            metric = "cosine",
            spec = ServerlessSpec(cloud = "aws", region = "us-east-1")
        )
            
        # wait for index to be initialized
        while not pinecone_client.describe_index(index_name).status['ready']:
            
            time.sleep(1)
    
    return pinecone_client.Index(name = index_name, host = pinecone_client.describe_index(index_name).host)


#Get and insert vector for each chunk into pinecone index

def insert_vectors_from_data(parent_page: str, filetext : list[str], index : Index):        

    #only add links not already in the db
        
    try:
    
        links_in_db : dict[str, dict] = index.fetch(ids = filetext)
      
        filetext = list(set(filetext) - set(links_in_db['vectors'].keys())) #using set difference
                
    except:
        
        #if encountered some error preventing check, just continue as normal
        
        pass
    
    #if there is nothing new to add, return
    if(len(filetext) == 0):
        return
    
    openai_embedding_prompt_counter : int = 0
    
    #filetext is the list of all chunks
    
    for i in range(0, len(filetext)):
        
        if(openai_embedding_prompt_counter >= 3000):
            
            #if rate limit hit, wait 1 minute to refresh it 
            
            time.sleep(60)
            openai_embedding_prompt_counter = 0
        
        vector_val = get_embedding(filetext[i])
        
        openai_embedding_prompt_counter += 1
        
        #use name of link as id, its vector as vector_val and the name of its parent page in metadata to create entry 
        #into vector index in proper format
        
        vector : dict = {"id" : filetext[i], "values": vector_val, "metadata" : {"parent_page" : parent_page}}        
        
        index.upsert(
        
            vectors = [vector],
            show_progress = False
        )


#Query the index

def query_pinecone_index(input_vector: list[float], parent_page :str, index : Index) -> list[str]:
    
    matches : list[dict] = index.query(
        
        vector = input_vector,
        top_k = 100,
        include_values= False,
        include_metadata = False,
        filter = {"parent_page" : {"$eq" : parent_page}}
                        
    ).get("matches") #This will return a list of dictionaries containing the IDs and similarity score of the top k 
    #matches
    
    #now get title of next possible wiki pages in route
    
    titles : list[str] = []
    
    for match in matches:
        
        titles.append(match.get("id"))
        
    return titles
