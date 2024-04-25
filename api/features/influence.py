from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv


def analyze_influence_in_languages(db, ProfileData, Tweets, InfluenceAnalysis):
    try:
        # Fetch data from ProfileData and Tweets tables
        users = db.session.query(ProfileData.username, ProfileData.followers, ProfileData.location)\
            .outerjoin(Tweets, ProfileData.username == Tweets.username)\
            .limit(1000).all()

        # Process each user and store data in InfluenceAnalysis table
        for user in users:
            username = user.username
            followers = user.followers if user.followers else 0  # Set followers to 0 if it's None
            location = user.location

            # Check if the user entry already exists in InfluenceAnalysis table
            existing_user = InfluenceAnalysis.query.filter_by(username=username).first()

            # If user entry does not exist, add it to InfluenceAnalysis table
            if not existing_user:
                # Initialize sets to store unique languages, regions, and hashtags for each user
                languages = set()
                regions = set()
                hashtags = set()

                # Fetch languages, regions, and hashtags used by the user from Tweets table
                tweets = Tweets.query.filter_by(username=username).all()
                for tweet in tweets:
                    languages.add(tweet.language)
                    regions.add(tweet.country)
                    hashtags.update(tweet.trend.split(','))

                # Create and store data in InfluenceAnalysis table
                analysis_data = InfluenceAnalysis(
                    username=username,
                    followers=followers,
                    location=location,
                    languages=','.join(list(languages)),
                    regions=','.join(list(regions)),
                    hashtags=','.join(list(hashtags))
                )
                db.session.add(analysis_data)

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Influence analysis data stored successfully'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback changes if an error occurs
        return jsonify({'error': str(e)}), 500
