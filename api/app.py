from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.getcwd())
basedir = basedir + '\db\\twitter.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.db'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + basedir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class TweetsAttribute(db.Model):
    __tablename__ = 'tweets_attribute'
    id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.BLOB)
    Trend = db.Column(db.BLOB)
    Country = db.Column(db.BLOB)
    Username = db.Column(db.BLOB)
    Tweet = db.Column(db.BLOB)
    Language = db.Column(db.BLOB)
    Tweet_time = db.Column(db.BLOB)

@app.route('/', methods=['GET'])
def home():
    return """<h1>Distant Reading Archive</h1>
    <p>A prototype API for distant reading of science fiction novels</p>
    """

@app.route('/get', methods=['GET'])
def get_tweets_attributes():
    try:
        tweets_attributes = TweetsAttribute.query.all()
        result = "Hello this is the back end with updated db..."
        print(tweets_attributes)
        #return jsonify(result)
        print(result)
        return jsonify(data=result)
    except Exception as e:  
        return(str(e))
    
if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        app.run(debug=True, host='0.0.0.0') 