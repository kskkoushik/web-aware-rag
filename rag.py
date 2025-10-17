import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct , VectorParams
import google.generativeai as gemini_client
from dotenv import load_dotenv
from uuid import uuid4


load_dotenv()


collection_name = "Aira_web_knowledge_base"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)


gemini_client.configure(api_key=GOOGLE_API_KEY)
def ingest_knowledge(url , chunks):

    embeddings = [
     gemini_client.embed_content(
        model="models/embedding-001",
        content=sentence,
        task_type="retrieval_document",
        title="AIra Web Knowledge Base",
    )
    for sentence in chunks

   ]
   
    points = [
    PointStruct(
        id=uuid4().int & ((1 << 64) - 1),
        vector=response['embedding'],
        payload={"text": text , 'url' : url},
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

    results =  client.search(
    collection_name=collection_name,
    query_vector=gemini_client.embed_content(
        model="models/embedding-001",
        content= query,
        task_type="retrieval_query",
    )["embedding"],
    )

    results = results[:topk]

    elements = [hit.payload for hit in results]

    return elements










    




