from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_cors import CORS, cross_origin
import os
import csv
import pandas as pd
import subprocess
from features.schedular_db_push import collect_data_job
from features.trends import get_trends
from features.word_freq import count_words_in_csv, analyze_abusive_language,analyze_sentiments_in_languages
from features.wordFrequency import analyze_word_frequency
from features.influence import analyze_influence_in_languages
from features.dataset_info import get_db_details
from features.lexical import analyze_lexical_analysis
from features.testing import testing_case


app = Flask(__name__)
CORS(app, resources={r"http://localhost:3000/wordusageext1": {"origins": 'http://localhost:3000/'}})
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
    language = db.Column(db.String)
    words = db.Column(db.String)
    frequency = db.Column(db.Integer)
class Abusivewords_dictcount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_tag = db.Column(db.String(10), unique=True)
    word_count = db.Column(db.Integer)
class Sentimentwords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String)
    positive_frequency = db.Column(db.Integer)
    negative_frequency = db.Column(db.Integer)
    neutral_frequency = db.Column(db.Integer)
class Lexical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_tag = db.Column(db.String)
    language_name = db.Column(db.String)
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
    country = db.Column(db.String)
    country_word = db.Column(db.String)
    country_frequency = db.Column(db.Integer)
    language = db.Column(db.String)
    language_word = db.Column(db.String)
    language_frequency = db.Column(db.Integer)
class Trendsanalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
def page_not_found(error):
    return 'This page does not exist', 404

# Routes
@app.route('/', methods=['GET'])
def home():
    db.create_all()
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """
@app.route('/test')
def test():
    unique_countries = Wordfrequency.query.with_entities(Wordfrequency.language.distinct()).all()
    countries_list = [language[0] for language in unique_countries]
    return jsonify({'countries': countries_list})

#working
@app.route('/trends', methods=['GET'])
@cross_origin()
def trends_analysis():
    return get_trends(db, ProfileData, Tweets, Trendsanalysis)

#Done
@app.route('/wordfrequency')
@cross_origin()
def word_frequency():
    country = request.args.get('country')
    language = request.args.get('language')
    if country:
        word_frequencies = Wordfrequency.query.filter_by(country=country).all()
        restructured_data = [{'text': item.country_word, 'value': item.country_frequency} for item in word_frequencies]
    elif language:
        word_frequencies = Wordfrequency.query.filter_by(language=language).all()
        restructured_data = [{'text': item.language_word, 'value': item.language_frequency} for item in word_frequencies]
    else:
        # Handle case where neither country nor language is provided
        return jsonify({'error': 'Please provide either a country or a language.'}), 400
    
    return jsonify(restructured_data)

#Done, user location plots.
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
@app.route('/abusivewords_dictcount')
def abusive_words_dict_count():
    abusive_words_dict_count = Abusivewords_dictcount.query.all()
    # Structure the data from Abusivewords_dictcount
    abusive_words_dict_count_data = {}
    for entry in abusive_words_dict_count:
        abusive_words_dict_count_data[entry.language_tag] = entry.word_count

    return jsonify(abusive_words_dict_count_data)

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

#Done, user location plots.
@app.route('/lexical')
def lexical():
    lexical_data = Lexical.query.all()
    # Convert the SQLAlchemy objects to dictionaries
    data = []
    for item in lexical_data:
        data.append({
            'language_tag': item.language_tag,
            'language_name': item.language_name,
            'diversity': item.diversity
        })
    return jsonify(data)

#Done
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

#update need in fyp file.
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
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        #scheduler.start()
        app.run(debug=True, host='0.0.0.0')