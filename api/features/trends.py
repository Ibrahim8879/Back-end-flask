from flask import jsonify
from collections import Counter
from itertools import groupby

def get_trends(db, ProfileData, Tweets):
    # Get trending topics by language
    language_trends = db.session.query(Tweets.trend, Tweets.language).all()
    language_trend_counts = Counter([(trend, language) for trend, language in language_trends])

    # Get trending topics by country
    country_trends = db.session.query(Tweets.trend, Tweets.country).all()
    country_trend_counts = Counter([(trend, country) for trend, country in country_trends])

    # Get trending topics by user location
    user_location_trends = db.session.query(Tweets.trend, ProfileData.location)\
        .join(ProfileData, Tweets.username == ProfileData.username).all()
    user_location_trend_counts = Counter([(trend, location) for trend, location in user_location_trends])

    # Process and format the trend data
    trends_data = {
        'languages': [{'language': language, 'top_trend': trend}
                      for language, trends in groupby(sorted(language_trend_counts.items(), key=lambda x: x[0][1]), key=lambda x: x[0][1]) for trend, _ in sorted(trends, key=lambda x: x[1], reverse=True)[:1]],
        'countries': [{'country': country, 'top_trends': [trend for trend, _ in sorted(trends, key=lambda x: x[1], reverse=True)[:1]]}
                      for country, trends in groupby(sorted(country_trend_counts.items(), key=lambda x: x[0][1]), key=lambda x: x[0][1])],
        'user_locations': [{'location': location, 'top_trend': trend}
                           for location, trends in groupby(sorted(user_location_trend_counts.items(), key=lambda x: x[0][1]), key=lambda x: x[0][1]) for trend, _ in sorted(trends, key=lambda x: x[1], reverse=True)[:1]]
    }

    return jsonify(trends_data)