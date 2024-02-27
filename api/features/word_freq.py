from collections import Counter
from flask import jsonify
import nltk
import os
import csv

def analyze_word_frequency(db, Tweets):
    
    # Download the NLTK stopwords corpus
    nltk.download('stopwords')

    # Calculate word frequency for all trends and countries after removing stopwords
    all_trend_word_counts = Counter()
    all_country_word_counts = Counter()

    trend_tweets = db.session.query(Tweets.tweet, Tweets.trend).all()
    country_tweets = db.session.query(Tweets.tweet, Tweets.country).all()

    english_stopwords = set(nltk.corpus.stopwords.words('english'))
    arabic_stopwords = set(nltk.corpus.stopwords.words('arabic'))

    for tweet, trend in trend_tweets:
        words = [word.lower() for word in tweet.split() if word.lower() not in english_stopwords]
        all_trend_word_counts += Counter(words)

    for tweet, country in country_tweets:
        lang = country.lower()
        if lang == 'en':
            stopwords = english_stopwords
        elif lang == 'ar':
            stopwords = arabic_stopwords
        else:
            stopwords = set()  # Use empty set for other languages
        words = [word.lower() for word in tweet.split() if word.lower() not in stopwords]
        all_country_word_counts += Counter(words)

    return jsonify({'all_trend_word_counts': all_trend_word_counts, 'all_country_word_counts': all_country_word_counts})


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
    print(path)
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
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language).all()
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                for word in tweet.tweet.split():
                    if word in abusive_words:
                        abusive_word_counts[language][word] = abusive_word_counts[language].get(word, 0) + 1

    return jsonify({'abusive_word_counts': abusive_word_counts})