import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import time
from groq import Groq
from groq import RateLimitError
from src.app.rag.retriever import retrieve
from src.app.rag.eval_dataset import test_cases
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import pandas as pd
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

scorer_llm = LangchainLLMWrapper(ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
))
scorer_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

import time
from groq import RateLimitError

def generate_answer(case: dict, context: str) -> str:
    for attempt in range(3):  # retry up to 3 times
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # faster, higher rate limits
                messages=[
                    {"role": "system", "content": f"""You are an EMS triage assistant.
Based on the OPQRST assessment and retrieved medical context, recommend one of:
1. Call 911 immediately
2. Go to the ER today
3. See a doctor within 24-48 hours
4. Monitor at home and see a doctor if it worsens

Retrieved context:
{context}

Be concise and explain your reasoning."""},
                    {"role": "user", "content": f"""OPQRST Assessment:
- Onset: {case['onset']}
- Provocation: {case['provocation']}
- Quality: {case['quality']}
- Region: {case['region']}
- Severity: {case['severity']}
- Time: {case['time']}"""}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(10)
    return "Unable to generate recommendation due to rate limiting."

def run_evaluation():
    print("Running evaluation on test cases...\n")
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for i, case in enumerate(test_cases[:4]):
        print(f"Processing case {i+1}/{len(test_cases)}...")
        query = f"{case['quality']} pain in {case['region']} severity {case['severity']} onset {case['onset']}"
        context = retrieve(query)
        answer = generate_answer(case, context)

        questions.append(query)
        answers.append(answer)
        contexts.append([context])
        ground_truths.append(case["expected"])

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    print("\nRunning RAGAS metrics...")
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=scorer_llm,
        embeddings=scorer_embeddings
    )
    
    df = results.to_pandas()
    print("\n--- RAGAS Evaluation Results ---")
    print("Columns:", df.columns.tolist())
    print(df.to_string())

    df.to_csv("src/app/rag/eval_results.csv", index=False)
    print("\nResults saved to src/app/rag/eval_results.csv")

if __name__ == "__main__":
    run_evaluation()