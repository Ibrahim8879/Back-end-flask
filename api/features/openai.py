import google.generativeai as genai
import re
from flask import jsonify

def remove_hashtags(tweet):
    return re.sub(r'#\w+', '', tweet)

def google_stance(db, Tweets, trend):
    topic = trend
    tweets_list = db.session.query(Tweets.tweet).filter(Tweets.trend == topic).limit(200).all()
    tweets = {index + 1: remove_hashtags(tweet[0]) for index, tweet in enumerate(tweets_list)}
    
    genai.configure(api_key='AIzaSyCdSUYfy80WL6fcToPvG-FgQFjcx7NYlvQ')
    # Initialize the model
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""I have a list of tweets related to a specific topic.
      I need to perform a stance analysis on this data to determine whether
        each tweet is "agreed" or "disagreed" with the given topic.
        The analysis should be conducted 10 times to ensure reliability, 
        and the final output should be a list containing "agreed" or "disagreed"
        for each tweet based on the most probable stance from these analyses. Tweets:{tweets}, Topic: {topic}"""
    
    stance_analysis = model.generate_content(prompt)
    stance_text = stance_analysis.text
    agreed_count = stance_text.count("Agreed")
    disagreed_count = stance_text.count("Disagreed")

    #print({"Total Agreed:", agreed_count, "Total Disagreed:", disagreed_count})
    # Print the total count of each sentiment
    response = {"agreed": agreed_count, "disagreed": disagreed_count}
    reponse_data = jsonify(response)
    return reponse_data