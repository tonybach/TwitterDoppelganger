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
        tweet_dict, description_dict, location_dict = get_info_of_self_and_friends(screen_name)
        similarityScores = findDoppelganger(screen_name, 0.7, 0.3)
        similarityScoresSorted = sorted(similarityScores.iteritems(),key=lambda (k,v): v,reverse=True)
        print(similarityScoresSorted)

    print(similarityScoresSorted)
    end = time.time()
    print(end-start)
    # print(tweet_dict, description_dict, location_dict)    


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

from stop_words import get_stop_words
from scipy import spatial
from sklearn.feature_extraction.text import TfidfVectorizer

stop_word_list = get_stop_words('en')

def get_profile_corpus(my_user_name, info_type):
    corpus = []
    if (info_type == "description"):
        info_dict = description_dict
    else:
        info_dict = location_dict
    corpus.append(info_dict[my_user_name])
    for user in info_dict:
        if user != my_user_name:
            corpus.append(info_dict[user])
    return corpus

def get_tweet_corpus(my_user_name, just_hash_tags):
    corpus = []
    my_content = ""
    
    # need to have current user content as the first in the document array/corpus
    # this would make it easier to calculate cosine similarity between
    # tf-idf vectors later
    for tweet in tweet_dict[my_user_name]:
        if (just_hash_tags):
            hashTags = tweet['entities']['hashtags']
            if (len(hashTags) != 0):
                for hashTag in hashTags:
                    my_content += (hashTag['text'] + " ")
        else:
            my_content += (tweet['text'] + " ")

    corpus.append(my_content)
    
    # now add friends' content to the corpus
    for user in tweet_dict:
        if user != my_user_name:
            current_user_content = ""
            for tweet in tweet_dict[user]:
                if (just_hash_tags):
                    hashTags = tweet['entities']['hashtags']
                    if (len(hashTags) != 0):
                        for hashTag in hashTags:
                            current_user_content += (hashTag['text'] + " ")
                else:
                    current_user_content += (tweet['text'] + " ")
            corpus.append(current_user_content)

    return corpus

def get_cosine_similarities(corpus, my_user_name):
    # transform the documents into tf-idf vectors, then compute the cosine similarity between them
    # method taken from here: http://stackoverflow.com/questions/8897593/similarity-between-two-text-documents
    tfidf = TfidfVectorizer(stop_words = stop_word_list).fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T
    cosine_similarities_list = pairwise_similarity.A[0]
    cosine_similarities_dict = defaultdict(list)
    index = 1
    for user in tweet_dict:
        if user != my_user_name:
            cosine_similarities_dict[user] = cosine_similarities_list[index]
            index += 1
    return cosine_similarities_dict

def get_all_cosine_similarities(user_name, contentWeight, profileWeight):
    all_cosine_similarities_dict = defaultdict(float)
    
    tweet_corpus = get_tweet_corpus(user_name, False)
    content_cosine_similarities_dict = get_cosine_similarities(tweet_corpus, user_name)

    description_corpus = get_profile_corpus(user_name, "description")
    description_cosine_similarities_dict = get_cosine_similarities(description_corpus, user_name)

    location_corpus = get_profile_corpus(user_name, "location")
    location_cosine_similarities_dict = get_cosine_similarities(location_corpus, user_name)
    
#     yourMentions = find_who_you_mentioned_in_your_tweets(user_name)
#     whoMentionedYou = find_who_mentioned_you(200) #TO DO
#     fDict = buildVectorsForWhoMentionedYouCorrectly(yourMentions)
#     fDict = cleanVectorDictionary(fDict)
#     md = mentionSimilarityBetter(fDict)

    for user in content_cosine_similarities_dict:
        content_score = float(content_cosine_similarities_dict[user])
        description_score = float(description_cosine_similarities_dict[user])
        location_score = float(location_cosine_similarities_dict[user])
        # have to check because number users in mention list is much smaller
#         if user in md:
#             mention_score = float(md[user])
#         else:
#             mention_score = 0
        profile_score = description_score * 0.5 + location_score * 0.5
        # add retweet score here if necessary
#         network_score = mention_score
        
#         all_score = content_score * contentWeight + profile_score * profileWeight + network_score * networkWeight
        all_score = content_score * contentWeight + profile_score * profileWeight

        all_cosine_similarities_dict[user] = all_score
    return all_cosine_similarities_dict

def findDoppelganger(username, x, y):
    all_cosine = get_all_cosine_similarities(username, x, y)
    return all_cosine

