from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_cors import CORS, cross_origin
import os
import csv
import pandas as pd
from datetime import datetime
from collections import defaultdict
import urllib.parse
import subprocess
from features.location_cleaning import Cleaning_locations
from features.trends import get_trends, fetch_trends_data
from features.abusive_sentiment import count_words_in_csv, analyze_abusive_language,analyze_sentiments_in_languages
from features.wordFrequency import analyze_word_frequency
from features.influence import analyze_influence_in_languages
from features.dataset_info import get_db_details
from features.lexical import analyze_lexical_analysis
from features.openai import google_stance

app = Flask(__name__)
CORS(app, resources={r"http://localhost:3000/wordusageext1": {"origins": 'http://localhost:3000/'},
                     r"http://localhost:3000/stance": {"origins": 'http://localhost:3000/'},})
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = APScheduler()
scheduler.init_app(app)
# Database
datacoll = os.path.abspath(os.getcwd())
basedir = os.path.abspath(os.getcwd())
basedir = basedir + '\\db\\twitter.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.db'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + basedir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class ProfileData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    birth_date = db.Column(db.String(255))
    description = db.Column(db.String(500))
    location = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    following = db.Column(db.Integer)
    verified = db.Column(db.String(50))
    num_posts = db.Column(db.Integer)
    date_joined = db.Column(db.String(255))
class Tweets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    country = db.Column(db.String(255))
    trend = db.Column(db.String(255))
    username = db.Column(db.String(255))
    tweet = db.Column(db.String(2000))
    language = db.Column(db.String(255))
    tweet_time = db.Column(db.String(255))
class Abusivewords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    language = db.Column(db.String)
    frequency = db.Column(db.Integer)
class Abusivewords_dictcount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_tag = db.Column(db.String(10), unique=True)
    word_count = db.Column(db.Integer)
class Sentimentwords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    language = db.Column(db.String)
    positive_frequency = db.Column(db.Integer)
    negative_frequency = db.Column(db.Integer)
    neutral_frequency = db.Column(db.Integer)
class Lexical_lang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    language_tag = db.Column(db.String)
    language_name = db.Column(db.String)
    diversity = db.Column(db.Integer)
class Lexical_loca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    location_tag = db.Column(db.String)
    location_name = db.Column(db.String)
    diversity = db.Column(db.Integer)    
class InfluenceAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    location = db.Column(db.String(255))
    languages = db.Column(db.String(255))
    regions = db.Column(db.String(255))
    hashtags = db.Column(db.String(255))
class Wordfrequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    country = db.Column(db.String)
    country_word = db.Column(db.String)
    country_frequency = db.Column(db.Integer)
    language = db.Column(db.String)
    language_word = db.Column(db.String)
    language_frequency = db.Column(db.Integer)
class Trendsanalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    language = db.Column(db.String)
    languages_top_trend = db.Column(db.String)
    languages_top_trend_count = db.Column(db.Integer)
    countries  = db.Column(db.String)
    countries_top_trend = db.Column(db.String)
    countries_top_trend_count = db.Column(db.Integer)
    userLocations  = db.Column(db.String)
    userLocations_top_trend = db.Column(db.String)
    userLocations_top_trend_count = db.Column(db.Integer)    


#scheduling the job
def convert_to_int(value):
    value = value.replace(',', '')  # Remove commas
    if value.isdigit():
        return int(value)
    elif value.endswith('K'):
        return int(float(value[:-1]) * 1000)
    elif value.endswith('M'):
        return int(float(value[:-1]) * 1000000)
    else:
        return value
def job():
    with app.app_context():
        # Scrapper Running here.
        #exe_path = os.path.abspath(os.getcwd())
        #exe_path = exe_path+'\\api\\data_collection\\twitter_scraper_main.exe'
        #subprocess.call([exe_path])
        print("Scheduled job executed.")
        # Function to push data from CSV files to the database
        file_path1 = datacoll+'\\api\\data_collection\\ProfileData.csv'
        file_path2 = datacoll+'\\api\data_collection\\tweets.csv'
        db.create_all()
        with open(file_path2, 'r', encoding='utf-8') as file:
            line_count = sum(1 for line in file)
            if line_count > 2:
                print("pushing data in db.")
                with open(datacoll+'\\api\data_collection\\tweets.csv', 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        tweet = Tweets(
                            date=row['Date'],
                            country=row['Country'],
                            trend=row['Trend'],
                            username=row['Username'],
                            tweet=row['Tweet'],
                            language=row['Language'],
                            tweet_time=row['Tweet_Time']
                        )
                        db.session.add(tweet)
                db.session.commit()
                with open(datacoll+'\\api\\data_collection\\ProfileData.csv', 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        profile_data = ProfileData(
                            username=row['Username'],
                            display_name=row['Display Name'],
                            birth_date=row['Birth Date'],
                            description=row['Description'],
                            location=row['Location'],
                            followers=convert_to_int(row['Followers']),
                            following=convert_to_int(row['Following']),
                            verified=row['Verified'],
                            num_posts=convert_to_int(row['Number of Posts']),
                            date_joined=row['Date Joined']
                        )
                        db.session.add(profile_data)

                    db.session.commit()
                print("Data pushed to database.")
            else:
                print("File Not Updated. So, dont update db.")

        #cleaning data files
        def clean_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                first_line = file.readline()  # Read the first line
            # Rewrite the file with just the first line
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(first_line)
        # Example usage
        clean_file(file_path1)
        clean_file(file_path2)
        print("Files are also cleaned.")

        #Now updating all analysis tables
        analyze_sentiments_in_languages(db, Tweets, Sentimentwords)
        analyze_abusive_language(db, Tweets, Abusivewords)
        count_words_in_csv(db, Abusivewords_dictcount)
        analyze_lexical_analysis(db, Tweets, Lexical)
        analyze_influence_in_languages(db, ProfileData, Tweets, InfluenceAnalysis)
        analyze_word_frequency(db, Tweets, Wordfrequency)

        get_trends(db, ProfileData, Tweets, Trends)
        

# Schedule the job to run every 12 hours
#scheduler.add_job(id='collect_data_job', func=job, trigger='interval', seconds=15)
# Error handlers
@app.errorhandler(404)
@cross_origin()
def page_not_found(error):
    return 'This page does not exist', 404

# Routes
@app.route('/', methods=['GET'])
@cross_origin()
def home():
    db.create_all()
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """
@app.route('/test')
@cross_origin()
def test():
    dates = [
        "2023-11-14",
        "2023-12-23",
        "2023-12-26",
        "2023-12-28",
        "2023-12-29",
        "2023-12-30",
        "2024-01-01",
        "2024-01-04",
        "2024-01-05",
        "2024-01-10",
        "2024-01-12",
        "2024-01-15",
        "2024-01-17"
    ]
    #return Cleaning_locations(db, ProfileData)
    #count_words_in_csv(db, Abusivewords_dictcount)
    #analyze_abusive_language(db, Tweets, Abusivewords, date)
    #analyze_sentiments_in_languages(db, Tweets, Sentimentwords, date)
    #analyze_influence_in_languages(db, ProfileData, Tweets, InfluenceAnalysis)
    #get_trends(db, ProfileData, Tweets, Trendsanalysis, date)

    #analyze_lexical_analysis(db, Tweets, Lexical_lang, Lexical_loca, date) location missing
    
    for date in dates:
        getdata = 0
        getdata = analyze_word_frequency(db, Tweets, Wordfrequency, date)
    return """<h1>Distant Reading Archive</h1>"""
    # analyze_word_frequency(db, Tweets, Wordfrequency, date)


#working, with date
@app.route('/trends', methods=['GET'])
@cross_origin()
def trends_analysis():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate') 
    return fetch_trends_data(db, Trendsanalysis, startDate, endDate)

#Done, Getting Dates
@app.route('/availabledates', methods=['GET'])
@cross_origin()
def available_dates():
    available_dates = Tweets.query.with_entities(Tweets.date).distinct().all()
    sorted_dates = sorted(available_dates)
    starting_dates = [date[0] for date in sorted_dates]
    return jsonify({'startingdate': starting_dates})

#Done
@app.route('/wordfrequency')
@cross_origin()
def word_frequency():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')  
    country = request.args.get('country')
    language = request.args.get('language')

    if country:
        word_frequencies = Wordfrequency.query.filter_by(country=country).filter(Wordfrequency.date.between(startDate, endDate)).all()
        frequency_dict = {}
        for item in word_frequencies:
            word = item.country_word
            frequency = item.country_frequency or 0
            if word in frequency_dict:
                frequency_dict[word] += frequency
            else:
                frequency_dict[word] = frequency
    elif language:
        word_frequencies = Wordfrequency.query.filter_by(language=language).filter(Wordfrequency.date.between(startDate, endDate)).all()
        frequency_dict = {}
        for item in word_frequencies:
            word = item.language_word
            frequency = item.language_frequency or 0
            if word in frequency_dict:
                frequency_dict[word] += frequency
            else:
                frequency_dict[word] = frequency
    else:
        # Handle case where neither country nor language is provided
        return jsonify({'error': 'Please provide either a country or a language.'}), 400
    
    restructured_data = [{'text': word, 'value': frequency} for word, frequency in frequency_dict.items()]

    return jsonify(restructured_data)

#Done, with date
@app.route('/abusivewords')
@cross_origin()
def abusivewords():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')   
    # Query to get all rows from Abusivewords table
    abusive_words = Abusivewords.query.filter(Abusivewords.date.between(startDate, endDate)).all()

    # Structure the data as language, total count, and all words
    structured_data = {}
    for word in abusive_words:
        if word.language not in structured_data:
            structured_data[word.language] = {
                'total_count': 0,
            }
        structured_data[word.language]['total_count'] += word.frequency

    # Convert the structured data to the desired format
    result = []
    for language, data in structured_data.items():
        result.append({
            'language': language,
            'total_count': round(data['total_count'],2),
        })

    # Return the result as JSON
    return jsonify(result)
@app.route('/abusivewords_dictcount')
@cross_origin()
def abusive_words_dict_count():
    abusive_words_dict_count = Abusivewords_dictcount.query.all()
    # Structure the data from Abusivewords_dictcount
    abusive_words_dict_count_data = {}
    for entry in abusive_words_dict_count:
        abusive_words_dict_count_data[entry.language_tag] = entry.word_count

    return jsonify(abusive_words_dict_count_data)

#Done, with date
@app.route('/sentiments')
@cross_origin()
def sentiments():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')   
    sentiment_data = Sentimentwords.query.filter(Sentimentwords.date.between(startDate, endDate)).all()
    formatted_data = [
        {
            "language": data.language,
            "positive_frequency": data.positive_frequency,
            "negative_frequency": data.negative_frequency,
            "neutral_frequency": data.neutral_frequency
        }
        for data in sentiment_data
    ]
    return jsonify(formatted_data)

#Done, with date, addition user locations filter
@app.route('/lexical')
@cross_origin()
def lexical():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')   
    lexical_data = Lexical_lang.query.filter(Lexical_lang.date.between(startDate, endDate)).all()
    lexical_data2 = Lexical_loca.query.filter(Lexical_loca.date.between(startDate, endDate)).all()
    
    # Dictionaries to accumulate diversity values
    language_dict = defaultdict(lambda: {'language_name': '', 'diversity': 0})
    location_dict = defaultdict(lambda: {'location_name': '', 'diversity': 0})

    # Process lexical_data
    for item in lexical_data:
        tag = item.language_tag
        name = item.language_name
        diversity = item.diversity

        if language_dict[tag]['language_name'] == '':
            language_dict[tag]['language_name'] = name
        language_dict[tag]['diversity'] += diversity

    # Process lexical_data2
    for item in lexical_data2:
        tag = item.location_name
        name = item.location_name
        diversity = item.diversity

        if location_dict[tag]['location_name'] == '':
            location_dict[tag]['location_name'] = name
        location_dict[tag]['diversity'] += diversity

    # Convert dictionaries to lists
    data = [{'language_tag': tag, 'language_name': details['language_name'], 'diversity': details['diversity']}
            for tag, details in language_dict.items()]

    data2 = [{'location_tag': tag, 'location_name': details['location_name'], 'diversity': details['diversity']}
            for tag, details in location_dict.items()]

    # Prepare final data
    fdata = {'language': data, 'location': data2}

    # Return JSON response
    return jsonify(fdata)

#Done, no need for date
@app.route('/influence')
@cross_origin()
def influence():
    try:
        # Fetch all data from InfluenceAnalysis table
        influence_data = InfluenceAnalysis.query.all()

        # Convert data to list of dictionaries
        data = []
        for entry in influence_data:
            data.append({
                'id': entry.id,
                'username': entry.username,
                'followers': entry.followers,
                'location': entry.location,
                'languages': entry.languages.split(','),  # Convert comma-separated string to list
                'regions': entry.regions.split(','),  # Convert comma-separated string to list
                'hashtags': entry.hashtags.split(',')  # Convert comma-separated string to list
            })

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#update need in fyp file.
@app.route('/dataset_info')
@cross_origin()
def dataset_info():
    get_db_details(db, ProfileData, Tweets)
    #get_trend_regions_details(db, Tweets)
    #get_tweet_languages_details(db, Tweets)
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """

@app.route('/openai')
@cross_origin()
def openai():
    trend = request.args.get('trend')
    decoded_string_python = urllib.parse.unquote(trend)
    return google_stance(db, Tweets, decoded_string_python)

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0')