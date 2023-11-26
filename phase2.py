import pymongo
from pymongo import MongoClient
import pprint
from datetime import datetime

def connect_to_mongodb():
    try:
        port_no = input("Please enter your port number: ")
        client = MongoClient("mongodb://localhost:" + port_no)
        db = client["291db"]
        tweets = db["tweets"]

        # creates the indexes needed for the functions to work
        tweets.create_index([("user.username", "text"), ("content", "text"), ("location", "text")], name='compound_text_index', default_language='english', textIndexVersion=3)

        return tweets
    except pymongo.errors.ConnectionFailure as error:
        print(f"Error connecting to MongoDB: {error}")
        return None

def search_tweets(tweets):
    while True:
        user_input = input("Enter keywords to search for tweets, or type 'menu' to return: ")
        if user_input.lower() == 'menu':
            return

        keywords = user_input.split()
        query = {"content": {"$regex": ' '.join(keywords), "$options": "i"}}
        listed_results = list(tweets.find(query))

        for index, result in enumerate(listed_results, start=1):
            print(f"Tweet {index}:")
            print(f"  ID: {result['id']}")
            print(f"  Date: {result['date']}")
            print(f"  Content: {result['content']}")
            print(f"  Username: {result.get('user', {}).get('username', 'N/A')}\n")

        if not listed_results:
            print("No results found.")
            continue

        tweet_selection = input("Enter the number of the tweet to see full details, or type 'menu' to return: ")
        if tweet_selection.lower() == 'menu':
            return

        try:
            tweet_number = int(tweet_selection)
            if 0 < tweet_number <= len(listed_results):
                selected_tweet = listed_results[tweet_number - 1]
                pprint.pprint(selected_tweet)
            else:
                print("Invalid tweet number entered.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def search_users(tweets):
    while True:
        user_input = input("Enter a keyword to search for, or type 'menu' to return: ")
        if user_input.lower() == 'menu':
            return

        username_query = {"user.displayname": {"$regex": user_input, "$options": "i"}}
        username_results = list(tweets.find(username_query))

        location_query = {"user.location": {"$regex": user_input, "$options": "i"}}
        location_results = list(tweets.find(location_query))

        merged_results = username_results + [location for location in location_results if "user" in location and "id" in location["user"] and location["user"]["id"] not in [user["user"]["id"] for user in username_results]]

        for index, result in enumerate(merged_results, start=1):
            print(f"User {index}:")
            user = result.get("user", {})
            print(f"  Username: {user.get('username', 'N/A')}")
            print(f"  Display Name: {user.get('displayname', 'N/A')}")
            print(f"  Location: {user.get('location', 'N/A')}\n")

        if not merged_results:
            print("No results found.")
            continue

        user_selection = input("Enter the number of the user to see full details, or type 'menu' to return: ")
        if user_selection.lower() == 'menu':
            return

        try:
            user_number = int(user_selection)
            if 0 < user_number <= len(merged_results):
                selected_user = merged_results[user_number - 1]
                pprint.pprint(selected_user.get("user", {}))
            else:
                print("Invalid user number entered.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def list_top_tweets(tweets):
    while True:
        field_input = input("Enter the field to sort by (retweetCount, likeCount, quoteCount), or type 'menu' to return: ")
        if field_input.lower() == 'menu':
            return

        if field_input not in ['retweetCount', 'likeCount', 'quoteCount']:
            print("Invalid field. Please enter one of 'retweetCount', 'likeCount', 'quoteCount'.")
            continue

        try:
            n = int(input("Enter the number of top tweets to list: "))
        except ValueError:
            print("Invalid number entered.")
            continue

        results = tweets.find().sort(field_input, pymongo.DESCENDING).limit(n)
        tweet_list = list(results)

        for index, tweet in enumerate(tweet_list, start=1):
            print(f"Tweet {index}:")
            print(f"  ID: {tweet['id']}")
            print(f"  Date: {tweet['date']}")
            print(f"  Content: {tweet['content']}")
            print(f"  Username: {tweet['user']['username']}\n")

        tweet_selection = input("Enter the number of the tweet to see full details, or type 'menu' to return: ")
        if tweet_selection.lower() == 'menu':
            return
            
def compose_tweet(tweets):
    content = input("Enter the tweet content: ")
    tweet_doc = {
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),  # Set date to current system date
        "user": {
            "username": "291user"
        }
    }
    result = tweets.insert_one(tweet_doc)
    
    if result.inserted_id:
        print("Tweet successfully composed and inserted into the database.")
    else:
        print("Failed to compose and insert the tweet.")
        
def main():
    tweets = connect_to_mongodb()

    if tweets is not None:
        end_program = False
        while not end_program:
            user_input = input("Please select an option: \n1 - Search for tweets \n2 - Search for users \n3 - List top tweets \n4 - List top users \n5 - Compose a tweet \n6 - Exit the program \nInput: ")
            if user_input == "1":
                search_tweets(tweets)
            elif user_input == "2":
                search_users(tweets)
            elif user_input == "3":
                list_top_tweets(tweets)
            elif user_input == "4":
                list_top_users(tweets)
            elif user_input == "5":
                compose_tweet(tweets)
            elif user_input == "6":
                end_program = True
            else:
                print("Invalid option. Please try again.")
    else:
        print("Exiting program due to connection error.")

if __name__ == "__main__":
    main()
