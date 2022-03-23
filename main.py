from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


API_Key = 'cf683xxxxxxxx'
API_URL = 'https://api.themoviedb.org/3/search/movie/'


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies_list.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField(label="Your Rating out of 10 e.g. 6.5")
    review = StringField(label="Your Review")
    submit = SubmitField(label="Done")


class AddMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.ranking).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)- i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(f"{API_URL}", params={"api_key": API_Key, "query" : movie_title})
        data = response.json()["results"]
        return render_template("select.html", results=data)

    return render_template("add.html", form=form)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie= movie_to_update, form=form)


@app.route('/find')
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        resp = requests.get(f"https://api.themoviedb.org/3/movie/{movie_api_id}", params={"api_key": API_Key})
        details = resp.json()
        new_movie = Movie(
        title=details['title'],
        year=details['release_date'].split('-')[0],
        description=details['overview'],
        img_url=f"{'https://image.tmdb.org/t/p/w500'}{details['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
