# 🧠 Neural Knowledge Base

### Context-Aware Web RAG System with Intelligent Background Processing

A sophisticated retrieval-augmented generation (RAG) system that ingests web content, chunks it intelligently, embeds it with state-of-the-art models, and serves context-aware answers powered by Gemini 2.5. Built with enterprise-grade architecture using RabbitMQ and Dramatiq for robust, scalable background processing.

---

## 🎯 Project Overview

Neural Knowledge Base transforms raw web data into a searchable, intelligent knowledge base. Users can submit URLs, which are automatically processed through a sophisticated pipeline, indexed into a vector database, and queried using semantic similarity. The system combines web scraping, text chunking, vector embeddings, and generative AI to deliver precise, source-grounded answers.

**Key Capabilities:**
- 🌐 **Web Data Ingestion** - Scrape and process URLs with Firecrawl
- 🔀 **Intelligent Chunking** - Semantically meaningful text segmentation
- 🎯 **Vector Embeddings** - High-dimensional semantic understanding
- ⚡ **Background Processing** - Non-blocking async task handling
- 🤖 **Generative AI** - Context-aware responses via Gemini 2.5
- 📊 **Real-time Status Tracking** - Monitor ingestion pipeline
- 💾 **Persistent Storage** - MongoDB for metadata + Qdrant for vectors

---

## 🏗️ Architecture & Design Choices

### System Architecture Diagram

<img width="5218" height="1812" alt="image" src="https://github.com/user-attachments/assets/1618722c-beca-4be0-9e74-b14606a2f608" />


### Why This Architecture?

**Background Processing with RabbitMQ + Dramatiq:**
- **Why not Redis?** While Redis is fast for caching, RabbitMQ provides true message durability, better handling of slow consumers, and superior failure recovery. For a production RAG system handling potentially large documents, RabbitMQ's reliability and persistence guarantees are invaluable.
- **Dramatiq Advantages:** Lightweight, strongly-typed task definitions, built-in retries, task scheduling, and lower overhead compared to Celery while maintaining robust error handling.
- **Non-blocking URLs:** Ingestion runs asynchronously, so the API responds immediately while processing happens in background workers.

**Separate Vector & Metadata Stores:**
- **Qdrant for Vectors:** Purpose-built vector database with efficient similarity search, clustering, and filtering capabilities.
- **MongoDB for Metadata:** Flexible schema for tracking ingestion status, URLs, and timestamps. Easy to query and update status without disrupting vector operations.

**Streaming Response for Queries:**
- Server-Sent Events (SSE) for real-time response streaming, delivering sources first, then AI-generated text in chunks for better UX.

---

## 🛠️ Technology Stack & Justification

| Component | Technology | Why? |
|-----------|-----------|------|
| **Web Framework** | FastAPI | Async-native, built-in streaming, automatic API documentation, exceptional performance |
| **Message Broker** | RabbitMQ | Enterprise-grade durability, robust failure handling, superior to Redis for heavy workloads |
| **Task Queue** | Dramatiq | Simpler than Celery, excellent RabbitMQ integration, lower memory footprint, strongly-typed tasks |
| **Web Scraping** | Firecrawl | Handles JavaScript rendering, respects robots.txt, returns clean HTML |
| **Text Chunking** | Unstructured.io | Intelligent document parsing, preserves semantic meaning, handles multiple formats |
| **Embeddings** | Jina AI (v3) | 768-dimensional vectors, optimized for retrieval, supports late chunking for better results |
| **Vector DB** | Qdrant | Lightning-fast similarity search, built-in filtering, cloud-ready, excellent Python SDK |
| **Metadata DB** | MongoDB | Flexible schemas, easy status tracking, native JSON support |
| **LLM** | Gemini 2.5 Flash | Fast inference, excellent reasoning, built-in Google Search integration |
| **Frontend** | Vanilla JS + HTML/CSS | No build step, real-time streaming support, responsive design with glassmorphism |

---

## 💾 Database Schema Explanation

### MongoDB - `data_status` Collection

Tracks ingestion pipeline status and metadata for each URL.

```json
{
  "_id": ObjectId("..."),
  "url": "https://example.com/article",
  "status": "completed",                    // "pending" | "completed" | "failed"
  "inserted_at": ISODate("2024-10-18T..."),
  "updated_at": ISODate("2024-10-18T...")
}
```

**Schema Design Rationale:**
- Upsert strategy prevents duplicate entries for the same URL
- Status field enables real-time progress tracking in frontend
- Timestamps allow sorting and audit trails

### Qdrant - Vector Collection: `Aira_web_knowledge_base`

Stores embeddings and their associated metadata for semantic search.

```json
{
  "id": 12345678901234567,                  // Unique integer ID
  "vector": [0.123, -0.456, ...],          // 768-dim Jina embedding
  "payload": {
    "text": "Chunk text content...",
    "url": "https://example.com/article"
  }
}
```

**Configuration:**
- Vector Size: **768 dimensions** (Jina v3 standard)
- Distance Metric: **COSINE** (optimal for embeddings)
- Collection Strategy: **Create on first ingest** (lazy initialization)

**Why COSINE?** Cosine distance measures angle between vectors, ideal for normalized embeddings. Works perfectly for semantic similarity regardless of magnitude.

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

---

### 1. **Ingest Data Endpoint**

Submit a URL for processing and indexing.

**Endpoint:** `POST /ingest-data`

**Request Body:**
```json
{
  "url": "https://docs.python.org/3/library/asyncio.html"
}
```

**Response (202 Accepted):**
```json
{
  "status": "in progress",
  "url": "https://docs.python.org/3/library/asyncio.html"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/ingest-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org/3/library/asyncio.html"}'
```

**Behind the Scenes:**
1. Task immediately queued to RabbitMQ via Dramatiq
2. Database marked as "pending"
3. Background worker fetches HTML via Firecrawl
4. Content chunked using Unstructured
5. Chunks embedded with Jina AI
6. Vectors indexed in Qdrant
7. Status updated to "completed" in MongoDB

---

### 2. **Query Endpoint**

Query the knowledge base with streaming responses.

**Endpoint:** `POST /query`

**Request Body:**
```json
{
  "query": "How does async/await work in Python?"
}
```

**Response (200 OK - Server-Sent Events Stream):**
```
data: {"type": "sources", "data": [{"text": "...", "url": "https://..."}, ...]}

data: {"type": "text", "data": "Async/await is a syntax for asynchronous programming "}
data: {"type": "text", "data": "that allows you to write non-blocking code that looks like "}
...
```

**cURL Example (with streaming):**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does async/await work in Python?"}' \
  -N  # Disable buffering for real-time streaming
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Your question here' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      console.log(data);
    }
  }
}
```

**Response Flow:**
1. Sources retrieved from Qdrant via semantic search (top-15)
2. Sources list streamed first to show retrieval
3. Query + sources sent to Gemini 2.5
4. AI response streamed token-by-token
5. Frontend renders real-time as tokens arrive

---

### 3. **Get Status Endpoint**

Retrieve status of all ingested URLs.

**Endpoint:** `GET /get-status`

**Response (200 OK):**
```json
[
  {
    "url": "https://example.com/article",
    "status": "completed",
    "inserted_at": "2024-10-18T10:30:00",
    "updated_at": "2024-10-18T10:35:00"
  },
  {
    "url": "https://example.com/another",
    "status": "pending",
    "inserted_at": "2024-10-18T10:40:00",
    "updated_at": "2024-10-18T10:40:00"
  }
]
```

**cURL Example:**
```bash
curl http://localhost:8000/get-status
```

**Frontend Usage:**
Polled every 3 seconds to update status list and show completion notifications.

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- RabbitMQ (running on localhost:5672)
- Docker + Docker Compose (optional, for containerization)
- API Keys: Google, Jina, Firecrawl, Qdrant

### Step 1: Clone & Install Dependencies

```bash
git clone <your-repo>
cd neural-knowledge-base

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Web Scraping
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Embeddings
JINA_API_KEY=your_jina_api_key_here

# Databases
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/Aira_db?retryWrites=true&w=majority
QDRANT_URL=https://your-qdrant-instance.example.com
QDRANT_API_KEY=your_qdrant_api_key_here

# Message Broker (RabbitMQ)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

**Getting API Keys:**

- **Google API:** [console.cloud.google.com](https://console.cloud.google.com) → Enable Generative AI API
- **Firecrawl:** [firecrawl.dev](https://firecrawl.dev) → Sign up and create API key
- **Jina AI:** [jina.ai](https://jina.ai) → Create account for embeddings
- **Qdrant:** [cloud.qdrant.io](https://cloud.qdrant.io) → Create cluster
- **MongoDB:** [mongodb.com/cloud](https://mongodb.com/cloud) → Create Atlas cluster

### Step 3: Start RabbitMQ

**Using Docker (Recommended):**
```bash
docker run -d --name rabbitmq -p 5672:15672 rabbitmq:4-management
```

Access management UI at `http://localhost:15672` (default: guest/guest)

**Using Local Installation:**
```bash
# macOS
brew install rabbitmq
brew services start rabbitmq-server

# Ubuntu
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
```

### Step 4: Start Backend Services

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app:app --reload
# Starts on http://localhost:8000
```

**Terminal 2 - Dramatiq Worker(s):**
```bash
# Single worker
dramatiq app

# Multiple workers for parallel processing (recommended)
dramatiq app -t 4  # 4 threads
dramatiq app -p 2 -t 4  # 2 processes, 4 threads each
```

**Terminal 3 - Frontend Server:**
```bash
python -m http.server 8080
# Serves frontend on http://localhost:8080
```

### Step 5: Verify Everything

- **Frontend:** http://localhost:8080
- **API Docs:** http://localhost:8000/docs
- **RabbitMQ UI:** http://localhost:15672

---

## 🐳 Docker Setup

### Docker Compose (`docker-compose.yml`)

[**Click to view/embed Docker Compose configuration** - link to embedded Docker Compose file]

Start entire stack:
```bash
docker-compose up -d
```

Stop everything:
```bash
docker-compose down
```

---

## 📹 Demo Video

[![Watch the video](https://img.youtube.com/vi/2-pYA6kW3QM/hqdefault.jpg)](https://www.youtube.com/watch?v=2-pYA6kW3QM)


Expected demo flow:
1. ✅ Frontend walkthrough
2. ✅ Submitting a URL for ingestion
3. ✅ Real-time status updates
4. ✅ Background worker processing
5. ✅ Querying the knowledge base
6. ✅ Streaming response with sources
7. ✅ Multiple concurrent ingestions
8. ✅ Error handling & recovery

**[INSERT VIDEO LINK]**

---

## 🔄 Complete Workflow Example

### Scenario: Ingest Python Documentation and Ask Questions

**Step 1:** Submit URL
```bash
curl -X POST http://localhost:8000/ingest-data \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org/3/library/asyncio.html"}'
```

**Step 2:** Status shows "pending" in frontend

**Step 3:** Background worker:
- Fetches page with Firecrawl
- Chunks into ~50 pieces of semantically meaningful text
- Generates 50 × 768-dim embeddings
- Indexes in Qdrant
- Updates status to "completed"

**Step 4:** Query the knowledge base
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I handle multiple async tasks concurrently?"}' \
  -N
```

**Step 5:** Response streams:
1. Sources with their URLs
2. AI-generated answer synthesizing the chunks

---

## ⚙️ Performance Tuning

### Dramatiq Workers
Adjust based on your hardware:
```bash
# For CPU-bound ingestion
dramatiq app -p 4 -t 8  # 4 processes, 8 threads each

# For I/O-bound (web scraping)
dramatiq app -t 32  # Single process, 32 threads
```

### Qdrant Vector Search
- Batch multiple queries if possible
- Use `limit=15` for top-15 results (configurable in `rag.py`)
- Consider indexing strategy for 100k+ vectors

### MongoDB Queries
- Index on `url` field for faster lookups
- Use TTL indexes for automatic old record cleanup

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ConnectionRefusedError` on RabbitMQ | Ensure RabbitMQ is running: `docker ps` or check `brew services` |
| `GOOGLE_API_KEY not found` | Verify `.env` file exists and is properly loaded |
| Slow ingestion | Increase Dramatiq workers or check Firecrawl API rate limits |
| No sources returned | Ensure Qdrant collection was created (happens on first ingest) |
| Frontend not loading | Verify `python -m http.server 8080` is running |

---

## 📚 Project Structure

```
neural-knowledge-base/
├── app.py                 # FastAPI main application
├── fc.py                  # Firecrawl web scraping
├── chunker.py             # Document chunking (Unstructured)
├── rag.py                 # RAG logic (Jina + Qdrant)
├── llm.py                 # Gemini 2.5 streaming
├── mdb.py                 # MongoDB operations
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker orchestration
└── README.md              # This file
```

---

## 🎨 Frontend Features

- **Real-time Status Tracking:** Live updates of ingestion pipeline
- **Streaming Chat:** Token-by-token response delivery
- **Source Attribution:** Click through to original web pages
- **Modern UI:** Glassmorphism design with purple/cyan theme
- **Responsive Design:** Works on desktop and tablet
- **Error Handling:** Toast notifications for user feedback

---

## 🔐 Security Considerations

- [ ] Keep `.env` secrets in `.gitignore`
- [ ] Use HTTPS in production (update CORS origins)
- [ ] Rate limit API endpoints
- [ ] Validate URL inputs before ingestion
- [ ] Use environment-specific credentials
- [ ] Enable RabbitMQ authentication (change guest/guest)
- [ ] Use Qdrant API key in production

---

## 📈 Scaling Strategy

1. **Horizontal:** Add more Dramatiq workers across multiple machines
2. **Message Queue:** RabbitMQ scales to millions of messages/sec
3. **Vector DB:** Qdrant supports clustering and replication
4. **MongoDB:** Use sharding for large metadata collections
5. **Frontend:** Serve static assets via CDN

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 💡 Future Enhancements

- [ ] Multi-language support for embeddings
- [ ] Document update detection and re-indexing
- [ ] User authentication and rate limiting
- [ ] Analytics dashboard for ingestion metrics
- [ ] Support for PDF, DOCX, and other formats
- [ ] Fine-tuned embedding models for domain-specific queries
- [ ] Caching layer for frequent queries
- [ ] Webhook notifications on ingestion completion

---

## 🙋 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section above

---

**Built with ❤️ using FastAPI, RabbitMQ, Qdrant, and Gemini 2.5**
