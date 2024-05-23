from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd


def get_db_details(db, ProfileData, Tweets):
    # User Locations
    return jsonify({"Done": "Done"})