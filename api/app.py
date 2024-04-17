from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_cors import CORS
import os
import csv
import pandas as pd
import subprocess
from features.schedular_db_push import collect_data_job
from features.trends import get_trends
from features.word_freq import analyze_word_frequency, analyze_abusive_language,analyze_sentiments_in_languages
from features.influence import analyze_influence_in_languages
from features.dataset_info import get_db_details
from features.lexical import analyze_lexical_analysis
from features.testing import testing_case


app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])
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

class Wordfrequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    country_word = db.Column(db.String)
    country_frequency = db.Column(db.Integer)
    trend = db.Column(db.String)
    trend_word = db.Column(db.String)
    trend_frequency = db.Column(db.Integer)

class Abusivewords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    words = db.Column(db.String)
    frequency = db.Column(db.Integer)
class Sentimentwords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    positive_frequency = db.Column(db.Integer)
    negative_frequency = db.Column(db.Integer)
    neutral_frequency = db.Column(db.Integer)
class Lexical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    diversity = db.Column(db.Integer)
class InfluenceAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    location = db.Column(db.String(255))
    languages = db.Column(db.String(255))
    regions = db.Column(db.String(255))
    hashtags = db.Column(db.String(255))


class Trendsanalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    languages_top_trend = db.Column(db.String)
    countries  = db.Column(db.String)
    countries_top_trend = db.Column(db.String)
    userLocations  = db.Column(db.String)
    userLocations_top_trend = db.Column(db.String)
class Trends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(255))
    language_top_trends = db.Column(db.String(255))
    language_top_trends_count = db.Column(db.Integer)
    country = db.Column(db.String(255))
    country_top_trends = db.Column(db.String(255))
    country_top_trends_count = db.Column(db.Integer)
    location = db.Column(db.String(255))
    location_top_trends = db.Column(db.String(255))
    location_top_trends_count = db.Column(db.Integer)


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
        analyze_lexical_analysis(db, Tweets, Lexical)
        analyze_influence_in_languages(db, ProfileData, Tweets, InfluenceAnalysis)


        get_trends(db, ProfileData, Tweets, Trends)
        

# Schedule the job to run every 12 hours
#scheduler.add_job(id='collect_data_job', func=job, trigger='interval', seconds=15)
# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

# Routes
@app.route('/', methods=['GET'])
def home():
    db.create_all()
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """

#working
@app.route('/trends', methods=['GET'])
def get_trends():
    # Retrieve data from the Trends table
    trends_data = Trends.query.all()

    # Process and format the data
    data = {
        'countries': [],
        'locations': [],
        'languages': []
    }

    for trend in trends_data:
        if trend.country:
            country_obj = next((obj for obj in data['countries'] if obj['name'] == trend.country), None)
            if country_obj is None:
                country_obj = {'name': trend.country, 'top_trends': []}
                data['countries'].append(country_obj)
            if trend.country_top_trends:
                country_obj['top_trends'].append({'trend': trend.country_top_trends, 'count': trend.country_top_trends_count})

        if trend.location:
            location_obj = next((obj for obj in data['locations'] if obj['name'] == trend.location), None)
            if location_obj is None:
                location_obj = {'name': trend.location, 'top_trends': []}
                data['locations'].append(location_obj)
            if trend.location_top_trends:
                location_obj['top_trends'].append({'trend': trend.location_top_trends, 'count': trend.location_top_trends_count})

        if trend.language:
            language_obj = next((obj for obj in data['languages'] if obj['name'] == trend.language), None)
            if language_obj is None:
                language_obj = {'name': trend.language, 'top_trends': []}
                data['languages'].append(language_obj)
            if trend.language_top_trends:
                language_obj['top_trends'].append({'trend': trend.language_top_trends, 'count': trend.language_top_trends_count})

    return jsonify(data['countries'])

#Areeb working
@app.route('/wordfrequency')
def word_frequency():
    return analyze_word_frequency(db, Tweets, Wordfrequency)

#Done
@app.route('/abusivewords')
def abusivewords():
    # Query to get all rows from Abusivewords table
    abusive_words = Abusivewords.query.all()

    # Structure the data as language, total count, and all words
    structured_data = {}
    for word in abusive_words:
        if word.language not in structured_data:
            structured_data[word.language] = {
                'total_count': 0,
                'all_words': []
            }
        structured_data[word.language]['total_count'] += word.frequency
        structured_data[word.language]['all_words'].append(word.words)

    # Convert the structured data to the desired format
    result = []
    for language, data in structured_data.items():
        result.append({
            'language': language,
            'total_count': round(data['total_count']*100,2),
            'all_words': data['all_words']
        })

    # Return the result as JSON
    return jsonify(result)

#Done
@app.route('/sentiments')
def sentiments():
    sentiment_data = Sentimentwords.query.all()
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

#Done   
@app.route('/lexical')
def lexical():
    lexical_data = Lexical.query.all()
    # Convert the SQLAlchemy objects to dictionaries
    data = []
    for item in lexical_data:
        data.append({
            'language': item.language,
            'diversity': item.diversity
        })
    return jsonify(data)

#Done almost
@app.route('/influence')
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
    

@app.route('/dataset_info')
def dataset_info():
    get_db_details(db, ProfileData, Tweets)
    #get_trend_regions_details(db, Tweets)
    #get_tweet_languages_details(db, Tweets)
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """

@app.route('/test')
def test():
    return testing_case(db, Tweets)

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0')