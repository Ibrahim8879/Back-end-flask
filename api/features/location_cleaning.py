import pandas as pd
from fuzzywuzzy import fuzz
from flask import Flask, jsonify, request
import os

# Function to find approximate matches
def find_approximate_match(user_location, correct_places):
    # Initialize variables to store best match and its similarity score
    best_match = None
    best_score = 0

    # Iterate over correct places and find the best match
    for place in correct_places:
        score = fuzz.partial_ratio(str(user_location), str(place))
        if score > best_score:
            best_match = place
            best_score = score

    # Return the best match
    return best_match if best_score >= 70 else 'NA'  # Adjust threshold as needed

def Cleaning_locations(db, ProfileData):
    matched_results = []

    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\location_cleaning\\location_frequency.csv"
    df = pd.read_csv(basedir, encoding='unicode_escape')
    profile_data = db.session.query(ProfileData).limit(50).all()

    # Iterate over each user location in the database
    for profile in profile_data:
        user_location = profile.location
        matched_city = find_approximate_match(user_location, df['CITIES CLEANED'])
        matched_results.append([user_location, matched_city])

    # Return the matched results as JSON
    return jsonify(matched_results)