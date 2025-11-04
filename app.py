from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # required for session

# --- Database setup ---
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    movie TEXT,
                    tickets INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Dummy movie data ---
movies_data = [
    {"name": "Inception", "price": 250},
    {"name": "Interstellar", "price": 300},
    {"name": "Avatar", "price": 280},
    {"name": "The Dark Knight", "price": 270},
    {"name": "KGF 2", "price": 200}
]

# --- Admin credentials ---
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html', movies=movies_data)

@app.route('/book/<movie_name>')
def book(movie_name):
    return render_template('book.html', movie=movie_name)

@app.route('/confirm', methods=['POST'])
def confirm():
    name = request.form['name']
    email = request.form['email']
    tickets = int(request.form['tickets'])
    movie = request.form['movie']

    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('INSERT INTO bookings (name, email, movie, tickets) VALUES (?, ?, ?, ?)',
              (name, email, movie, tickets))
    conn.commit()
    conn.close()

    return render_template('success.html', name=name, movie=movie, tickets=tickets)

# --- Admin Login Page ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error="Invalid credentials!")
    return render_template('admin_login.html')

# --- Admin Panel ---
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bookings')
    data = c.fetchall()
    conn.close()
    return render_template('admin.html', bookings=data)

# --- Admin Logout ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# --- Run the app ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render provides PORT
    app.run(host='0.0.0.0', port=port)
