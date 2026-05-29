 1. Project Directory Structure
When you deploy this code base on a new machine, your project folder should look exactly like this.
Plaintext
rag-services-product/
│
├── .env                    # Cryptographic keys & configuration variables
├── requirements.txt        # Python dependency manifest
├── README.md               # Setup and runtime instructions
│
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI entry point, application routing, and ASGI server config
│   ├── database.py         # SQLite connection pool and core CRUD actions
│   ├── auth.py             # Bcrypt password hashing & PyJWT token infrastructure
│   ├── vector_engine.py    # LangChain, Ollama embeddings, and FAISS index persistence
│   └── scraper.py          # BeautifulSoup4 web parsing and DuckDuckGo extraction
│
└── frontend/
    ├── __init__.py
    ├── app.py              # Streamlit entry point & main page layout
    ├── UI_components.py    # Custom CSS injectors & HTML card renderer templates
    └── session_manager.py  # User authentication session state controllers

    
2. Database Schema Design (SQLite)
Your backend uses a unified relational database layout file named local_market.db. The tables are structured as follows:
Workers Table (workers)
Stores verified platform partners who have registered an official profile.
•	username (TEXT, PRIMARY KEY): Unique login identifier.
•	password_hash (TEXT): Cryptographically salted bcrypt string.
•	name (TEXT): Display name or company entity name.
•	profession (TEXT): Categorization tag (e.g., plumber, electrician, carpenter).
•	phone (TEXT): Verified phone number for clickable dialers.
•	email (TEXT): Direct customer contact email address.
•	address (TEXT): Physical workshop or service area radius address.
•	rating (REAL): Dynamically calculated average performance score (default is 5.0).
•	bio (TEXT): Detailed professional history read by the RAG model for context mapping.
Customers Table (customers)
Stores registered customer tracking variables.
•	username (TEXT, PRIMARY KEY): Unique customer identifier.
•	password_hash (TEXT): Secure customer password representation.
•	name (TEXT): Customer display name.
•	location (TEXT): Default region city or zip code block.
Reviews Table (reviews)
Stores public feedback entries tied to platform workers.
•	id (INTEGER, PRIMARY KEY, AUTOINCREMENT): Sequential review identifier.
•	worker_username (TEXT, FOREIGN KEY): Maps explicitly back to a record in the workers table.
•	customer_name (TEXT): Display name of the user leaving the feedback.
•	rating (INTEGER): An integer value from 1 to 5.
•	comment (TEXT): Text summary of the user's experience.
•	timestamp (TEXT): System-generated date and time stamp.


🔌 3. API Endpoint Specification (FastAPI Architecture)
The API gateway acts as the brain, processing requests from the Streamlit UI and routing them to the data and AI layers.
HTTP Method	Route Endpoint	Payload Model	Security Level	Purpose / Action
POST	/register/worker	WorkerRegister	Public	Hashes password, commits worker to SQLite, rebuilds FAISS vector cache.
POST	/register/customer	CustomerRegister	Public	Inserts customer variables into the relational database.
POST	/login	LoginRequest	Public	Validates hash, issues signature-signed 24h JWT token.
GET	/worker/profile	None	Bearer JWT Required	Decodes token sub-claims, pulls profile stats back to the user.
POST	/submit-review	ReviewSubmit	Public	Inserts feedback, executes automated database recalculation of worker rating.
GET	/reviews/{username}	None	Public	Returns chronological review entries for a specific worker profile.
POST	/search	SearchQuery	Public	Primary RAG Router. Runs simultaneous FAISS similarity check + BeautifulSoup backup.


 4. Unified RAG Search & Web Fallback Workflow
When a query is received, the backend executes a dual-track routing algorithm to prevent "zero results" errors:
Plaintext
                [ Customer Search Input Query ]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
   [ Embed via nomic-embed-text ]     [ Execute Live Web Scraper ]
                │                             │
                ▼                             ▼
    [ FAISS Vector DB Search ]       [ Parse DuckDuckGo HTML Data ]
  (Checks similarity score vs Bios)    (Extract Title, Address, Phone)
                │                             │
        ┌───────┴───────┐                     │
        ▼               ▼                     │
  (Score >= 0.7)  (Score < 0.7)               │
        │               │                     │
     [ YES ]         [ NO ]                   │
        │               └──────────────┐      │
        ▼                              ▼      ▼
[ Pull SQL Records ]         [ Combined Response Package ]
[ Compile with Llama3 ]                    │
        │                                  ▼
        ▼                      [ UI Columns Engine Split ]
[ Display: PREMIUM CARDS ]        ┌────────┴────────┐
                                  ▼                 ▼
                         [ Premium Panel ]   [ Web Scraped Panel ]


5. Core Stack Dependencies (requirements.txt)
To roll this setup out to a clean server or a brand-new computer environment, save this requirements text file to your directory to ensure exact package matching:
Plaintext
fastapi==0.110.0
uvicorn==0.28.0
streamlit==1.32.0
langchain-community==0.0.28
langchain-ollama==0.0.1
faiss-cpu==1.8.0
beautifulsoup4==4.12.3
bcrypt==4.1.2
pyjwt==2.8.0
python-dotenv==1.0.1


6. Step-by-Step Implementation and Deployment Plan
Follow this exact production execution timeline to assemble, test, and host the code files:
Phase 1: Environment Provisioning
1.	Download and install your system package version of Python 3.10+.
2.	Install the local inference manager Ollama onto the desktop system environment.
3.	Open a terminal pane and download your local network open-weights models:
Bash
ollama pull nomic-embed-text
ollama pull llama3
Phase 2: System Coding Setup
1.	Create your root framework folder structure based on the project layout directory shown in Section 1.
2.	Initialize your secure configuration settings inside a hidden .env file by auto-generating a unique key:
Bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > .env
3.	Install all necessary dependencies globally using the pip configuration controller:
Bash
pip install -r requirements.txt
Phase 3: Launching the Platform Service Cluster
1.	Boot Up the Backend Engine: Open a fresh terminal shell and run Uvicorn. This initializes the SQLite schemas, logs any structural adjustments, and listens for requests at port 8000:
Bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
2.	Boot Up the Frontend Interface: Open an alternate terminal window pane and launch the user application. This compiles the web components and automatically opens a browser page at port 8501:
Bash
streamlit run frontend/app.py
3.	Perform End-to-End Testing: * Navigate to the Partner Desk tab, register an active trade technician with an intensive bio (e.g., specializing in central heating systems), and verify that they can log back in.
o	Switch to the Customer Portal and perform a relevant semantic search. The worker will instantly populate the high-visibility premium row with active email links and review submission forms.
o	Search for an unmapped skill or remote service that doesn't exist in your local database. The system will automatically use the backup web scraper to pull directory cards, including extracted web ratings and contact links, ensuring your user interface is never blank.

