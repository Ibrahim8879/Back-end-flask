from collections import Counter
from flask import jsonify 
from sqlalchemy import func
import pandas as pd
import os
import csv

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

def testing_case(db, Tweets):
    basedir = os.path.abspath(os.getcwd())
    basedir = basedir + "\\api\\features\\"
    path = os.path.join(basedir, f"te.csv")
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        updated_rows = []
        for row in reader:
            updated_row = [convert_to_int(value) for value in row]
            updated_rows.append(updated_row)

    # Convert updated rows to a dictionary
    data = {'updated_rows': updated_rows}

    return jsonify(data)
