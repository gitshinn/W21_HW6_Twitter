#########################################
##### Name: Kristian Shin           #####
##### Uniqname: shinkris            #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests

import secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

# client_key = "MCfKBDq7nL1xBZbUv7ZVm997r"
# client_secret = "CBBHigXd1hjx1r5zUwf1UI61og5QE3T9f5eenGFMgV3tlii7z2"
# access_token = "1376013641472954369-hTpAnuCsvS1GYiGdQlWcFTVvE8ueEI"
# access_token_secret = "exlyiPjJlledEX8HIJiCuhk7gxFaETdQ7ZYXJTbPIMv96"

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    #empty list to append key:value pairs to
    param_strings = []
    #separator needed to construct unique url
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
        param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key



def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    #requesting the twitter API and adding the authorization
    twitter_request = requests.get(baseurl, params=params, auth=oauth)
    json_str = twitter_request.text
    #Making a dictionary object from the json
    twitter_dict = json.loads(json_str)
    return twitter_dict


def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    CACHE_DICT = open_cache()
    params = {'q': hashtag, 'count': count}
    search_item = construct_unique_key(baseurl, params)
    #if the unique_key is in the cached dictionary, return that item from the dictionary
    if search_item in CACHE_DICT:
        print("fetching cached data")
        return CACHE_DICT[search_item]
    #if the unique_key is not in the cached dictionary, get a new result and save it to the cached dictionary
    else:
        print("making new request")
        new_result = make_request(baseurl, params)
        CACHE_DICT[search_item] = new_result
        save_cache(CACHE_DICT)
        return new_result


def find_most_common_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")

    Returns
    -------
    string
        the hashtag that most commonly co-occurs with the hashtag 
        queried in make_request_with_cache()

    '''
    # TODO: Implement function
    occurence_count = {}
    #removing the hashtag
    hashtag_to_ignore = hashtag_to_ignore[1:]
    #loop through hashtags in tweet_data
    for status in tweet_data['statuses']:
        for hashtag in status['entities']['hashtags']:
            #make string comaprisons case-insensitive
            h_txt = hashtag['text'].lower()
            if h_txt != hashtag_to_ignore.lower():
                if h_txt not in occurence_count:
                    occurence_count[h_txt] = 0
                occurence_count[h_txt] += 1
    max_ct = 0
    #Setting a default return
    hashtag_with_max = "none"
    #looping over occurence_count to find the max number of occurences of a hashtag
    #and save it to a variable if it has more counts than the previous record holder
    for hashtag in occurence_count.keys():
        if occurence_count[hashtag] > max_ct:
            max_ct = occurence_count[hashtag]
            hashtag_with_max = hashtag
    return hashtag_with_max


    ''' Hint: In case you're confused about the hashtag_to_ignore 
    parameter, we want to ignore the hashtag we queried because it would 
    definitely be the most occurring hashtag, and we're trying to find 
    the most commonly co-occurring hashtag with the one we queried (so 
    we're essentially looking for the second most commonly occurring 
    hashtags).'''

    

if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()

    CACHE_DICT = open_cache()

    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    hashtag = "#MarchMadness2021"
    count = 100

    tweet_data = make_request_with_cache(baseurl, hashtag, count)
    most_common_cooccurring_hashtag = find_most_common_cooccurring_hashtag(tweet_data, hashtag)
    print("The most commonly cooccurring hashtag with {} is {}.".format(hashtag, most_common_cooccurring_hashtag))

