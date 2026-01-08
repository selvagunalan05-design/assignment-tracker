from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
# user email ID
USER_EMAIL="selvagunalan05@gmail.com"

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

def send_email (to_email,subject,message):
   try:
        sender_email="selva94406@gmail.com"
        app_password='zypa oepy omic hwcf'

        msg=MIMEText(message)
        msg['subject']=subject
        msg['From']=sender_email
        msg['To']=to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print("Email sent Succesfully")

   except Exception as e:
       print("Message failed to send",e)

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
    reminder_message = None
    assignment_data = []

    for i in assignments:
        due = datetime.strptime(i['due_date'], "%Y-%m-%d").date()
        days_left = (due - today).days


        if i['status'] == 'Pending':
            pending += 1
            if days_left < 0:
                overdue += 1
            if days_left == 0:
                reminder_message = "⚠ You have assignments due today!"
                send_email ( USER_EMAIL, "Assignment Due today", f"hey friend i'm sure you wouldn't forgot to eat your breakfast,lunch, and Dinner then how the hell did you forgot to complete your assignment, your assignment'{i['title']}' is due today")

            elif days_left < 0:
                reminder_message = "❌ You have overdue assignments!"

        elif i['status'] =='Submitted':
             completed+=1

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
        overdue=overdue,
        reminder_message=reminder_message

    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        subject = request.form['subject']
        title = request.form['title']
        due_date = request.form['due_date']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO assignments (subject, title, due_date, status) VALUES (?, ?, ?, ?)',
            (subject, title, due_date, 'Pending')
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    conn=get_db_connection()
    conn.execute('DELETE FROM assignments WHERE id=?',(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

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


