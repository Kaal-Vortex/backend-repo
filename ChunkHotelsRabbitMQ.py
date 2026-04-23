import json
import pika


class HotelChunkPublisher:
    def __init__(self, host='localhost', queue_name='hotel_queue', chunk_size=3):
        self.host = host
        self.queue_name = queue_name
        self.chunk_size = chunk_size

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()

        # Durable queue
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def extract_hotels(self, data):
        return data.get("searchResult", {}).get("his", [])

    def chunk_data(self, hotels):
        for i in range(0, len(hotels), self.chunk_size):
            yield hotels[i:i + self.chunk_size]

    # DEBUG FUNCTION (NEW)
    def debug_hotels(self, hotels):
        print("\n================ DEBUG START ================")

        # Total hotels
        print(f"TOTAL HOTELS FOUND: {len(hotels)}")

        # Print first 3 hotels only (avoid overload)
        print("\n--- SAMPLE HOTEL STRUCTURE (First 3) ---")
        for i, hotel in enumerate(hotels[:3]):
            print(f"\nHotel #{i+1}:")
            print(json.dumps(hotel, indent=2))

        # Manual counting check
        print("\n--- VERIFY COUNT ---")
        count = 0
        for _ in hotels:
            count += 1
        print(f"Verified Count: {count}")

        print("================ DEBUG END ================\n")

    def publish_chunk(self, chunk, search_id, index):
        message = {
            "searchId": search_id,
            "chunkIndex": index,
            "hotels": chunk
        }

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )

        print(f"Sent chunk #{index} with {len(chunk)} hotels")

    def process_and_publish(self, data):
        hotels = self.extract_hotels(data)
        search_id = data.get("searchQuery", {}).get("searchId", "")

        # DEBUG CALL
        self.debug_hotels(hotels)

        total_processed = 0

        for index, chunk in enumerate(self.chunk_data(hotels)):
            total_processed += len(chunk)
            print(f"Processing chunk {index}, total processed so far: {total_processed}")

            self.publish_chunk(chunk, search_id, index)

        print(f"\nFINAL TOTAL PROCESSED: {total_processed}")

        self.connection.close()


# Run
if __name__ == "__main__":
    with open("input.json") as f:
        data = json.load(f)

    publisher = HotelChunkPublisher(chunk_size=3)
    publisher.process_and_publish(data)
