import pymongo
from pymongo import MongoClient
import pprint
from datetime import datetime
import re

def connect_to_mongodb():
    try:
        port_no = input("Please enter your port number: ")
        print()
        client = MongoClient("mongodb://localhost:" + port_no)
        db = client["291db"]
        tweets = db["tweets"]

        # creates the indexes needed for the functions to work
        tweets.create_index([("user.username", "text"), ("content", "text"), ("location", "text")], name='compound_text_index', default_language='english', textIndexVersion=3)

        return tweets
    except pymongo.errors.ConnectionFailure as error:
        print(f"Error connecting to MongoDB: {error}\n")
        return None

def search_tweets(tweets):
    while True:
        user_input = input("Enter keywords to search for tweets, or type 'menu' to return: ")
        if user_input.lower() == 'menu':
            return

        keywords = user_input.split()
        query = {"content": {"$regex": ' '.join(keywords), "$options": "i"}}
        listed_results = list(tweets.find(query))

        matched_tweets = []
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'

            for result in listed_results:
                if re.search(pattern, result['content'], flags=re.IGNORECASE):
                    matched_tweets.append(result)

        for index, result in enumerate(listed_results, start=1):
            print(f"Tweet {index}:")
            print(f"  ID: {result.get('id', 'N/A')}")
            print(f"  Date: {result.get('date','N/A')}")
            print(f"  Content: {result.get('content','N/A')}")
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
        print()
        if user_input.lower() == 'menu':
            return

        pattern = r'\b' + re.escape(user_input) + r'\b'
        query = {
            "$or": [
                {"user.displayname": {"$regex": pattern, "$options": "i"}},
                {"user.location": {"$regex": pattern, "$options": "i"}}
            ]
        }
        results = list(tweets.find(query))

        unique_users = set()
        merged_results = []

        for result in results:
            user_id = result.get("user", {}).get("id")
            if user_id and user_id not in unique_users:
                unique_users.add(user_id)
                merged_results.append(result)

        for index, result in enumerate(merged_results, start=1):
            print(f"User {index}:")
            user = result.get("user", {})
            print(f"  Username: {user.get('username', 'N/A')}")
            print(f"  Display Name: {user.get('displayname', 'N/A')}")
            print(f"  Location: {user.get('location', 'N/A')}\n")

        if not merged_results:
            print("No results found.\n")
            continue

        user_selection = input("Enter the number of the user to see full details, or type 'menu' to return: ")
        print()
        if user_selection.lower() == 'menu':
            return

        try:
            user_number = int(user_selection)
            if 0 < user_number <= len(merged_results):
                selected_user = merged_results[user_number - 1]
                pprint.pprint(selected_user.get("user", {}))
            else:
                print("Invalid user number entered.\n")
        except ValueError:
            print("Invalid input. Please enter a number.\n")

def list_top_tweets(tweets):
    while True:
        field_input = input("Enter the field to sort by (retweetCount, likeCount, quoteCount), or type 'menu' to return: ")
        print()
        if field_input.lower() == 'menu':
            return

        if field_input not in ['retweetCount', 'likeCount', 'quoteCount']:
            print("Invalid field. Please enter one of 'retweetCount', 'likeCount', 'quoteCount'.\n")
            continue

        try:
            n = int(input("Enter the number of top tweets to list: "))
            print()
        except ValueError:
            print("Invalid number entered.\n")
            continue

        results = tweets.find().sort(field_input, pymongo.DESCENDING).limit(n)
        tweet_list = list(results)

        if not tweet_list:
            print("No tweets found.")
            continue

        for index, tweet in enumerate(tweet_list, start=1):
            print(f"Tweet {index}:")
            print(f"  ID: {tweet['id']}")
            print(f"  Date: {tweet['date']}")
            print(f"  Content: {tweet['content']}")
            print(f"  Username: {tweet['user']['username']}\n")

        tweet_selection = input("Enter the number of the tweet to see full details, or type 'menu' to return: ")
        print()
        if tweet_selection.lower() == 'menu':
            return

        try:
            tweet_number = int(tweet_selection)
            if 0 < tweet_number <= len(tweet_list):
                selected_tweet = tweet_list[tweet_number - 1]
                pprint.pprint(selected_tweet)
            else:
                print("Invalid tweet number entered.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def list_top_users(tweets):
    n = input("Enter the number of users you would like to list: ")
    print()
    while not n.isdigit():
        n = input("Invalid. Please enter a valid number: ")
        print()

    results = list(tweets.find().sort("user.followersCount", pymongo.DESCENDING).limit(int(n)))
    user_index_to_id_map = {}

    while True:
        for index, result in enumerate(results, start = 1):
            user = result.get("user", {})
            user_id, username, display_name = user.get('id', 'N/A'), user.get('username', 'N/A'), user.get('displayname', 'N/A')
            followers_count = user.get('followersCount', 'N/A')
            user_index_to_id_map[index] = user_id
            print(f"{index}. User ID: {user_id} | Username: {username:20} | Display name: {display_name:20} | Followers Count: {followers_count}")
        print()

        user_input = input("Options:\n1 - Select user\n2 - Go back\n\nInput: ")
        print()
        while user_input not in ["1", "2"]:
            user_input = input("Invalid. Please select from one of the following options:\n1 - Select user\n2 - Go back\n\nInput: ")
            print()

        if user_input == "1":
            while True:
                user_input = input("Select a user by number to see more information: ")
                print()
                while not user_input.isdigit():
                    user_input = input("Invalid selection. Please select one of the numbers displayed above: ")
                    print()
                
                selected_user_id = user_index_to_id_map[int(user_input) - 1]
                
                user_id, user_info = '', ''
                for result in results:
                    user = result.get("user", {})
                    user_id = user.get("id", "N/A")
                    if user_id == selected_user_id:
                        user_info = result
                        break

                if user_info:
                    pprint.pprint(user_info)
                    print()
                else:
                    print("User information not found.\n")
                
                user_input = input("Options:\n1 - Go back\n\nInput: ")
                while user_input != "1":
                    user_input = input("Invalid. Please select one of the following options:\n1 - Go back\n\nInput: ")
                break

        else:
            break
            
def compose_tweet(tweets):
    content = input("Enter the tweet content: ")
    print()
    tweet_doc = {
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),  # Set date to current system date
        "user": {
            "username": "291user"
        }
    }
    result = tweets.insert_one(tweet_doc)
    
    if result.inserted_id:
        print("Tweet successfully composed and inserted into the database.\n")
    else:
        print("Failed to compose and insert the tweet.\n")
        
def main():
    tweets = connect_to_mongodb()

    if tweets is not None:
        end_program = False
        while not end_program:
            user_input = input("Welcome to Fake Twitter 2.0!\n\nOptions:\n1 - Search for tweets\n2 - Search for users\n3 - List top tweets\n4 - List top users\n5 - Compose a tweet\n6 - Exit the program\n\nInput: ")
            print()
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
                print("Invalid option. Please try again.\n")
    else:
        print("Exiting program due to connection error.\n")

if __name__ == "__main__":
    main()
