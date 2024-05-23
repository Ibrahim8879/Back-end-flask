from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re

def count_unique_words(tweet):
    words = re.findall(r'\b\w+\b', tweet.lower())
    unique_words = set(words)     # Convert the list of words to a set to get unique words
    return len(unique_words)

def analyze_lexical_analysis_loc(db, Tweets, LexicalByLocation):
    # Query the database to fetch tweets and their languages
    tweets = db.session.query(Tweets.tweet, Tweets.country).all()

    # Convert the query result to a DataFrame
    df = pd.DataFrame(tweets, columns=['tweet', 'country'])

    # Compute the count of unique words in each tweet
    df['uniqueWordsCount'] = df['tweet'].apply(count_unique_words)

    # Compute the diversity for each tweet
    diversity = [uniqueWords / len(singleTweet) if len(singleTweet)>0 else 0 for singleTweet, uniqueWords in zip(df.tweet, df.uniqueWordsCount)]
    df['diversity'] = diversity
    
    # Group the DataFrame by 'country' and calculate the mean of 'diversity' within each group
    mean_diversity_by_language = df.groupby('country')['diversity'].mean()

    for country, avg_diversity in mean_diversity_by_language.items():
            new_lexical_entry = LexicalByLocation(location=country, diversity=round(avg_diversity*100))
            print(country,round(avg_diversity*100))
            db.session.add(new_lexical_entry)
    db.session.commit()

    return jsonify({'message': 'Lexical Diversity updated successfully'})

