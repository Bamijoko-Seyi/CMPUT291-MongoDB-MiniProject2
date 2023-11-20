import pymongo
from pymongo import MongoClient
import pprint

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
    exit_function = False
    while not exit_function:
        user_input = input("Enter keywords to search for tweets (separate by commas if they are multiple): ")
        print()
        keywords = user_input.split()

        # Use the $text operator for text search
        query = {"content": {"$regex": ' '.join(keywords), "$options": "i"}}

        listed_results = list(tweets.find(query))
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
                    target_input = input("Invalid. No tweet has that tweet number. Please enter a valid number: ")
                    print()

                for result in listed_results:
                    if result["tweet_no"] == int(target_input):
                        target_result = result
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

def search_users(tweets):
    exit_function = False
    while exit_function == False:
        user_input = input("Enter a keyword to search for : ")
        print()

        username_query = {"user.username": {"$regex": user_input, "$options": "i"}}
        username_results = list(tweets.find(username_query))

        location_query = {"user.location": {"$regex": user_input, "$options": "i"}}
        location_results = list(tweets.find(location_query))

        merged_results = username_results + [location for location in location_results if "user" in location and "id" in location["user"] and location["user"]["id"] not in [user["user"]["id"] for user in username_results]]

        current_tweet_no = 1
        for result in merged_results:
            result["user_no"] = current_tweet_no
            current_tweet_no += 1
        if len(merged_results) == 0:
            print("No results")
        else:
            for result in merged_results:
                username_value = result.get("user", {}).get("username", "N/A")
                displayname_value = result.get("user", {}).get("displayname", "N/A")
                location_value = result.get("user", {}).get("location", "N/A")
                print(f'user no: {result["user_no"]} | username: {username_value} | displayname: {displayname_value} | location: {location_value}')

        while True:
            user_input = input("Options: \n1 - Show more information on a user \n2 - Search for another user \n3 - Go back \nInput: ")
            print()
            if user_input == "1":
                target_input = input("Please enter one of the user numbers displayed: ")
                while not any(int(target_input) == result['user_no'] for result in merged_results):
                    target_input = input("Invalid. No user has that user number. Please enter a valid number: ")
                    print()

                for result in merged_results:
                    if result["user_no"] == int(target_input):
                        target_result = result
                        break

                #Will find a more tidy solution later
                username_value = target_result.get("user", {}).get("username", "N/A")
                displayname_value = target_result.get("user", {}).get("displayname", "N/A")
                id_value = target_result.get("user", {}).get("id", "N/A")
                description_value = target_result.get("user", {}).get("description", "N/A")
                created_value = target_result.get("user", {}).get("created", "N/A")
                followers_count_value = target_result.get("user", {}).get("followersCount", "N/A")
                friends_count_value = target_result.get("user", {}).get("friendsCount", "N/A")
                statuses_count_value = target_result.get("user", {}).get("statusesCount", "N/A")
                favourites_count_value = target_result.get("user", {}).get("favouritesCount", "N/A")
                listed_count_value = target_result.get("user", {}).get("listedCount", "N/A")
                media_count_value = target_result.get("user", {}).get("mediaCount", "N/A")
                location_value = target_result.get("user", {}).get("location", "N/A")
                protected_value = target_result.get("user", {}).get("protected", "N/A")
                profile_image_url_value = target_result.get("user", {}).get("profileImageUrl", "N/A")
                profile_banner_url_value = target_result.get("user", {}).get("profileBannerUrl", "N/A")
                url_value = target_result.get("user", {}).get("url", "N/A")

                print(f'username: {username_value} | displayname: {displayname_value} | id: {id_value} | description: {description_value}')
                print(f'created: {created_value} | followersCount: {followers_count_value} | friendsCount: {friends_count_value}')
                print(f'statusesCount: {statuses_count_value} | favouritesCount: {favourites_count_value} | listedCount: {listed_count_value}')
                print(f'mediaCount: {media_count_value} | location: {location_value} | protected: {protected_value}')
                print(f'profileImageUrl: {profile_image_url_value} | profileBannerUrl: {profile_banner_url_value} | url: {url_value}')

            elif user_input == "2":
                break
            elif user_input == "3":
                exit_function = True
                break

def main():
    tweets = connect_to_mongodb()

    if tweets != None:
        end_program = False
        while not end_program:
            user_input = input("Please select an option: \n1 - Search for tweets \n2 - Search for users \n6 - Exit the program \ninput: ")
            if user_input == "1":
                search_tweets(tweets)
            elif user_input == "2":
                search_users(tweets)
            elif user_input == "6":
                end_program = True
    else:
        print("Exiting program due to connection error.")

main()
