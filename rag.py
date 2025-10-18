import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct , VectorParams
import google.generativeai as gemini_client
from dotenv import load_dotenv
from uuid import uuid4
import requests



load_dotenv()


collection_name = "Aira_web_knowledge_base"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)


def ingest_knowledge(url1 , chunks):

    JINA_API_KEY = os.getenv("JINA_API_KEY")
    MODEL = "jina-embeddings-v3"
    DIMENSIONS = 768 # Or choose your desired output vector dimensionality.
    TASK = 'retrieval.passage' # For indexing, or set to retrieval.query for querying

    # Get embeddings from the API
    url = "https://api.jina.ai/v1/embeddings"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}",
    }

    data = {
        "input": chunks,
        "model": MODEL,
        "dimensions": DIMENSIONS,
        "task": TASK,
        "late_chunking": True,
    }

    response = requests.post(url, headers=headers, json=data)
     
    embeddings = [d["embedding"] for d in response.json()["data"]]
   
    points = [
    PointStruct(
        id=uuid4().int & ((1 << 64) - 1),
        vector=response,
        payload={"text": text , 'url' : url1},
    )
    for idx, (response, text) in enumerate(zip(embeddings, chunks))

   ] 
    
    if not client.collection_exists(collection_name=collection_name):

        client.create_collection(collection_name, vectors_config=
                VectorParams(
                    size=768,
                    distance=Distance.COSINE,
                )
        )

    client.upsert(collection_name, points)


def query_knowledge_base(query , topk=15):



    JINA_API_KEY = os.getenv("JINA_API_KEY")
    MODEL = "jina-embeddings-v3"
    DIMENSIONS = 768 # Or choose your desired output vector dimensionality.
    TASK = 'retrieval.query' # For indexing, or set to retrieval.query for querying

    # Get embeddings from the API
    url = "https://api.jina.ai/v1/embeddings"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}",
    }

    data = {
        "input": [query],
        "model": MODEL,
        "dimensions": DIMENSIONS,
        "task": TASK,
        "late_chunking": True,
    }

    response = requests.post(url, headers=headers, json=data)


    query_vector = response.json()["data"][0]["embedding"]


    results =  client.search(
    collection_name=collection_name,
    query_vector=query_vector
    )

    results = results[:topk]

    elements = [hit.payload for hit in results]

    print(elements)

    return elements








    




