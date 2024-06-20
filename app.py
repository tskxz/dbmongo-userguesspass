from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with your secret key
app.config['MONGO_URI'] = 'mongodb://localhost:27017/crud'  # Replace with your MongoDB URI

mongo = PyMongo(app)

# MongoDB collection 'data' schema: {_id: ObjectId(), username: str, password: str, role: str, admin_access: int}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        app.logger.info(f"Login attempt with username: {username}")

        user = mongo.db.data.find_one({'username': username})

        if user:
            app.logger.info(f"User found: {user}")

            if check_password_hash(user['password'], password):
                flash('Login Successful', 'success')
                if user['role'] == 'admin':
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('user'))
            else:
                app.logger.warning(f"Password mismatch for user: {username}")
                flash('Login Failed. Please check your credentials.', 'danger')
        else:
            app.logger.warning(f"User not found for username: {username}")
            flash('Login Failed. Please check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/user')
def user():
    current_user = mongo.db.data.find_one({'username': 'user'})

    return render_template('user.html', admin_access=current_user['admin_access'])

@app.route('/guess_password', methods=['POST'])
def guess_password():
    if request.method == 'POST':
        password_guess = request.form['password_guess']

        current_user = mongo.db.data.find_one({'username': 'user'})

        if current_user and current_user['role'] == 'user':
            admin_user = mongo.db.data.find_one({'role': 'admin'})
            
            if admin_user and check_password_hash(admin_user['password'], password_guess):
                mongo.db.data.update_one({'username': current_user['username']}, {'$set': {'admin_access': 1}})
                flash('Congratulations! You have gained admin access.', 'success')
            else:
                flash('Incorrect password. Please try again.', 'danger')

    return redirect(url_for('user'))

@app.route('/admin')
def admin():
    current_user = mongo.db.data.find_one({'username': 'user'})

    if current_user and current_user['admin_access'] == 1:
        return render_template('admin.html')
    else:
        flash('You do not have admin access.', 'danger')
        return redirect(url_for('user'))

@app.route('/logout')
def logout():
    # Implement logout functionality as needed
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
