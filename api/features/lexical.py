from flask import jsonify 
import pandas as pd
import re

twitter_tags = {
    "qst": "Question Status",
    "qht": "Question Hashtags",
    "qme": "Question Mention",
    "eu": "European Union",
    "ja": "Japanese",
    "lv": "Latvian",
    "dv": "Divehi (Maldivian)",
    "fi": "Finnish",
    "sl": "Slovenian",
    "tr": "Turkish",
    "da": "Danish",
    "de": "German",
    "et": "Estonian",
    "hu": "Hungarian",
    "in": "Indonesian",
    "nl": "Dutch",
    "sv": "Swedish",
    "tl": "Tagalog (Filipino)",
    "zh": "Chinese",
    "ar": "Arabic",
    "ca": "Catalan",
    "cs": "Czech",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ht": "Haitian Creole",
    "is": "Icelandic",
    "it": "Italian",
    "ko": "Korean",
    "pl": "Polish",
    "und": "Undetermined (language not identified)",
    "bn": "Bengali",
    "ckb": "Central Kurdish (Sorani)",
    "fa": "Persian (Farsi)",
    "my": "Burmese",
    "no": "Norwegian",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "ps": "Pashto",
    "sd": "Sindhi",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "iw": "Hebrew",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "hi": "Hindi",
    "lt": "Lithuanian",
    "or": "Odia (Oriya)",
    "gu": "Gujarati",
    "kn": "Kannada",
    "qam": "Question American",
    "si": "Sinhala",
    "mr": "Marathi",
    "ne": "Nepali",
    "qct": "Question Canadian (Quebec)",
    "ml": "Malayalam"
}

def count_unique_words(tweet):
    words = re.findall(r'\b\w+\b', tweet.lower())
    unique_words = set(words)
    return len(unique_words)

def analyze_lexical_analysis_language(db, Tweets, Lexical_lang, Date):
    # Query the database to fetch tweets and their languages
    tweets = db.session.query(Tweets.tweet, Tweets.language).filter(Tweets.date == Date).all()

    # Convert the query result to a DataFrame
    df = pd.DataFrame(tweets, columns=['tweet', 'language'])

    # Compute the count of unique words in each tweet
    df['uniqueWordsCount'] = df['tweet'].apply(count_unique_words)

    # Compute the diversity for each tweet
    diversity = [uniqueWords / len(singleTweet) if len(singleTweet) > 0 else 0 for singleTweet, uniqueWords in zip(df.tweet, df.uniqueWordsCount)]
    df['diversity'] = diversity
    
    # Group the DataFrame by 'language' and calculate the mean of 'diversity' within each group
    mean_diversity_by_language = df.groupby('language')['diversity'].mean()

    for language, avg_diversity in mean_diversity_by_language.items():
        # Get the full name of the language tag
        language_name = twitter_tags.get(language, "Unknown")

        # Create a new entry in the Lexical table with language tag and full name
        new_lexical_entry = Lexical_lang(date=Date, language_tag=language, language_name=language_name, diversity=int(round(avg_diversity * 100)))
        db.session.add(new_lexical_entry)

    db.session.commit()

    return jsonify({'message': 'Lexical Diversity updated successfully'})

def analyze_lexical_analysis_location(db, Tweets, Lexical_loca, Date):
    # Query the database to fetch tweets and their languages
    tweets = db.session.query(Tweets.tweet, Tweets.country).filter(Tweets.date == Date).limit(100).all()

    # Convert the query result to a DataFrame
    df = pd.DataFrame(tweets, columns=['tweet', 'country'])

    # Compute the count of unique words in each tweet
    df['uniqueWordsCount'] = df['tweet'].apply(count_unique_words)

    # Compute the diversity for each tweet
    diversity = [uniqueWords / len(singleTweet) if len(singleTweet)>0 else 0 for singleTweet, uniqueWords in zip(df.tweet, df.uniqueWordsCount)]
    df['diversity'] = diversity
    
    # Group the DataFrame by 'country' and calculate the mean of 'diversity' within each group
    mean_diversity_by_language = df.groupby('country')['diversity'].mean()

    for country, avg_diversity in mean_diversity_by_language.items():
            new_lexical_entry = Lexical_loca(date=Date, location_tag=country, location_name=country, diversity=round(avg_diversity*100))
            db.session.add(new_lexical_entry)
    db.session.commit()

    return jsonify({'message': 'Lexical Diversity updated successfully'})

def analyze_lexical_analysis(db, Tweets, Lexical_lang, Lexical_loca, Date):
    analyze_lexical_analysis_language(db, Tweets, Lexical_lang, Date)
    analyze_lexical_analysis_location(db, Tweets, Lexical_loca, Date)
    return jsonify({'message': 'Lexical Diversity updated successfully'})