from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'superPuperSecretKey123'

db = SQLAlchemy(app)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serving = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Food {self.id} {self.name}>'

with app.app_context():
    db.create_all()
    
@app.route('/', methods=['GET', 'POST'])
def index():  # переименовали функцию
    if request.method == 'POST':
        name = request.form['food_name']
        serving = int(request.form['food_serving'])
        calories = int(request.form['food_calories'])
        db.session.add(Food(name=name, serving=serving, calories=calories))
        db.session.commit()
        flash('Food added!', 'success')
        return redirect(url_for('index'))
    foods = Food.query.order_by(Food.time.desc()).all()
    total_calories = sum(f.calories for f in foods)
    return render_template('dashboard.html', foods=foods, total_calories=total_calories)

@app.route('/delete/<int:food_id>')
def delete_food(food_id):
    f = Food.query.get_or_404(food_id)
    db.session.delete(f)
    db.session.commit()
    flash('Record deleted', 'warning')
    return redirect(url_for('index'))

@app.route('/update/<int:food_id>', methods=['GET', 'POST'])
def update_food(food_id):
    f = Food.query.get_or_404(food_id)
    if request.method == 'POST':
        f.name = request.form['food_name']
        f.serving = int(request.form['food_serving'])
        f.calories = int(request.form['food_calories'])
        db.session.commit()
        flash('Record updated', 'info')
        return redirect(url_for('index'))
    return render_template('update_food.html', food=f)

@app.route('/login')
def login():
    return 'Login page'

@app.route('/register')
def register():
    return 'Register page'

if __name__ == '__main__':
    app.run(debug=True)
