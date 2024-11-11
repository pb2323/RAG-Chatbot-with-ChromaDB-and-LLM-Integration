import pika
import json
import openai
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize OpenAI API key
openai.api_key = 'YOUR_API_KEY'

# Initialize ChromaDB and SentenceTransformer
client = PersistentClient(
    path="/tmp/chroma_data",
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection("pdf_knowledge_base")
model = SentenceTransformer("all-MiniLM-L6-v2")

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='query_queue')
channel.queue_declare(queue='response_queue')

# Function to generate a refined response using OpenAI
def generate_openai_response(user_query, context_text):
    prompt = f"User query: {user_query}\n\nContext:\n{context_text}\n\nPlease provide a concise and relevant answer based on this information."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access and prefer it
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise answers based on provided context."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred while generating the response with OpenAI."

# Process function to handle incoming queries
def process_query(ch, method, properties, body):
    # Decode query and process it
    request_data = json.loads(body)
    user_query = request_data.get("query")
    query_embedding = model.encode(user_query).tolist()

    # Query the ChromaDB collection
    results = collection.query(
        query_embedding, include=["documents", "metadatas", "distances"]
    )

    response_data = {"response": "No relevant documents found"}  # Default response

    # Check if there are results
    if "documents" in results and results["documents"]:
        min_index = results["distances"][0].index(min(results["distances"][0]))
        closest_match = {
            "text": results["documents"][0][min_index],
            "source": results["metadatas"][0][min_index].get("source"),
            "page": results["metadatas"][0][min_index].get("page"),
            "year": results["metadatas"][0][min_index].get("year"),
            "similarity": results["distances"][0][min_index],
        }
       
        # Generate a refined response from OpenAI
        context_text = closest_match["text"]
        print("context: "+context_text)
        openai_response = generate_openai_response(user_query, context_text)
        # openai_response="ABC"
        response_data = {
            "response": openai_response,
            "context": closest_match  # Include original context for reference if needed
        }

        print("response_data: "+response_data["response"])

    # Publish the refined response back to response_queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response_data)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming messages from query_queue
channel.basic_consume(queue='query_queue', on_message_callback=process_query)
print("Worker is waiting for messages in query_queue. To exit, press CTRL+C")
channel.start_consuming()



