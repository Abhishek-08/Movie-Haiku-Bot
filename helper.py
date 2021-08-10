import json
import nltk
import tweepy

def read_params():
    '''
    Helper function to read param.json file

    Output :
    params : params dictionary
    '''
    with open("auth_params.json") as f:
        params = json.loads(f.read())
    return params

def get_scores(g_list, tf_dict):
    ss = []
    for j in range(len(g_list)):
        score = []
        for i in nltk.word_tokenize(g_list[j]):
            if i in tf_dict.keys():
                score.append(tf_dict[i])
            else:
                score.append(0)
        ss.append(sum(score))
    return ss

def authenticate():
    '''
    Function to authenticate by reading the json filename
    '''
    params = read_params()
    APIKEY = params["APIKEY"]
    APISecretKey = params["APISecretKey"]
    AccessToken = params["AccessToken"]
    AccessTokenSecret = params["AccessTokenSecret"]
    auth = tweepy.OAuthHandler(APIKEY, APISecretKey)
    auth.set_access_token(AccessToken, AccessTokenSecret)

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
    api = tweepy.API(auth, wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)
    return api
