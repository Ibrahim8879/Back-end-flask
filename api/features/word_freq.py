from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv

language_mapping = {
    "en": "english", "fa": "persian", "ur": "urdu", "ar": "arabic", 
    "tr": "turkish", "iw": "hebrew","es": "spanish",
    "in": "indonesian", "zh": "chinese", "ne": "nepali", "hi": "hindi", 
    "ru": "russian", "bn": "bengali"
}

def load_custom_stopwords(language_mapping):
    stopwords_list = []
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\stopwords\\"
    
    for code, lang in language_mapping.items():
        path = os.path.join(basedir, f"{lang}")
        with open(path, "r", encoding="utf-8") as file:
            stopwords_list.extend([line.strip() for line in file])
    
    return stopwords_list

def analyze_word_frequency(db, Tweets, WordFrequency):
    stopwords = load_custom_stopwords(language_mapping)

    countries = db.session.query(Tweets.country).all()
    trends = db.session.query(Tweets.trend).all()

    country_word_counts = {}
    
    for country, in countries:
        tweets = db.session.query(Tweets.tweet).filter(Tweets.country == country).limit(100).all()
        tweets_df = pd.DataFrame(tweets, columns=['tweet'])
        tweets_df['words'] = tweets_df['tweet'].str.lower().str.split()
        tweets_df['words'] = tweets_df['words'].apply(lambda x: [word for word in x if word.lower() not in stopwords])
        country_word_counts[country] = Counter([word for sublist in tweets_df['words'] for word in sublist])

    trend_word_counts = {}

    for trend, in trends:
        tweets = db.session.query(Tweets.tweet).filter(Tweets.trend == trend).limit(100).all()
        tweets_df = pd.DataFrame(tweets, columns=['tweet'])
        tweets_df['words'] = tweets_df['tweet'].str.lower().str.split()
        tweets_df['words'] = tweets_df['words'].apply(lambda x: [word for word in x if word.lower() not in stopwords])
        trend_word_counts[trend] = Counter([word for sublist in tweets_df['words'] for word in sublist])

    return jsonify({'country_word_counts': country_word_counts, 'trend_word_counts': trend_word_counts})


def get_all_languages(db, Tweets):
    languages = [
    "en", "de", "fa", "ur", "ar", "ckb", "it", "tr", "und", "ps", "qme", "iw", "ro", "fr", "es", "tl", "qht",
    "et", "fi", "ca", "in", "zh", "ne", "hi", "nl", "te", "ta", "kn", "hu", "ja", "pt", "gu", "qct", "is",
    "dv", "vi", "lv", "ht", "da", "th", "ko", "pl", "mr", "si", "sl", "sv", "no", "sd", "cs", "ru", "lt", "bn",
    "eu", "or", "qam", "qst", "my", "ml"
]
    tweets_by_language = {lang: None for lang in languages}

    for language in languages:
        # Assuming Tweets has columns for 'id', 'tweet', and other attributes
        tweet = db.session.query(Tweets).filter(Tweets.language == language).first()
        if tweet:
            tweets_by_language[language] = {
                'id': tweet.id,
                'tweet': tweet.tweet,
                'country': tweet.country,
                'language': tweet.language,
                # Add other attributes as needed
            }

    return jsonify({'tweets_by_language': tweets_by_language})


def load_abusive_words(language):
    language_mapping = {
        "ar": "arabic",
        "en": "english",
        "iw": "hebrew",
        "hi": "hindi",
        "ms": "malay",
        "fa": "persian",
        "ur": "urdu"
    }
    full_language_name = language_mapping.get(language)
    if not full_language_name:
        raise ValueError(f"Language code '{language}' not supported")
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\abusive\\"
    path = os.path.join(basedir, f"{full_language_name}.csv")
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]

def analyze_abusive_language(db, Tweets):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    # Initialize dictionaries to store abusive word counts per language
    abusive_word_counts = {lang: {} for lang in languages}

    for language in languages:
        abusive_words = load_abusive_words(language)
        # Assuming Tweets has 'tweet' and 'language' columns
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language).limit(100).all()
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                for word in tweet.tweet.split():
                    if word in abusive_words:
                        abusive_word_counts[language][word] = abusive_word_counts[language].get(word, 0) + 1

    return jsonify({'abusive_word_counts': abusive_word_counts})


def load_sentiment_words(language, Categ):
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\post_negat_words\\"
    path = os.path.join(basedir, f"{language}{Categ}.csv")
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]
    
def analyze_sentiments_in_languages(db, Tweets):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    # Initialize dictionaries to store abusive word counts per language
    sentiment_counts = {lang: {"positive": 0, "negative": 0} for lang in languages}

    for language in languages:
        positive_words = load_sentiment_words(language, "_positive")
        negative_words = load_sentiment_words(language, "_negative")
        # Assuming Tweets has 'tweet' and 'language' columns
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language).limit(100).all()
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                for word in tweet.tweet.split():
                    if word in positive_words:
                        sentiment_counts[language]["positive"] += 1
                    elif word in negative_words:
                        sentiment_counts[language]["negative"] += 1

    return jsonify({'sentiment_counts': sentiment_counts})