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
    # Get top trends
    language_trends = get_language_trends(db, Tweets)
    country_trends = get_country_trends(db, Tweets)
    user_location_trends = get_user_location_trends(db, ProfileData, Tweets)
    
    # Save top language trends
    for language, top_trends in language_trends.items():
        for trend, count in top_trends:
            language_entry = Trendsanalysis(language=language, languages_top_trend=trend,
                                             languages_top_trend_count=count)
            db.session.add(language_entry)
    
    # Save top country trends
    for country, top_trends in country_trends.items():
        for trend, count in top_trends:
            country_entry = Trendsanalysis(countries=country, countries_top_trend=trend,
                                           countries_top_trend_count=count)
            db.session.add(country_entry)
    
    # Save top user location trends
    for location, top_trends in user_location_trends.items():
        for trend, count in top_trends:
            location_entry = Trendsanalysis(userLocations=location, userLocations_top_trend=trend,
                                            userLocations_top_trend_count=count)
            db.session.add(location_entry)
    
    # Commit the changes to the database
    db.session.commit()

    # Return the results as JSON
    return jsonify({'message': language_trends,'message2': country_trends, 'message3':user_location_trends})




#fetching the data from the database
def fetch_language_trends(db, Trendsanalysis):
    language_trends = {}
    # Query top language trends
    top_language_entries = db.session.query(Trendsanalysis.language, Trendsanalysis.languages_top_trend, Trendsanalysis.languages_top_trend_count).all()
    for entry in top_language_entries:
        language = entry.language
        trend = entry.languages_top_trend
        count = entry.languages_top_trend_count
        if language not in language_trends:
            language_trends[language] = []
        language_trends[language].append({"trend": trend, "count": count})
    return language_trends

def fetch_country_trends(db, Trendsanalysis):
    country_trends = {}
    # Query top country trends
    top_country_entries = db.session.query(Trendsanalysis.countries, Trendsanalysis.countries_top_trend, Trendsanalysis.countries_top_trend_count).all()
    for entry in top_country_entries:
        country = entry.countries
        trend = entry.countries_top_trend
        count = entry.countries_top_trend_count
        if country not in country_trends:
            country_trends[country] = []
        country_trends[country].append({"trend": trend, "count": count})
    return country_trends

def fetch_user_location_trends(db, Trendsanalysis):
    location_trends = {}
    # Query top user location trends
    top_location_entries = db.session.query(Trendsanalysis.userLocations, Trendsanalysis.userLocations_top_trend, Trendsanalysis.userLocations_top_trend_count).all()
    for entry in top_location_entries:
        location = entry.userLocations
        trend = entry.userLocations_top_trend
        count = entry.userLocations_top_trend_count
        if location not in location_trends:
            location_trends[location] = []
        location_trends[location].append({"trend": trend, "count": count})
    return location_trends


def fetch_trends_data(db, Trendsanalysis):
    language_trends = fetch_language_trends(db, Trendsanalysis)
    country_trends = fetch_country_trends(db, Trendsanalysis)
    location_trends = fetch_user_location_trends(db, Trendsanalysis)
    
    # Extract unique languages, countries, and locations
    all_languages = list(language_trends.keys())
    all_countries = list(country_trends.keys())
    all_locations = list(location_trends.keys())
    
    # Remove None values if any
    language_trends = {language: trends for language, trends in language_trends.items() if language is not None}
    country_trends = {country: trends for country, trends in country_trends.items() if country is not None}
    location_trends = {location: trends for location, trends in location_trends.items() if location is not None}
    
    return jsonify({
        'languages': all_languages,
        'countries': all_countries,
        'locations': all_locations,
        'languages_trends': language_trends,
        'countries_trends': country_trends,
        'locations_trends': location_trends
    })

