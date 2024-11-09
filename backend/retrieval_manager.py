from sentence_transformers import SentenceTransformer

# Initialize the model once at the top level
model = SentenceTransformer("all-MiniLM-L6-v2")

def query_documents(collection, query):
    # Convert the user query to an embedding
    try:
        query_embedding = model.encode(query).tolist()
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return "I'm sorry, there was an issue generating the query embedding."

    # Attempt a simpler query on ChromaDB without `top_k`
    try:
        # Perform the query with only the query embedding
        results = collection.query(query_embedding)  # Adjusted query
        print("Retrieved Documents:", results)  # Debugging output
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return "I'm sorry, there was an issue retrieving the information."

    # Collect and format retrieved documents
    documents = []
    if results and "documents" in results:
        for doc in results["documents"]:
            if isinstance(doc, list):
                documents.append(" ".join(doc))
            else:
                documents.append(doc)
    response_text = (
        " ".join(documents)
        if documents
        else "I'm sorry, I couldn't find any relevant information."
    )

    return response_text
