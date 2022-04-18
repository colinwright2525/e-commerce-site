from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from flask_bootstrap import Bootstrap
import werkzeug.security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from games import Boardgame, descriptions
import os
import stripe
import math

stripe.api_key = 'sk_test_51Koa0FJHonimlikof3kQ3rxOhvQljmJtktIswOKsx74S353AyH36pxxEya1Ia7yXl2ece01SnVUJUq381cj513tK00tXJdUtPo'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///commerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    cart = db.Column(db.String(500))

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log me in!")


# db.create_all()

monopoly = Boardgame(id=0, name='Monopoly', description=descriptions['Monopoly'], price='$19.99', image='static/images/monopoly.jpg')
scrabble = Boardgame(id=1, name='Scrabble', description=descriptions['Scrabble'], price='$14.99', image='static/images/scrabble.jpg')
clue = Boardgame(id=2, name='Clue', description=descriptions['Clue'], price='$24.99', image='static/images/clue.jpg')
risk = Boardgame(id=3, name='Risk', description=descriptions['Risk'], price='$34.99', image='static/images/risk.jpeg')

boardgames = [monopoly, scrabble, clue, risk]

@app.route('/')
def home():
    session.clear()
    return render_template("index.html", games=boardgames)


@app.route('/home')
def get_all_games():
    message = 'Boardgame Marketplace'
    sub_message = 'Prepare for your next game night here!'
    return render_template("index.html", games=boardgames, message=message, sub_message=sub_message)

@app.route('/success')
def success():
    message = 'Payment successful!'
    sub_message = 'Continue shopping for more fun games!'
    return render_template("index.html", games=boardgames, message=message, sub_message=sub_message)

@app.route('/cancel')
def cancel():
    message = 'Payment failed!'
    sub_message = 'Continue shopping for more fun games!'
    return render_template("index.html", games=boardgames, message=message, sub_message=sub_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        all_users = db.session.query(User).all()
        all_emails = [user.email for user in all_users]
        for email in all_emails:
            if email == request.form.get("email"):
                flash('This email already belongs to an existing account, log-in instead!')
                return render_template('login.html', form=form)

        password = request.form.get("password")
        hashed_password = werkzeug.security.generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=request.form.get("email"),
            password=hashed_password,
            name=request.form.get("name"),
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('get_all_games'))
    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form["email"]).first()
        given_password = request.form.get('password')

        if not user:
            flash('Account does not exist')
            return render_template('login.html', form=form)
        elif not check_password_hash(user.password, given_password):
            flash('Given password is incorrect')
            return render_template('login.html', form=form)
        else:
            flash('Logged in successfully')
            login_user(user)
            return redirect(url_for("get_all_games"))

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('get_all_games'))

@app.route('/cart')
def cart():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    name = user.cart
    shopping_cart = []
    if name == None:
        return render_template('cart.html', cart=shopping_cart)
    else:
        names = name.split()
        for name in names:
            for game in boardgames:
                if game.name == name:
                    shopping_cart.append(game)



        return render_template('cart.html', cart=shopping_cart)

@app.route('/add-to-cart/<int:game_id>')
def add_to_cart(game_id):
    for game in boardgames:
        if game.id == game_id:
            item = game.name
            id = current_user.id
            user = User.query.filter_by(id=id).first()
            if user.cart == None:
                user.cart = item
            else:
                user.cart += f' {item}'
            db.session.commit()

    return redirect(url_for('get_all_games'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    name = user.cart
    shopping_cart = []
    if name == None:
        return render_template('checkout.html', cart=shopping_cart)
    else:
        names = name.split()
        for name in names:
            for game in boardgames:
                if game.name == name:
                    shopping_cart.append(game)
        return render_template('checkout.html', cart=shopping_cart)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    cart = user.cart
    shopping_cart = []
    names = cart.split()
    for name in names:
        for game in boardgames:
            if game.name == name:
                shopping_cart.append(game)
    price_items = []
    for game in shopping_cart:
        price = game.price.replace("$", "")
        price = float(price)
        price = int(math.ceil(price))
        price = price * 100
        game = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': game.name,
                },
                'unit_amount': price,
            },
            'quantity': 1,
        }
        price_items.append(game)
    session = stripe.checkout.Session.create(
        line_items=price_items,
        mode='payment',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
    )

    return redirect(session.url, code=30)

@app.route('/delete/<int:game_id>')
def delete_game(game_id):
    for game in boardgames:
        if game.id == game_id:
            item = game.name
            id = current_user.id
            user = User.query.filter_by(id=id).first()
            cart = user.cart
            cart_items = cart.split(" ")
            if item in cart_items:
                cart_items.remove(item)
            user.cart = ' '.join(cart_items)
            db.session.commit()

    return redirect(url_for('cart'))
if __name__ == "__main__":
    app.run(debug=True)