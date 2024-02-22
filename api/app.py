from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from schedular_db_push import collect_data_job
import os
import csv

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
<<<<<<< Updated upstream
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class TweetsAttribute(db.Model):
    __tablename__ = 'tweets_attribute'
=======
db = SQLAlchemy(app)

class ProfileData(db.Model):
>>>>>>> Stashed changes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    birth_date = db.Column(db.String(255))
    description = db.Column(db.String(500))
    location = db.Column(db.String(255))
    followers = db.Column(db.String(100))
    following = db.Column(db.String(100))
    verified = db.Column(db.String(100))
    num_posts = db.Column(db.String(100))
    date_joined = db.Column(db.String(255))
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255))
    country = db.Column(db.String(255))
    trend = db.Column(db.String(255))
    username = db.Column(db.String(255))
    tweet = db.Column(db.String(2000))
    language = db.Column(db.String(255))
    tweet_time = db.Column(db.String(255))

#scheduling the job
def job():
    with app.app_context():
        print("Scheduled job executed")
        # Function to push data from CSV files to the database
        db.create_all()
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
        with open(datacoll+'\\api\data_collection\\tweets.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tweet = Tweet(
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
        print("Data pushed to database")

# Schedule the job to run every 12 hours
scheduler.add_job(id='collect_data_job', func=job, trigger='interval', seconds=5)



@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.route('/', methods=['GET'])
def home():
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """
    
if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        scheduler.start()
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        scheduler.start()
        app.run(debug=True, host='0.0.0.0')