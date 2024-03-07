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

def analyze_abusive_language(db, Tweets, Abusivewords):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    # Initialize dictionaries to store abusive word counts per language
    abusive_word_counts = {lang: {} for lang in languages}

    for language in languages:
        abusive_words = load_abusive_words(language)
        # Assuming Tweets has 'tweet' and 'language' columns
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language).limit(1000).all()
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                for word in tweet.tweet.split():
                    if word in abusive_words:
                        abusive_word_counts[language][word] = abusive_word_counts[language].get(word, 0) + 1

    for language, word_counts in abusive_word_counts.items():
        for word, count in word_counts.items():
            # Check if the word already exists in the database
            abusive_word = Abusivewords.query.filter_by(language=language, words=word).first()
            if abusive_word:
                # Update the frequency if the word already exists
                abusive_word.frequency += count
            else:
                # Create a new entry for the word if it doesn't exist
                new_abusive_word = Abusivewords(language=language, words=word, frequency=count)
                db.session.add(new_abusive_word)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Abusive words counts updated successfully'})


def load_sentiment_words(language, Categ):
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\post_negat_words\\"
    path = os.path.join(basedir, f"{language}{Categ}.csv")
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]
    
def analyze_sentiments_in_languages(db, Tweets, Sentimentwords):
    languages = [
        "ar", "en", "iw", "hi", "ms", "fa", "ur"
    ]

    for language in languages:
        positive_words = load_sentiment_words(language, "_positive")
        negative_words = load_sentiment_words(language, "_negative")
        tweets = db.session.query(Tweets.tweet).filter(Tweets.language == language).limit(1000).all()
        
        # Initialize counts
        positive_count = 0
        negative_count = 0
        
        for tweet in tweets:
            if tweet.tweet is not None and isinstance(tweet.tweet, str):
                for word in tweet.tweet.split():
                    if word in positive_words:
                        positive_count += 1
                    elif word in negative_words:
                        negative_count += 1

        # Update database
        sentiment_data = Sentimentwords(language=language, positive_frequency=positive_count, negative_frequency=negative_count)
        db.session.add(sentiment_data)
        db.session.commit()

    return jsonify({'message': 'Sentiment counts updated successfully'})

    
def analyze_influence_in_languages(db, ProfileData, Influenceanalysis):
    weight_followers = 0.7
    weight_tweets = 0.3
    weight_following = 0.6

    # Query the database and calculate the Adjusted Weighted Score
    data = ProfileData.query.limit(100).all()
    max_score = 0
    influence_data = []
    for user in data:
        try:
            followers = int(user.followers)
            tweets = int(user.num_posts)
            following = int(user.following)
            score = (followers * weight_followers) + (tweets * weight_tweets) - (following * weight_following)
            if score >= 0:  # Ensure score is non-negative
                max_score = max(max_score, score)
                influence_data.append({'username': user.username, 'score': score})
        except ValueError:
            continue

    # Calculate the standardized score as a percentage
    for user_data in influence_data:
        user_data['standardized_score'] = (user_data['score'] / max_score) * 100 if max_score > 0 else 0

    # Save only non-negative scores to the database
    for user_data in influence_data:
        standardized_score = Influenceanalysis(username=user_data['username'], score=user_data['score'], standardized_score=user_data['standardized_score'])
        db.session.add(standardized_score)

    db.session.commit()

    return jsonify({'message': 'Influence analysis completed successfully'})
