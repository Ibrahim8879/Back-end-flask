from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import os
import csv
import pandas as pd
import subprocess
from features.schedular_db_push import collect_data_job
from features.trends import get_trends
from features.word_freq import analyze_word_frequency, analyze_abusive_language, get_all_languages, analyze_sentiments_in_languages
from features.dataset_info import get_db_details
from features.lexical import analyze_lexical_analysis


app = Flask(__name__)
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
    followers = db.Column(db.String(50))
    following = db.Column(db.String(50))
    verified = db.Column(db.String(50))
    num_posts = db.Column(db.String(50))
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
class Trendsanalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    languages_top_trend = db.Column(db.String)
    countries  = db.Column(db.String)
    countries_top_trend = db.Column(db.String)
    userLocations  = db.Column(db.String)
    userLocations_top_trend = db.Column(db.String)


#scheduling the job
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
                            followers=row['Followers'],
                            following=row['Following'],
                            verified=row['Verified'],
                            num_posts=row['Number of Posts'],
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

# Schedule the job to run every 12 hours
scheduler.add_job(id='collect_data_job', func=job, trigger='interval', seconds=15)
# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

# Routes
@app.route('/', methods=['GET'])
def home():
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """
@app.route('/test')
def test():
    return get_all_languages(db, Tweets)

@app.route('/trends', methods=['GET'])
def trends():
    return get_trends(db, ProfileData, Tweets)

@app.route('/wordfrequency')
def word_frequency():
    return analyze_word_frequency(db, Tweets, Wordfrequency)

@app.route('/abusivewords')
def abusivewords():
    return analyze_abusive_language(db, Tweets)

@app.route('/sentiments')
def sentiments():
    return analyze_sentiments_in_languages(db, Tweets)

@app.route('/lexical')
def lexical():
    return analyze_lexical_analysis(db, Tweets, ProfileData)

@app.route('/dataset_info')
def dataset_info():
    get_db_details(db, ProfileData, Tweets)
    #get_trend_regions_details(db, Tweets)
    #get_tweet_languages_details(db, Tweets)
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """


if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        #scheduler.start()
        db.create_all()
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0')