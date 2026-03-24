# EMS OPQRST Pain Assessment Chatbot with RAG

A clinical triage chatbot that guides patients through the OPQRST pain assessment framework, retrieves relevant medical information from trusted public health sources, and provides a recommendation on whether they should seek medical attention.

> **Disclaimer:** This tool provides general information only and is not a substitute for professional medical advice.

---

## What It Does

1. Asks the patient 6 structured questions based on the OPQRST pain assessment model
2. Collects responses on: Onset, Provocation, Quality, Region, Severity, and Time
3. Retrieves relevant medical context from a local vector store built from NIH MedlinePlus
4. Uses LLaMA 3.3 (via Groq) to generate a triage recommendation grounded in the retrieved context
5. Recommends one of: Call 911, Go to the ER, See a doctor within 24-48 hours, or Monitor at home

---

## Architecture
```
User Input → LangGraph (OPQRST Flow) → RAG Retrieval (ChromaDB) → LLaMA 3.3 (Groq) → Recommendation
```

- **LangGraph** orchestrates the question/answer flow
- **ChromaDB** stores embedded medical document chunks from NIH MedlinePlus
- **sentence-transformers** (all-MiniLM-L6-v2) generates embeddings locally for free
- **Groq** runs LLaMA 3.3 70B for fast, free inference
- **FastAPI** serves the backend
- **HTML/JS** provides the frontend

---

## Prerequisites

- Python 3.12
- A free Groq API key — sign up at https://console.groq.com

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/rags03/EMS-Triage-RAG.git
cd EMS-Triage-RAG
```

### 2. Create a virtual environment
```bash
py -3.12 -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up your API key

Copy the example env file:
```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 6. Build the vector store (run once)

This scrapes NIH MedlinePlus pages and builds a local ChromaDB vector store:
```bash
python -m src.app.rag.ingest
```

### 7. Run the application
```bash
uvicorn src.app.server:app
```

### 8. Open in your browser

Go to: **http://localhost:8000**

---

## Project Structure
```
EMS-Triage-RAG/
├── src/
│   └── app/
│       ├── graph/
│       │   ├── edges.py          # LangGraph graph definition
│       │   ├── nodes.py          # AI logic, RAG retrieval, question flow
│       │   └── state.py          # State schema
│       ├── rag/
│       │   ├── ingest.py         # Scrapes and embeds medical documents
│       │   ├── retriever.py      # Retrieves relevant chunks from ChromaDB
│       │   ├── evaluate.py       # RAGAS evaluation script
│       │   ├── eval_dataset.py   # 12 synthetic OPQRST test cases
│       │   └── eval_results.csv  # Evaluation results
│       ├── server.py             # FastAPI backend
│       └── index.html            # Frontend UI
├── .env.example                  # API key template
├── requirements.txt              # Python dependencies
└── README.md
```

---

## RAG Evaluation (RAGAS)

The RAG pipeline was evaluated using [RAGAS](https://github.com/explodinggradients/ragas) on 12 synthetic OPQRST test cases covering scenarios from mild back pain to severe chest pain.

### Metrics
- **Faithfulness**: How grounded the recommendation is in retrieved medical documents
- **Answer Relevancy**: How relevant the answer is to the patient's specific symptoms

### Results
| Case | Faithfulness | Answer Relevancy |
|------|-------------|-----------------|
| Crushing chest pain radiating to arm | 0.455 | - |
| Dull lower back pain | 0.375 | - |
| Sharp lower right abdomen | 0.286 | - |
| Sudden tearing back pain | 0.615 | 0.521 |
| **Mean** | **0.433** | **0.521** |

### Analysis
- Mean faithfulness of 0.43 indicates partial grounding in retrieved documents
- Answer relevancy of 0.52 shows responses are moderately targeted to patient symptoms
- Missing answer relevancy scores are due to Groq API rate limiting during evaluation
- Scores would improve with clinical-grade sources such as ACEP guidelines or UpToDate

To rerun evaluation:
```bash
python -m src.app.rag.evaluate
```

---

## Technologies Used

- [LangGraph](https://github.com/langchain-ai/langgraph) — conversation flow orchestration
- [Groq](https://console.groq.com) — LLaMA 3.3 70B inference
- [ChromaDB](https://www.trychroma.com) — local vector store
- [sentence-transformers](https://www.sbert.net) — local embeddings (all-MiniLM-L6-v2)
- [RAGAS](https://github.com/explodinggradients/ragas) — RAG evaluation framework
- [FastAPI](https://fastapi.tiangolo.com) — backend API
- [Uvicorn](https://www.uvicorn.org) — ASGI server
