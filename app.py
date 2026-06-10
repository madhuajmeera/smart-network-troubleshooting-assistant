import sqlite3
import csv 
from flask import Response
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

issues = {
    "No Signal": [
        "Turn Airplane Mode ON/OFF",
        "Restart Device",
        "Check SIM card"
    ],

    "Data Issue": [
        "Enable Mobile Data",
        "Reset Network Settings",
        "Check APN Settings"
    ],

    "Call Issue": [
        "Check Signal Strength",
        "Restart Device",
        "Try Another Location"
    ],

    "SMS Issue":[
        "Check SMS Center Number",
        "Restart Device",
        "Clear Messaging App Cache"
    ]
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/troubleshoot', methods=['POST'])
def troubleshoot():
    issue = request.form['issue']
    steps = issues.get(issue, [])

    return render_template(
        'troubleshoot.html',
        issue=issue,
        steps=steps
    )

@app.route('/ticket', methods=['POST'])
def ticket():

    name = request.form['name']
    issue = request.form['issue']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO tickets
        (customer_name, issue_type, status)
        VALUES (?, ?, ?)
        ''',
        (name, issue, "Open")
    )

    ticket_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return render_template(
        'ticket.html',
        name=name,
        issue=issue,
        ticket_id=ticket_id
    )

# Admin dashboard
@app.route('/admin')
def admin():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tickets")

    tickets = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM tickets"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Open'"
    )

    open_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Closed'"
    )

    closed_tickets = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin.html', 
        tickets=tickets,
        total=total,
        open_tickets=open_tickets,
        closed_tickets=closed_tickets
    )

#Close ticket function
@app.route('/close/<int:ticket_id>', methods=['POST'])
def close_ticket(ticket_id):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE tickets 
        SET status='Closed'
        WHERE id=?
        ''',
        (ticket_id,)
    )
    conn.commit()
    conn.close()

    return redirect('/admin')

# Creating route for Network health analyzer
@app.route('/network-health')
def network_health():
    return render_template(
        'network_health.html'
    )

#Adding scoring engine

@app.route('/calculate-health', methods=['POST'])
def calculate_health():

    signal = int(request.form['signal'])

    speed = int(request.form['speed'])

    call = int(request.form['call'])

    speed_score = min(speed, 100)

    signal_score = (signal/5)*100

    call_score = (call/5)*100

    final_score = int(
        signal_score*0.4+speed_score*0.3+call_score*0.3
    )

    if final_score >= 80:
        status = "Excellent"

    elif final_score >=60:
        status = "Good"

    elif final_score >=40:
        status = "Poor"

    else:
        status = "Critical"

    return render_template(
        'health_result.html',
        score=final_score,
        status=status
    )

    #Logoin route

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/login-check', methods=['POST'])
    def login_check():

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute(
            '''SELECT * FROM users
            WHERE username=? AND password=?
            ''',
            (username,password)

        )
        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect('/admin')
        return "Invalid Login"

        #Search route

    @app.route('/search')
    def search():

        keyword = request.args.get('keyword')

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT * FROM tickets
            WHERE customer_name LIKE ?
            ''',
            ('%'+keyword+'%',)
        )

        tickets = cursor.fetchall()

        conn.close()

        return render_template(
            'search.html',
            tickets=tickets
        )


    @app.route('/export')
    def export():

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute(

            "SELECT * FROM tickets"
        )
        rows = cursor.fetchall()

        conn.close()

        def generate():

            yield "ID,Customer,Issue,Status\n"

            for row in rows:

                yield(
                    f"{row[0]},"
                    f"{row[1]},"
                    f"{row[2]},"
                    f"{row[3]}\n"
                )

        return Response(
            generate(),
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=tickets.csv"
            }
        )
if __name__=='__main__':
    app.run(debug=True)