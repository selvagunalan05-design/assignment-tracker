from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# Connect to database (creates file if not exists)
conn = sqlite3.connect('index.db')

# Create cursor
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    title TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL
)
''')

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database and table created successfully!")

def get_db_connection():
    conn = sqlite3.connect('index.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    assignments = conn.execute('SELECT * FROM assignments').fetchall()
    conn.close()

    total = len(assignments)
    pending = 0
    completed = 0
    overdue = 0

    today = date.today()

    assignment_data = []

    for i in assignments:
        due = datetime.strptime(i['due_date'], "%Y-%m-%d").date()
        days_left = (due - today).days

        if i['status'] == 'Pending':
            pending += 1
            if days_left < 0:
                overdue += 1
        else:
            completed += 1

        assignment_data.append({
            "id": i["id"],
            "subject": i["subject"],
            "title": i["title"],
            "due_date": i["due_date"],
            "status": i["status"],
            "days_left": days_left
        })

    return render_template('index.html',
        assignments=assignment_data,
        total=total,
        pending=pending,
        completed=completed,
        overdue=overdue
    )

@app.route('/complete/<int:id>')
def complete(id):
    conn = get_db_connection()
    conn.execute(
        'UPDATE assignments SET status = ? WHERE id = ?',
        ('Submitted', id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)
