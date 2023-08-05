from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_data.db'
db.init_app(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    author = db.Column(db.String(200), unique=False, nullable=False)
    rating = db.Column(db.Float, nullable=False)


# checking if db file exists
data_file = Path('./instance/book_data.db')
if data_file.is_file():
    pass
else:
    with app.app_context():
        db.create_all()

# reading db file
all_books = []


@app.route('/')
def home():
    with app.app_context():
        global all_books
        result = db.session.execute(db.select(Book).order_by(Book.id))
        rated_books = result.scalars()
        all_books = rated_books.all()
    return render_template('index.html', books=all_books)


@app.route("/add", methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        with app.app_context():
            db.create_all()
            new_book = Book(title=request.form['book_name'],
                            author=request.form['book_author'],
                            rating=request.form['book_rating'])
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')


@app.route('/edit/<int:our_id>', methods=['POST', 'GET'])
def edit_rating(our_id):
    if request.method == 'POST':
        new_rating = request.form['change_rating']
        with app.app_context():
            rating = db.session.execute(db.select(Book).where(Book.id == our_id)).scalar()
            rating_to_update = db.session.execute(db.select(Book).where(Book.rating == rating.rating)).scalar()
            rating_to_update.rating = new_rating
            db.session.add(rating_to_update)
            db.session.commit()

        return redirect(url_for('home'))
    return render_template('edit.html', all_books=all_books, our_id=our_id)


@app.route('/delete/<int:our_id>', methods=['POST', 'GET'])
def delete(our_id):
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Book).where(Book.id == our_id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
