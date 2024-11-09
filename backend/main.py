from flask import Flask, request, jsonify
from flask_cors import CORS
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

# Initialize PersistentClient and load the collection
client = PersistentClient(
    path="/tmp/chroma_data",  # Persistent storage path
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection("pdf_knowledge_base")
model = SentenceTransformer("all-MiniLM-L6-v2")


@app.route("/query", methods=["POST"])
def query():
    user_query = request.json.get("query")
    query_embedding = model.encode(user_query).tolist()

    # Query the ChromaDB collection
    results = collection.query(
        query_embedding, include=["documents", "metadatas", "distances"]
    )

    # Find the closest match based on distance
    response_data = []
    if "documents" in results and "metadatas" in results and "distances" in results:
        # Find the index of the closest document
        min_index = results["distances"][0].index(
            min(results["distances"][0])
        )  # Get the most relevant result

        # Extract the closest match information
        closest_match = {
            "text": results["documents"][0][min_index],
            "source": results["metadatas"][0][min_index].get("source"),
            "page": results["metadatas"][0][min_index].get("page"),
            "year": results["metadatas"][0][min_index].get("year"),
            "similarity": results["distances"][0][min_index],
        }

        return jsonify({"response": closest_match})
    else:
        return jsonify({"response": "No relevant documents found"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
