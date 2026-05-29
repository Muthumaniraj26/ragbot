from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
# Using the updated LangChain Ollama integrations
from langchain_ollama import OllamaEmbeddings, ChatOllama

app = FastAPI(title="Local AI Handyman Finder API")

# 1. Initialize Local Ollama Models
# Ensure Ollama is running in the background (default: http://localhost:11434)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = ChatOllama(model="llama3", temperature=0.3)

# Mock Databases
workers_db = {}
customers_db = {}
vector_store = None

# ---- Pydantic Models ----
class WorkerRegister(BaseModel):
    username: str
    password: str
    name: str
    profession: str  # carpenter, plumber, electrician, etc.
    phone: str
    rating: float = 5.0
    bio: str

class CustomerRegister(BaseModel):
    username: str
    password: str
    name: str
    location: str

class SearchQuery(BaseModel):
    customer_query: str

# ---- Sync Vector DB ----
def update_vector_store():
    global vector_store
    if not workers_db:
        return
    
    texts = []
    metadatas = []
    
    for username, worker in workers_db.items():
        # Rich text layout for semantic local lookup
        combined_text = f"Profession: {worker['profession']}. Name: {worker['name']}. Bio: {worker['bio']}"
        texts.append(combined_text)
        metadatas.append({
            "name": worker["name"],
            "profession": worker["profession"],
            "phone": worker["phone"],
            "rating": worker["rating"],
            "bio": worker["bio"]
        })
        
    # Local FAISS indexing using local embeddings
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

# ---- API Endpoints ----

@app.post("/register/worker")
def register_worker(worker: WorkerRegister):
    if worker.username in workers_db:
        raise HTTPException(status_code=400, detail="Worker already exists")
    
    workers_db[worker.username] = worker.dict()
    update_vector_store()  
    return {"message": f"Worker {worker.name} registered successfully locally!"}

@app.post("/register/customer")
def register_customer(customer: CustomerRegister):
    if customer.username in customers_db:
        raise HTTPException(status_code=400, detail="Customer already exists")
    
    customers_db[customer.username] = customer.dict()
    return {"message": f"Customer {customer.name} registered successfully!"}

@app.post("/search")
def search_workers(query: SearchQuery):
    global vector_store
    if not vector_store:
        return {"response": "No workers registered in the local system yet."}
    
    # 2. Local Semantic Search
    docs = vector_store.similarity_search(query.customer_query, k=2)
    
    if not docs:
        return {"response": "No matching workers found for your request."}
    
    # 3. Format the retrieved context block
    context = ""
    for doc in docs:
        meta = doc.metadata
        context += f"- Name: {meta['name']}, Profession: {meta['profession']}, Phone: {meta['phone']}, Rating: {meta['rating']}/5, Bio: {meta['bio']}\n\n"
    
    # 4. Construct Prompt for local LLM execution
    prompt = f"""
    You are an AI Assistant helping a customer find a local service worker.
    Based ONLY on the following available workers, recommend the best match(es) for the customer's request.
    Always print their Name, Profession, Phone Number, Rating, and a brief reason why they match.

    Customer Request: {query.customer_query}

    Available Workers:
    {context}
    """
    
    # Invoke the local Llama3 instance
    try:
        response = llm.invoke(prompt)
        return {"response": response.content}
    except Exception as e:
        return {"response": f"Failed to communicate with local Ollama instance: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)