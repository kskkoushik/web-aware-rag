from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fc import fetch_html
from rag import ingest_knowledge , query_knowledge_base
from chunker import chunk_html_content
from mdb import insert_data , get_all_data
from llm import generate
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import json

broker = RabbitmqBroker(url="amqp://guest:guest@localhost:5672/")
dramatiq.set_broker(broker)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",   # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://localhost:8080"
          # sometimes needed
    # "https://yourdomain.com" # production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # OR ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE...
    allow_headers=["*"],        # Allow all headers
)

@dramatiq.actor
def ingest_web_data(url):

   
    insert_data(url , "pending")

    html_content = fetch_html(target_url=url)

    chunks = chunk_html_content(html_content=html_content)

    ingest_knowledge(url1=url , chunks=chunks)

    insert_data(url , "completed")


@app.post("/ingest-data")
async def ingest_data_endpoint(request: Request):
    print("Ingest data endpoint called")
    data = await request.json()  # Add await here
    url = data['url'].strip()
    ingest_web_data.send(url)
    return JSONResponse(content={"status": "in progress", "url": url}, status_code=202)

@app.post("/query")
async def query_endpoint(request : Request):
    from fastapi.responses import StreamingResponse
    
    data = await request.json()  # Add await here
    query = data['query']

    async def generate_response():
        retrieved_docs = query_knowledge_base(query=query)
        docs_content = [doc["text"] for doc in retrieved_docs]
        retrived_str = "\n\n".join(docs_content)

        user_input = f"""
          user query : {query}
          ========================= WEB BASED KNOWLEDGE BASE FACTS =========================
          {retrived_str}
        """

        # First yield the sources
        yield f"data: {json.dumps({'type': 'sources', 'data': retrieved_docs})}\n\n"

        # Then yield the AI response
        for chunk in generate(user_input=user_input):
            yield f"data: {json.dumps({'type': 'text', 'data': chunk})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")


@app.get("/get-status")
def get_status():
    
    data = get_all_data()

    return data





    





