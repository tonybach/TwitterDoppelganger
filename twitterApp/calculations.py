import twitter
import json
from collections import defaultdict
from collections import OrderedDict
import time
import pprint

t = None
tweet_dict = None
description_dict = None
location_dict = None

def find_similarities(consumer_key, consumer_secret, access_token, access_token_secret, screen_name):
    global tweet_dict, description_dict, location_dict, t

    auth = twitter.oauth.OAuth(access_token, access_token_secret, consumer_key, consumer_secret)
    t = twitter.Twitter(auth=auth)
    pp = pprint.PrettyPrinter(indent=2)

    start = time.time()
    if (tweet_dict == None):
        # tweet_dict, description_dict, location_dict = get_info_of_self_and_friends(screen_name)
        print('test')
    end = time.time()
    print(end-start)
    print(tweet_dict, description_dict, location_dict)    


def get_info_of_self_and_friends(my_user_name):
    tweet_dict = defaultdict(list)
    description_dict = defaultdict(str)
    location_dict = defaultdict(str)
    
    # getting user's tweets, description and location
    tweet_dict[my_user_name] = t.statuses.user_timeline(screen_name=my_user_name, count = 200)
    user_info = t.users.show(screen_name=my_user_name)
    description_dict[my_user_name] = user_info['description']
    location_dict[my_user_name] = user_info['location']
    
    # number of calls we have left to get a user's tweets. Need to keep track of
    # this so that we don't run into the rate limit error
    numCallsLeft = t.application.rate_limit_status(resources="statuses")['resources']['statuses']['/statuses/user_timeline']['remaining']
    
    # friend list is in reverse chronological order, so we want to get to the bottom of the list
    friends = t.friends.list(screen_name=my_user_name, count = 200)
    while (friends['next_cursor'] != 0):
        friends = t.friends.list(screen_name=my_user_name, cursor = friends['next_cursor'], count = 200)
    
    # go up the list from the bottom, to get the "oldest" friends first
    # need to leave two calls remaining for another method
    while (numCallsLeft >= 2):
        i = len(friends['users']) - 1
        while (i >= 0):
            friend = friends['users'][i]
            friend_name = friend['screen_name']
            if (friend_name not in tweet_dict):
                try:
                    friend_tweets = t.statuses.user_timeline(screen_name=friend_name, count = 200)
                    friend_info = t.users.show(screen_name=friend_name)
                    friend_description = friend_info['description']
                    friend_location = friend_info['location']
                    if (friend_tweets > 20):
                        tweet_dict[friend_name] = friend_tweets
                        description_dict[friend_name] = friend_description
                        location_dict[friend_name] = friend_location
                except twitter.api.TwitterHTTPError:
                    pass
                numCallsLeft -= 1
            i -= 1           
        # this is reached when we still have calls left, but we have already iterated through
        # all the friends of this user
        if (friends['previous_cursor'] == 0):
            break
        friends = t.friends.list(screen_name=my_user_name, cursor = friends['previous_cursor'], count = 200)
        
    return tweet_dict, description_dict, location_dict