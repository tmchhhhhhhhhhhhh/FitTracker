from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate






app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'superPuperSecretKey123'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serving = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Food {self.id} {self.name}>'
    
    
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

    
@app.route('/', methods=['GET', 'POST'])
@login_required
def index(): 
    if request.method == 'POST':
        name = request.form['food_name']
        serving = int(request.form['food_serving'])
        calories = int(request.form['food_calories'])
        db.session.add(Food(name=name, serving=serving, calories=calories, user_id=current_user.id))
        db.session.commit()
        flash('Food added!', 'success')
        return redirect(url_for('index'))
    foods = Food.query.filter_by(user_id=current_user.id).order_by(Food.time.desc()).all()
    total_calories = sum(f.calories for f in foods)
    return render_template('dashboard.html', foods=foods, total_calories=total_calories)

@app.route('/delete/<int:food_id>')
def delete_food(food_id):
    f = Food.query.get_or_404(food_id)
    if f.user_id != current_user.id:
        flash("You don't have permission to delete this item.", "danger")
        return redirect(url_for('index'))
    db.session.delete(f)
    db.session.commit()
    flash('Record deleted', 'warning')
    return redirect(url_for('index'))

@app.route('/update/<int:food_id>', methods=['GET', 'POST'])
def update_food(food_id):
    f = Food.query.get_or_404(food_id)
    if f.user_id != current_user.id:
        flash("You don't have permission to delete this item.", "danger")
        return redirect(url_for('index'))
    if request.method == 'POST':
        f.name = request.form['food_name']
        f.serving = int(request.form['food_serving'])
        f.calories = int(request.form['food_calories'])
        db.session.commit()
        flash('Record updated', 'info')
        return redirect(url_for('index'))
    return render_template('update_food.html', food=f)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
