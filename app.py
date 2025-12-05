from flask import Flask,request,render_template
import pickle
import requests

app = Flask(__name__)

movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity_list.pkl','rb'))


def get_poster(id):
    api_key = 'c8142edc47ea327653fc16e3c1536462'
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.exceptions.RequestException as e:
        print("API Error:", e)
    
    return "https://via.placeholder.com/300x450?text=No+Image"


def recommend(movie_name):
    movie_name = movie_name.lower()
    if movie_name not in movies['title'].str.lower().values:
        return [], []

    index = movies[movies['title'].str.lower() == movie_name].index[0]
    distances = list(enumerate(similarity[index]))
    movies_list = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

    recommend_movies = []
    recommend_posters = []

    for i in movies_list:
        id = movies.iloc[i[0]].movie_id
        recommend_movies.append(movies.iloc[i[0]].title)
        try:
            poster = get_poster(id)
        except:
            poster = "https://via.placeholder.com/300x450?text=No+Image"
        recommend_posters.append(poster)

    return recommend_movies, recommend_posters





@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend',methods = ['POST'])
def recommend_route():
    movie = request.form['movie']
    recommendations, posters = recommend(movie)
    return render_template("index.html", movie_name=movie, recommendations=recommendations, posters=posters, zip=zip)


if __name__ == '__main__':
    app.run(debug=True)
