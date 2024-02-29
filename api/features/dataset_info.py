from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd


def get_db_details(db, ProfileData, Tweets):
    # User Locations
    user_locations_data = []
    for location, in db.session.query(ProfileData.location).distinct().all():
        if location is not None:
            total_users = db.session.query(func.count(ProfileData.id)).filter(ProfileData.location == location).scalar()
            total_followers = db.session.query(func.sum(ProfileData.followers)).filter(ProfileData.location == location).scalar()
            total_tweets = db.session.query(func.sum(ProfileData.num_posts)).filter(ProfileData.location == location).scalar()
            total_verified = db.session.query(func.sum(ProfileData.verified)).filter(ProfileData.location == location).scalar()
            user_locations_data.append({
                'location': location,
                'total_users': total_users,
                'total_followers': total_followers,
                'total_tweets': total_tweets,
                'total_verified': total_verified
            })

    # Trend Regions
    trend_regions_data = []
    for trend, country in db.session.query(Tweets.trend, Tweets.country).distinct().all():
        total_tweets = db.session.query(func.count(Tweets.id)).filter(Tweets.trend == trend, Tweets.country == country).scalar()
        total_languages = db.session.query(func.count(Tweets.language.distinct())).filter(Tweets.trend == trend, Tweets.country == country).scalar()
        trend_regions_data.append({
            'trend': trend,
            'country': country,
            'total_tweets': total_tweets,
            'total_languages': total_languages
        })

    # Tweets Languages
    tweets_languages_data = []
    for language, in db.session.query(Tweets.language).distinct().all():
        total_tweets = db.session.query(func.count(Tweets.id)).filter(Tweets.language == language).scalar()
        total_trends = db.session.query(func.count(Tweets.trend.distinct())).filter(Tweets.language == language).scalar()
        tweets_languages_data.append({
            'language': language,
            'total_tweets': total_tweets,
            'total_trends': total_trends
        })

    return jsonify({
        'user_locations_data': user_locations_data,
        'trend_regions_data': trend_regions_data,
        'tweets_languages_data': tweets_languages_data
    })