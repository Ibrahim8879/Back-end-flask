from flask import jsonify
from collections import Counter

def get_top_trends(data):
    trends_count = Counter(data)
    top_trends = trends_count.most_common(10)  # Get the top 10 trends
    return top_trends

def get_language_trends(db, Tweets):
    language_trends = db.session.query(Tweets.trend, Tweets.language).all()
    unique_languages = set(language for trend, language in language_trends)
    top_language_trends = {}
    for language in unique_languages:
        language_trends_filtered = [trend for trend, lang in language_trends if lang == language]
        top_trends = get_top_trends(language_trends_filtered)
        top_language_trends[language] = top_trends
    return top_language_trends

def get_country_trends(db, Tweets):
    country_trends = db.session.query(Tweets.trend, Tweets.country).all()
    unique_countries = set(country for trend, country in country_trends)
    top_country_trends = {}
    for country in unique_countries:
        country_trends_filtered = [trend for trend, c in country_trends if c == country]
        top_trends = get_top_trends(country_trends_filtered)
        top_country_trends[country] = top_trends
    return top_country_trends

def get_user_location_trends(db, ProfileData, Tweets):
    user_location_trends = db.session.query(Tweets.trend, ProfileData.location) \
        .join(ProfileData, Tweets.username == ProfileData.username).limit(1000).all()
    unique_locations = set(location for trend, location in user_location_trends)
    top_location_trends = {}
    for location in unique_locations:
        location_trends_filtered = [trend for trend, loc in user_location_trends if loc == location]
        top_trends = get_top_trends(location_trends_filtered)
        top_location_trends[location] = top_trends
    return top_location_trends

    
def get_trends(db, ProfileData, Tweets, Trendsanalysis):
    # Usage
    language_trends = get_language_trends(db, Tweets)
    country_trends = get_country_trends(db, Tweets)
    user_location_trends = get_user_location_trends(db, ProfileData, Tweets)
    
    for language, top_trends in language_trends.items():
        for trend, count in top_trends:
            language_entry = Trendsanalysis(language=language, languages_top_trend=trend,
                                             languages_top_trend_count=count)
            db.session.add(language_entry)
    
    for country, top_trends in country_trends.items():
        for trend, count in top_trends:
            country_entry = Trendsanalysis(countries=country, countries_top_trend=trend,
                                           countries_top_trend_count=count)
            db.session.add(country_entry)
    
    for location, top_trends in user_location_trends.items():
        for trend, count in top_trends:
            location_entry = Trendsanalysis(userLocations=location, userLocations_top_trend=trend,
                                            userLocations_top_trend_count=count)
            db.session.add(location_entry)
    
    db.session.commit()

    # Return the results as JSON
    return jsonify({'message': 'Trends analysis data added to the database'})