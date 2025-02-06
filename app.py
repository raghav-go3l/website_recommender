# import streamlit as st
# import pandas as pd
# import pickle
# import requests
#
# def fetch_poster(movie_id):
#     response = requests.get(
#         f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=909c2e53859958e5025681089989ee90&language=en-US")
#     data = response.json()
#     return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
#
#
# def recommend(movie):
#     movie_index = movies[movies['title'] == movie].index[0]
#     distances = similarity[movie_index]
#     movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
#     recommended_movies = []
#     recommended_movies_posters = []
#
#     for i in movie_list:
#         movie_id = movies.iloc[i[0]].movie_id
#         recommended_movies.append(movies.iloc[i[0]].title)
#         recommended_movies_posters.append(fetch_poster(movie_id))
#
#     return recommended_movies, recommended_movies_posters
#
#
# similarity = pickle.load(open('similarity.pkl', 'rb'))
# movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
# movies = pd.DataFrame(movies_dict)
#
# st.title('Movie Recommender System')
#
# selected_movie_name = st.selectbox('Select Movie', movies['title'].values)
#
# if st.button('Recommend'):
#     name, posters = recommend(selected_movie_name)
#     col1, col2, col3, col4, col5 = st.columns(5)
#
#     with col1:
#         st.text(name[0])
#         st.image(posters[0])
#     with col2:
#         st.text(name[1])
#         st.image(posters[1])
#     with col3:
#         st.text(name[2])
#         st.image(posters[2])
#     with col4:
#         st.text(name[3])
#         st.image(posters[3])
#     with col5:
#         st.text(name[4])
#         st.image(posters[4])
#


#below is the og code

# import streamlit as st
# import pandas as pd
# import pickle
# import requests
#
#
# def fetch_poster(movie_id):
#     response = requests.get(
#         f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=909c2e53859958e5025681089989ee90&language=en-US")
#     data = response.json()
#     return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
#
#
# def recommend(movie):
#     movie_index = movies[movies['title'] == movie].index[0]
#     distances = similarity[movie_index]
#     movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
#     recommended_movies = []
#     recommended_movies_posters = []
#
#     for i in movie_list:
#         movie_id = movies.iloc[i[0]].movie_id
#         recommended_movies.append(movies.iloc[i[0]].title)
#         recommended_movies_posters.append(fetch_poster(movie_id))
#
#     return recommended_movies, recommended_movies_posters
#
#
# similarity = pickle.load(open('similarity.pkl', 'rb'))
# movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
# movies = pd.DataFrame(movies_dict)
#
# st.title('Movie Recommender System')
#
# selected_movie_name = st.selectbox('Select Movie', movies['title'].values)
#
# if st.button('Recommend'):
#     name, posters = recommend(selected_movie_name)
#     col1, col2, col3, col4, col5 = st.columns(5)
#
#     with col1:
#         st.text(name[0])
#         st.image(posters[0])
#     with col2:
#         st.text(name[1])
#         st.image(posters[1])
#     with col3:
#         st.text(name[2])
#         st.image(posters[2])
#     with col4:
#         st.text(name[3])
#         st.image(posters[3])
#     with col5:
#         st.text(name[4])
#         st.image(posters[4])

# GPT improvised code below using exception handling

import streamlit as st
import pandas as pd
import pickle
import requests
import time

# Use a session to reuse connections and reduce API failures
session = requests.Session()


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=909c2e53859958e5025681089989ee90&language=en-US"

    retries = 5  # Try 5 times before failing
    backoff_factor = 2  # Exponential backoff (2, 4, 8, 16 sec delays)

    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)  # Increased timeout
            response.raise_for_status()  # Raise error for HTTP issues

            data = response.json()

            # Check if poster_path exists
            if "poster_path" in data and data["poster_path"]:
                return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {backoff_factor ** attempt} seconds...")
            time.sleep(backoff_factor ** attempt)  # Exponential backoff

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Too many requests
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"HTTP error: {e}")
                break  # Don't retry on permanent errors

        except requests.exceptions.Timeout:
            print("Request timed out. Retrying...")
            time.sleep(backoff_factor ** attempt)

        except Exception as e:
            print(f"Unexpected error: {e}")
            break  # Stop retrying on unknown errors

    return "https://via.placeholder.com/500x750?text=Error+Loading+Image"  # Fallback if all retries fail


def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movie_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters
    except IndexError:
        st.error("Movie not found in dataset. Try another movie.")
        return [], []


# Load data
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Streamlit UI
st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Select a Movie', movies['title'].values)

if st.button('Recommend'):
    name, posters = recommend(selected_movie_name)

    if name:  # Only display if recommendations exist
        cols = st.columns(5)  # Create 5 columns for recommendations
        for col, movie_name, poster_url in zip(cols, name, posters):
            with col:
                st.text(movie_name)
                st.image(poster_url)
