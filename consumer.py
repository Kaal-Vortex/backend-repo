import pika
import json
import time


def callback(ch, method, properties, body):
    data = json.loads(body)

    print("\nProcessing chunk:")
    print(f"Chunk Index: {data.get('chunkIndex')}")
    print(f"Hotels count: {len(data.get('hotels', []))}")

    # Simulate processing time (important for testing)
    time.sleep(2)

    # ACK only after processing is done
    ch.basic_ack(delivery_tag=method.delivery_tag)

    print(f"Chunk {data.get('chunkIndex')} processed and ACK sent")


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)

channel = connection.channel()

# Durable queue
channel.queue_declare(queue='hotel_queue', durable=True)

#  VERY IMPORTANT: Process ONE message at a time
channel.basic_qos(prefetch_count=1)

channel.basic_consume(
    queue='hotel_queue',
    on_message_callback=callback,
    auto_ack=False  #  MUST BE FALSE
)

print("Waiting for messages (one-by-one)...")
channel.start_consuming()

