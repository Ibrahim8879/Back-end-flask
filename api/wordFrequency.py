from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv
import re

language_mapping = {
   "en": "english", "fa": "persian", "ur": "urdu", "ar": "arabic", 
   "tr": "turkish", "iw": "hebrew","es": "spanish",
   "in": "indonesian", "zh": "chinese", "ne": "nepali", "hi": "hindi", 
   "ru": "russian", "bn": "bengali"
}

def load_custom_stopwords(language_mapping):
    stopwords_list = {}
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\stopwords\\"

    for code, lang in language_mapping.items():
        stopwords_list[code] = []
        path = os.path.join(basedir, f"{lang}")
        with open(path, "r", encoding="utf-8") as file:
            stopwords_list[code].extend([line.strip() for line in file])

    return stopwords_list



def clean_text(text):
    # Remove special characters and digits, and convert to lowercase
    if len(text) == 0:
        return text
    
    text_list = list(text)
    
    if (text_list[0] >= chr(0) and text_list[0]<=chr(64)) or (text_list[0]>=chr(91) and text_list[0]<=chr(96)) or (text_list[0] >= chr(123) and text_list[0] <= chr(127)):
        text_list.pop(0)
        text = "".join(text_list)
        text = clean_text(text)
    elif (text_list[-1] >= chr(0) and text_list[-1] <=chr(64)) or (text_list[-1]>=chr(91) and text_list[-1]<=chr(96)) or (text_list[-1] >= chr(123) and text_list[-1] <= chr(127)):
        text_list.pop(-1)
        text = "".join(text_list)
        text = clean_text(text)
        
    return text

def countWordsGroupedByLanguage(grouped_tweets):
    word_frequencies = {}

    stopwords = load_custom_stopwords(language_mapping)
    for index, row in grouped_tweets.iterrows():
        language = row['language']
        tweets_text = row['tweet']
        # Tokenize the tweets into words
        words = tweets_text.split()
        # Count word frequencies
        word_freq = {}
    
        for word in words:
            cleanedWord = clean_text(word)
            if cleanedWord != "" and (language not in language_mapping or cleanedWord not in stopwords[language]):
                word_freq[cleanedWord] = word_freq.get(cleanedWord, 0) + 1
                # word_freq[word] = word_freq.get(word, 0) + 1
        
        word_frequencies[language] = word_freq

    return word_frequencies



def countWordsGroupedByLocation(grouped_tweets):
    word_frequencies = {}

    stopwords = load_custom_stopwords(language_mapping)
    for index, row in grouped_tweets.iterrows():
        country = row['country']
        tweets_text = row['tweet']
        language = row['language']

        # Tokenize the tweets into words 
        words = tweets_text.split()
        # Count word frequencies
        word_freq = {}

        for word in words:
            cleanedWord = clean_text(word)
            if cleanedWord != "" and (language not in language_mapping or cleanedWord not in stopwords[language]):
                word_freq[cleanedWord] = word_freq.get(cleanedWord, 0) + 1
                # word_freq[word] = word_freq.get(word, 0) + 1
        
        word_frequencies[country] = word_freq

    return word_frequencies




#this function is supposed to count the occurance of each word grouped by the language.
def analyze_word_frequency(db, Tweets, WordFrequency):

    tweets = db.session.query(Tweets.tweet, Tweets.language, Tweets.country).limit(100).all()
    # Convert the query result to a DataFrame
    df = pd.DataFrame(tweets, columns=['tweet', 'language', 'country'])
    
#grouped by language.   
    grouped_tweets = df.groupby('language')['tweet'].apply(' '.join).reset_index()
    gt = countWordsGroupedByLanguage(grouped_tweets)
    
#grouped by country.
    # grouped_tweets = df.groupby(['country', 'language'])['tweet'].apply(' '.join).reset_index()
    # gt = countWordsGroupedByLocation(grouped_tweets)
        
    return jsonify(gt)
   
    
#this function is supposed to count the occurance of each word grouped by the language.
def analyze_word_frequency(db, Tweets, WordFrequency):

    stopwords = load_custom_stopwords(language_mapping)
    tweets = db.session.query(Tweets.tweet, Tweets.language, Tweets.country).all()
    # Convert the query result to a DataFrame
    df = pd.DataFrame(tweets, columns=['tweet', 'language', 'country'])
    
    grouped_tweets = df.groupby('country')['tweet'].apply(' '.join).reset_index()
    countbylocation = countWordsGroupedByLocation(grouped_tweets)

    grouped_tweets2 = df.groupby('language')['tweet'].apply(' '.join).reset_index()
    countbylanguage = countWordsGroupedByLanguage(grouped_tweets2)

    # Push the word frequency data into the database
    for country, word_freq in countbylocation.items():
        for word, frequency in word_freq.items():
            word_frequency_entry = WordFrequency(
                country=country,
                country_word=word,
                country_frequency=frequency,
                language='',
                language_word='',
                language_frequency=0
            )
            db.session.add(word_frequency_entry)

    for language, word_freq in countbylanguage.items():
        for word, frequency in word_freq.items():
            word_frequency_entry = WordFrequency(
                country='',
                country_word='',
                country_frequency=0,
                language=language,
                language_word=word,
                language_frequency=frequency
            )
            db.session.add(word_frequency_entry)
        
    db.session.commit()
        
    return jsonify({'message': 'Word frequency data stored successfully'})