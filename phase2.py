import pymongo
from pymongo import MongoClient
import pprint

port_no = input("Please enter your port number: ")
client = MongoClient("mongodb://localhost:" + port_no)
db = client["291db"]
tweets = db["tweets"]

# Create text index on the "content" field with case-insensitivity
tweets.create_index([("content", "text")], default_language='english', textIndexVersion=3)

def search_tweets():
    exit_function  = False
    while exit_function == False:
        user_input = input("Enter keywords to search for tweets (separate by commas if they are multiple): ")
        print()
        keywords = user_input.split()

        # Use the $text operator for text search
        query = {"$text": {"$search": ' '.join(keywords)}}

        # Use the projection to control the fields returned
        projection = {"id": 1,"date": 1, "user.username": 1, "content": 1, "score": {"$meta": "textScore"},"url": 1,
        "renderedContent": 1, "id": 1, "outlinks": 1, "tcooutlinks": 1, "replyCount": 1, "retweetCount": 1, "likeCount": 1,
        "quoteCount": 1, "conversationId": 1, "lang": 1, "source": 1, "sourceUrl": 1, "sourceLabel": 1, "media": 1, "retweetedTweet": 1,
        "quotedTweet": 1, "mentionedUsers": 1}

        # Sort the results by textScore
        results = tweets.find(query, projection).sort([("score", {"$meta": "textScore"})])

        listed_results = list(results)
        current_tweet_no = 1
        for result in listed_results:
            result["tweet_no"] = current_tweet_no
            current_tweet_no += 1
            
        if len(listed_results) == 0:
            print("No results")
        else:
            for result in listed_results:
                username_value = result.get("user", {}).get("username", "N/A")
                print(f'tweet no: {result["tweet_no"]} | id: {result["id"]} | date: {result["date"]} | username: {username_value} | content: {result["content"]}')
                print()

        while True:
            user_input = input("Options: \n1 - Show more information on a tweet \n2 - Search for another tweet \n3 - Go back \nInput: ")
            print()
            if user_input == "1":
                target_input = input("Please enter one of the tweet numbers displayed: ")
                while not any(int(target_input) == result['tweet_no'] for result in listed_results):
                    target_input = input("Invalid. No tweet has that tweet number. Please enter a valid option: ")
                    print()

                for result in listed_results:
                    if(result["tweet_no"] == int(target_input)):
                        target_result =  result
                        break
                username_value = target_result.get("user", {}).get("username", "N/A")
                print(f'url: {target_result["url"]} | date: {target_result["date"]} | content: {target_result["content"]} | rendered content: {target_result["renderedContent"]}')
                print(f'username: {username_value} | outlinks: {target_result["outlinks"]} | tcooutlinks: {target_result["tcooutlinks"]} | ')
                print(f'replyCount: {target_result["replyCount"]} | retweetCount: {target_result["retweetCount"]} | likeCount: {target_result["likeCount"]}')
                print(f'quoteCount: {target_result["quoteCount"]} | conversationId: {target_result["conversationId"]} | lang: {target_result["lang"]} | source: {target_result["source"]} | sourceUrl: {target_result["sourceUrl"]} | sourceLabel: {target_result["sourceLabel"]}')
                print()


            elif user_input == "2":
                break
            elif user_input == "3":
                exit_function = True
                break
        
def search_users():
    pass

def main():
    end_program = False
    while not end_program:
        user_input = input("Please select an option: \n1 - Search for tweets \n6 - Exit the program \ninput: ")
        if user_input == "1":
            search_tweets()
        elif user_input == "2":
            search_users()
        elif user_input == "6":
            end_program = True

main()
