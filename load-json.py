import argparse
import pymongo
from pymongo import MongoClient
from pymongo import TEXT
import os
import time

def main():
    
    ##Gets the location of the json and the port number through the terminal
    parser = argparse.ArgumentParser(description="Load json script")
    parser.add_argument("--json", help="JSON file to be read for the program", required=True)
    parser.add_argument("--port", help="Port for the program", required=True)
    args = parser.parse_args()

    start_time = time.time()

    ##Connects the database using the port number provided
    client = MongoClient('mongodb://localhost:'+ args.port)
    db = client["291db"]

    tweets = db["tweets"]
    tweets.drop()

    ##Inserts the data in batches in to the tweets collection
    os.system('mongoimport --db=291db --collection=tweets --port={} --file={} --batchSize=10000 --numInsertionWorkers=20'.format(args.port,args.json))

    end_time = time.time()

    print("Json file successfully imported!")
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
