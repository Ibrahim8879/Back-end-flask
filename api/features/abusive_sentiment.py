from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv

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

def analyze_abusive_language(db, Tweets, Abusivewords, Date):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    # Initialize dictionary to store the count of abusive tweets per language
    abusive_tweet_counts = {lang: {'count': 0, 'tweets': []} for lang in languages}

    for language in languages:
        abusive_words = load_abusive_words(language)
        # Assuming Tweets has 'tweet' and 'language' columns
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language, Tweets.date == Date).all()
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                # Check if any abusive word is present in the tweet
                if any(word in tweet.tweet.split() for word in abusive_words):
                    abusive_tweet_counts[language]['count'] += 1
                    #abusive_tweet_counts[language]['tweets'].append(tweet.tweet)

    for language, info in abusive_tweet_counts.items():
            new_abusive_language = Abusivewords(date = Date, language=language, frequency=info['count'])
            db.session.add(new_abusive_language)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': abusive_tweet_counts})



def load_sentiment_words(language, Categ):
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\post_negat_words\\"
    path = os.path.join(basedir, f"{language}{Categ}.csv")
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]
    
def analyze_sentiments_in_languages(db, Tweets, Sentimentwords, Date):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    for language in languages:
        positive_words = load_sentiment_words(language, "_positive")
        negative_words = load_sentiment_words(language, "_negative")
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language, Tweets.date == Date).all()
        
        # Initialize counts
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                positive_score = 0
                negative_score = 0
                for word in tweet.tweet.split():
                    if word in positive_words:
                        positive_score += 1
                    elif word in negative_words:
                        negative_score += 1
                
                # Determine sentiment
                if positive_score > negative_score:
                    positive_count += 1
                elif negative_score > positive_score:
                    negative_count += 1
                else:
                    neutral_count += 1
           
        # Update database
        sentiment_data = Sentimentwords(date=Date ,language=language, positive_frequency=positive_count,
                                negative_frequency=negative_count, neutral_frequency=neutral_count)
        db.session.add(sentiment_data)
        db.session.commit()

    return jsonify({'message': 'Sentiment counts updated successfully'})

def count_words_in_csv(db, Abusivewords_dictcount):
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\abusive\\"
    abusive_folder_path = basedir
    for filename in os.listdir(abusive_folder_path):
        if filename.endswith('.csv'):
            language_tag = os.path.splitext(filename)[0]
            word_count = 0
            with open(os.path.join(abusive_folder_path, filename), 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    word_count += len(row)
            # Check if the language tag already exists in the database
            language_count = Abusivewords_dictcount.query.filter_by(language_tag=language_tag).first()
            if language_count:
                language_count.word_count = word_count
            else:
                new_language_count = Abusivewords_dictcount(language_tag=language_tag, word_count=word_count)
                db.session.add(new_language_count)
    db.session.commit()