from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import Form, SelectField, BooleanField, StringField, FloatField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm, CSRFProtect  # Agregamos la importación de Flask-WTF

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configura Flask-WTF
csrf = CSRFProtect(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    price = db.Column(db.Float)

class SellBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])

class BuyBookForm(FlaskForm):
    book = SelectField('Book', validators=[DataRequired()])
    seller = StringField('Seller', validators=[DataRequired()])
    total_price = FloatField('Total Price', validators=[DataRequired()])

class PublishBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/sell_book', methods=['GET', 'POST'])
@login_required
def sell_book():
    form = SellBookForm(request.form)
    if request.method == 'POST' and form.validate():
        book = Book(title=form.title.data, author=form.author.data, price=form.price.data)
        db.session.add(book)
        db.session.commit()
        flash('Book listed for sale', 'success')
        return redirect(url_for('home'))
    return render_template('sell_book.html', form=form)

@app.route('/buy_book', methods=['GET', 'POST'])
@login_required
def buy_book():
    form = BuyBookForm(request.form)
    books = [(book.id, f"{book.title} by {book.author}") for book in Book.query.all()]
    form.book.choices = books
    if request.method == 'POST' and form.validate():
        book_id = form.book.data
        seller = form.seller.data
        book = Book.query.get(book_id)
        if book:
            total_price = form.total_price.data
            flash(f'You have bought {book.title} by {book.author} from {seller} for ${total_price:.2f}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Book not found', 'danger')
    return render_template('buy_book.html', form=form)

@app.route('/publish_book', methods=['GET', 'POST'])
@login_required
def publish_book():
    form = PublishBookForm(request.form)
    if request.method == 'POST' and form.validate():
        book = Book(title=form.title.data, author=form.author.data, price=form.price.data)
        db.session.add(book)
        db.session.commit()
        flash('Book published for sale', 'success')
        return redirect(url_for('home'))
    return render_template('publish_book.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)