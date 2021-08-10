import random
import spacy
from spacy.matcher import Matcher
import syllapy
import random
import pandas as pd
import numpy as np
import nltk
import time
import os
import tweepy

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

import nltk
from nltk.corpus import stopwords

from helper import read_params, authenticate, get_scores

# !python3 -m spacy download en_core_web_md

nltk.download('punkt')
nltk.download('words')
nltk.download('stopwords')

nlp = spacy.load("en_core_web_md")

def generate_haiku(movie_name, movie_metadata, plot_file):
    '''
    Function to generate haikus

    Input :
    movie_name - Movie name input from either twitter or command line1
    movie_metadata - metadata file containing the wikipedia id of all MovieSummaries
    plot_file - Text file with the movie plots

    Output:
    haiku - Generated haiku either in the command prompt or as a tweet
    '''
    matcher2 = Matcher(nlp.vocab)
    matcher3 = Matcher(nlp.vocab)
    matcher4 = Matcher(nlp.vocab)
    matcher5 = Matcher(nlp.vocab)
    matcher6 = Matcher(nlp.vocab)

    #First word noun, second word adverb, and third word a verb gerund
    pattern = [{'POS':  {"IN": ["NOUN"]} },
            {'POS':  {"IN": ["ADV"]} },
            {'TAG':  {"IN": ["VBG"]} }]
    matcher2.add("1", [pattern])

    #Pattern starting and ending with either a noun or a verb with anything except space and punctuation in between
    pattern = [{'POS': {"IN" : ["NOUN", "VERB"]}},
            {'IS_ASCII': True, 'IS_PUNCT': False, 'IS_SPACE': False},
            {'POS': {"IN" : ["NOUN", "VERB"]}}]
    matcher3.add("2", [pattern])

    #Pattern starting with an adjective and ending with a noun
    pattern = [{'POS': 'ADJ', 'IS_PUNCT': False},
            {'IS_ASCII': True, 'IS_PUNCT': False, 'IS_SPACE': False},
            {'POS': 'NOUN'}]
    matcher4.add("3", [pattern])

    pattern = [{'POS': {"IN": ['NOUN','ADJ']}, 'IS_PUNCT': False},
            {'IS_ASCII': True, 'IS_PUNCT': False, 'IS_SPACE': False},
            {'TAG': {"IN" : ["VBN", "VBD"]}}]
    matcher5.add("4", [pattern])

    pattern = [{'POS':  {"IN": ["NOUN", "ADJ", "ADV"]} },
            {'IS_ASCII': True, 'IS_PUNCT': False, 'IS_SPACE': False},
            {'IS_ASCII': True, 'IS_PUNCT': False, 'IS_SPACE': False},
            {'POS':  {"IN": ["NOUN","VERB"]} }]
    matcher6.add("5", [pattern])


    try:
        plot  = plot_file.loc[movie_metadata[movie_metadata[2] == (movie_name).lower()][0].values[0],1]
    except Exception as e:
        print("Movie doesn't exist")
        print()
        plot = "A plot device is a means of advancing the plot in a story. It is often used to motivate characters, create urgency, or resolve a difficulty. This can be contrasted with moving a story forward with dramatic technique; that is, by making things happen because characters take action for well-developed reasons. An example of a plot device would be when the cavalry shows up at the last moment and saves the day in a battle. In contrast, an adversarial character who has been struggling with himself and saves the day due to a change of heart would be considered dramatic technique."

    doc = nlp(plot)
    matches2 = matcher2(doc)
    matches3 = matcher3(doc)
    matches4 = matcher4(doc)
    matches5 = matcher5(doc)
    matches6 = matcher6(doc)

    five_syllable = [] # 5 syllable list
    seven_syllable = [] # 7 syllable list
    for match_id, start, end in matches2 + matches3 + matches4 + matches5 + matches6:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]

        syl_count = 0
        for token in span:
            syl_count += syllapy.count(token.text)
        if syl_count == 5:
            if span.text not in five_syllable:
                five_syllable.append(span.text)
        if syl_count == 7:
            if span.text not in seven_syllable:
                seven_syllable.append(span.text)

    # Defining count vectorizer to count the occurances of words in a document
    vectorizer = CountVectorizer()
    filtered_words = [word for word in nltk.word_tokenize(plot) if word not in stopwords.words('english')]
    transformed_data = vectorizer.fit_transform(filtered_words)

    tf_dict = dict(zip(vectorizer.get_feature_names(), np.ravel(transformed_data.sum(axis=0))))

    five_syllable = list(set(five_syllable))
    five_syllable = [g.lower() for g in five_syllable]
    seven_syllable = list(set(seven_syllable))
    seven_syllable = [g.lower() for g in seven_syllable]

    #Call the scorer function
    five_syllable_scores = get_scores(five_syllable,tf_dict)
    seven_syllable_scores = get_scores(seven_syllable,tf_dict)

    #Get the line with the maximum score fro both 5 syllable and 7 syllable list
    line1 = five_syllable[np.argmax(five_syllable_scores)]
    line2 = seven_syllable[np.argmax(seven_syllable_scores)]
    arg_max = np.argmax(five_syllable_scores)
    five_syllable_scores.pop(arg_max)
    five_syllable.pop(arg_max)

    #Get the most similar line to line1 as line3
    doc1 = nlp(line1)
    str(doc1).split(' ')
    sim_dict = {}
    for i in range(len(five_syllable)):
        doc2 = nlp(five_syllable[i])
    sim_dict[doc2] = doc1.similarity(doc2)
    line3 = str(max(sim_dict, key=sim_dict.get))

    haiku = line1+'\n'+line2+'\n'+line3
    return haiku

def main():
    base_path = "MovieSummaries/"
    txtpath = base_path+"plot_summaries.txt"
    plot_file = pd.read_table(txtpath, header=None, index_col=0)
    movie_metadata = pd.read_csv(base_path+'movie.metadata.tsv', sep='\t', header = None)
    #Removing spaces and converting all movies to lowercase
    movie_metadata[2] = movie_metadata[2].str.replace(' ','')
    movie_metadata[2] = movie_metadata[2].str.lower()
    inp_var = input("Do you want to get input from twitter or from command line? Type T for twitter and C for commandline (T/C) : ")

    if inp_var.lower()=='t':
        print("Tweet @MovieSenryuBot to get your outputs")
        print()
        api = authenticate()
        while(True):
          mentions = api.mentions_timeline(count=1)

          for mention in mentions:
              print(mention.text)
              print(mention.user.screen_name)
              tweet_id = mention.id
              user_name = mention.user.screen_name
              movie_to_search = str.lower(mention.text[16:]).lstrip()
              movie_to_search = movie_to_search.replace(' ','')
              haiku = generate_haiku(movie_to_search, movie_metadata, plot_file)
              print(movie_to_search)
              tweet_ = '@'+user_name+'\n'+haiku+'\n'+'#'+movie_to_search.replace(' ','')

              try:
                api.update_status(tweet_,tweet_id)
              except Exception as e:
                print(e)
                pass
              time.sleep(10)
    else:
        movie_name = input("Enter your movie :")
        movie_name = movie_name.replace(' ','')
        movie_name = str.lower(movie_name)
        haiku = generate_haiku(movie_name, movie_metadata, plot_file)
        print(haiku)

if __name__ == '__main__':
    main()
