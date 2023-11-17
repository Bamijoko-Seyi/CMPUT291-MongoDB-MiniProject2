import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient

def insert_batch(batch, collection):
    collection.insert_many(batch)

def main():
    parser = argparse.ArgumentParser(description="Load json script")
    parser.add_argument("--json", help="JSON file to be read for the program", required=True)
    parser.add_argument("--port", help="Port for the program", required=True)
    args = parser.parse_args()

    with open(args.json, 'r') as json_file:
        json_data = json.load(json_file)

    client = MongoClient("mongodb://localhost:"+ args.port)
    db = client["291db"]

    if "tweets" in db.list_collection_names():
        db["tweets"].drop()

    tweets = db["tweets"]

    # Set your desired batch size
    batch_size = 10000
    num_insertion_workers = 20

    # Break the data into batches
    batches = [json_data[i:i + batch_size] for i in range(0, len(json_data), batch_size)]

    # Use ThreadPoolExecutor for parallel insertion
    with ThreadPoolExecutor(max_workers=num_insertion_workers) as executor:
        futures = [executor.submit(insert_batch, batch, tweets) for batch in batches]

    # Wait for all threads to complete
    for future in futures:
        future.result()

if __name__ == "__main__":
    main()
