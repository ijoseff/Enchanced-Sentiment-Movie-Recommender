import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import bs4 as bs
import urllib.request
from datetime import date, datetime
import os

app = Flask(__name__)

# Load the NLP model and vectorizer from disk with error handling
try:
    clf = pickle.load(open('nlp_model.pkl', 'rb'))
    vectorizer = pickle.load(open('tranform.pkl', 'rb'))
except FileNotFoundError as e:
    raise Exception("Model or vectorizer file not found. Ensure 'nlp_model.pkl' and 'tranform.pkl' exist.") from e

def convert_to_list(my_list):
    try:
        my_list = my_list.strip('[]').split('","')
        my_list[0] = my_list[0].lstrip('["')
        my_list[-1] = my_list[-1].rstrip('"]')
        return my_list
    except Exception:
        return []

def convert_to_list_num(my_list):
    try:
        return [int(num.strip()) for num in my_list.strip('[]').split(',')]
    except ValueError:
        return []

def get_suggestions():
    try:
        data = pd.read_csv('main_data.csv')
        return list(data['movie_title'].str.capitalize())
    except FileNotFoundError:
        return []

@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions)

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Get data from AJAX request
        title = request.form.get('title', '')
        cast_ids = convert_to_list_num(request.form.get('cast_ids', '[]'))
        cast_names = convert_to_list(request.form.get('cast_names', '[]'))
        cast_chars = convert_to_list(request.form.get('cast_chars', '[]'))
        cast_bdays = convert_to_list(request.form.get('cast_bdays', '[]'))
        cast_bios = convert_to_list(request.form.get('cast_bios', '[]'))
        cast_places = convert_to_list(request.form.get('cast_places', '[]'))
        cast_profiles = convert_to_list(request.form.get('cast_profiles', '[]'))
        imdb_id = request.form.get('imdb_id', '')
        poster = request.form.get('poster', '')
        genres = request.form.get('genres', '')
        overview = request.form.get('overview', '')
        vote_average = request.form.get('rating', '')
        vote_count = request.form.get('vote_count', '')
        rel_date = request.form.get('rel_date', '')
        release_date = request.form.get('release_date', '')
        runtime = request.form.get('runtime', '')
        status = request.form.get('status', '')
        rec_movies = convert_to_list(request.form.get('rec_movies', '[]'))
        rec_posters = convert_to_list(request.form.get('rec_posters', '[]'))
        rec_movies_org = convert_to_list(request.form.get('rec_movies_org', '[]'))
        rec_year = convert_to_list_num(request.form.get('rec_year', '[]'))
        rec_vote = convert_to_list_num(request.form.get('rec_vote', '[]'))

        # Get movie suggestions for auto-complete
        suggestions = get_suggestions()

        # Render movie cards and cast data
        movie_cards = {rec_posters[i]: [rec_movies[i], rec_movies_org[i], rec_vote[i], rec_year[i]] 
                       for i in range(len(rec_posters))}
        casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] 
                 for i in range(len(cast_profiles))}
        cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] 
                        for i in range(len(cast_places))}

        # Web scraping IMDB reviews
        reviews_list = []
        reviews_status = []
        try:
            sauce = urllib.request.urlopen(f'https://www.imdb.com/title/{imdb_id}/reviews?ref_=tt_ov_rt').read()
            soup = bs.BeautifulSoup(sauce, 'lxml')
            soup_result = soup.find_all("div", {"class": "text show-more__control"})
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    movie_vector = vectorizer.transform([reviews.string])
                    pred = clf.predict(movie_vector)
                    reviews_status.append('Positive' if pred else 'Negative')
        except Exception as e:
            print(f"Error fetching reviews: {e}")

        movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}

        # Calculate current and release dates
        curr_date = datetime.strptime(str(date.today()), '%Y-%m-%d') if rel_date else ""
        movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d') if rel_date else ""

        return render_template('recommend.html', title=title, poster=poster, overview=overview,
                               vote_average=vote_average, vote_count=vote_count, release_date=release_date,
                               movie_rel_date=movie_rel_date, curr_date=curr_date, runtime=runtime, 
                               status=status, genres=genres, movie_cards=movie_cards, reviews=movie_reviews, 
                               casts=casts, cast_details=cast_details)
    except Exception as e:
        print(f"Error in recommendation logic: {e}")
        return render_template('error.html', message="An error occurred while processing your request.")

if __name__ == '__main__':
    app.run(debug=True)
