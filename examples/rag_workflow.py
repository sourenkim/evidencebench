"""A small retrieval-like integration using the public library API."""

from evidencebench.chunking import chunk_documents
from evidencebench.evaluation import evaluate_answer
from evidencebench.ingestion import load_documents
from evidencebench.retrieval import LexicalRetriever


def main() -> None:
    documents = load_documents("examples/docs")
    chunks = chunk_documents(documents)
    retriever = LexicalRetriever(chunks, top_k=2, min_score=0.15)
    retrieved = retriever.retrieve("What does the guide recommend for older animals?")
    context = "\n".join(item.text for item in retrieved)
    answer = "Protein restriction is recommended for older animals."
    result = evaluate_answer(
        "What does the guide recommend for older animals?",
        answer,
        chunks,
        retriever=retriever,
    )
    print("Retrieved context:")
    print(context)
    print("\nEvaluation:")
    print(result.metrics.to_dict())


if __name__ == "__main__":
    main()
