from flask import jsonify
from collections import Counter
from itertools import groupby
from collections import defaultdict

def get_trends(db, ProfileData, Tweets, Trends):
    # Get trending topics by language
    language_trends = db.session.query(Tweets.trend, Tweets.language).all()
    country_trends = db.session.query(Tweets.trend, Tweets.country).all()
    user_location_trends = db.session.query(Tweets.trend, ProfileData.location)\
        .join(ProfileData, Tweets.username == ProfileData.username).all()
    
    # Initialize dictionaries to store trends for each category
    language_dict = defaultdict(set)
    country_dict = defaultdict(set)
    user_location_dict = defaultdict(set)

    # Group trends by language, country, and user location, and count occurrences
    for trend, language in language_trends:
        language_dict[language].add(trend)

    for trend, country in country_trends:
        country_dict[country].add(trend)

    for trend, user_location in user_location_trends:
        user_location_dict[user_location].add(trend)

    # Convert sets to lists and add count
    def get_trend_count(trend_set, all_trends):
        trend_count = defaultdict(int)
        for trend in trend_set:
            trend_count[trend] = all_trends.count(trend)
        return [{"trend": k, "count": v} for k, v in trend_count.items()]

    language_results = [{"language": k, "top_trends": get_trend_count(language_dict[k], [trend for lang_set in language_dict.values() for trend in lang_set])} for k in language_dict]
    country_results = [{"country": k, "top_trends": get_trend_count(country_dict[k], [trend for country_set in country_dict.values() for trend in country_set])} for k in country_dict]
    user_location_results = [{"user_location": k, "top_trends": get_trend_count(user_location_dict[k], [trend for loc_set in user_location_dict.values() for trend in loc_set])} for k in user_location_dict]

    for country_data in country_results:
        country = country_data["country"]
        for trend_data in country_data["top_trends"]:
            trend = trend_data["trend"]
            count = trend_data["count"]
            trend_entry = Trends(
                country=country,
                country_top_trends=trend,
                country_top_trends_count=count
            )
            db.session.add(trend_entry)

    for language_data in language_results:
        language = language_data["language"]
        for trend_data in language_data["top_trends"]:
            trend = trend_data["trend"]
            count = trend_data["count"]
            trend_entry = Trends(
                language=language,
                language_top_trends=trend,
                language_top_trends_count=count
            )
            db.session.add(trend_entry)

    for location_data in user_location_results:
        location = location_data["user_location"]
        for trend_data in location_data["top_trends"]:
            trend = trend_data["trend"]
            count = trend_data["count"]
            trend_entry = Trends(
                location=location,
                location_top_trends=trend,
                location_top_trends_count=count
            )
            db.session.add(trend_entry)

    # Commit the changes to the database
    db.session.commit()

    # Return the results as JSON
    return jsonify({'message': 'Trends have been updated'})
