from flask import Flask, render_template,jsonify, request, redirect, url_for, session,flash
import sqlite3

app = Flask(__name__)

DATABASE = 'example.db'
app.secret_key = 'your_secret_key_here111'

# Dummy user credentials
admin_username = "admin"
admin_password = "123"
def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time_slot TEXT NOT NULL
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS salesman (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        product TEXT NOT NULL
                    )''')
    print("Creating table done")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    
    return render_template('appointment.html')


# def get_available_slots(date):
#     all_slots = [f"{i:02}:00 - {i+1:02}:00" for i in range(0, 24)]
    
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
    
#     cursor.execute("SELECT time_slot FROM bookings WHERE date=?", (date,))
#     booked_slots = [slot[0].strip() for slot in cursor.fetchall()]  # Strip leading and trailing spaces
    
#     available_slots = [slot for slot in all_slots if slot not in booked_slots]

#     conn.close()
    
#     return available_slots
def get_available_slots(date):
    # Create slots with 4-minute intervals between 6:00 and 8:00
    available_slots = []
    hour = 6
    minute = 0
    for _ in range(30):
        available_slots.append(f"{hour:02}:{minute:02} - {hour:02}:{minute+4:02}")
        minute += 4
        if minute >= 60:
            minute = 0
            hour += 1
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT time_slot FROM bookings WHERE date=?", (date,))
    booked_slots = [slot[0].strip() for slot in cursor.fetchall()]  # Strip leading and trailing spaces
    
    # Remove booked slots from available slots
    available_slots = [slot for slot in available_slots if slot not in booked_slots]

    conn.close()
    
    return available_slots


@app.route('/checkdate')
def check_date():
    date = request.args.get('date')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if the date exists in the bookings table
    cursor.execute("SELECT time_slot FROM bookings WHERE date=?", (date,))
    booked_slots = [slot[0] for slot in cursor.fetchall()]

    available_slots = get_available_slots(date)
    
    response = f"{', '.join(available_slots)}"

    conn.close()

    return response




# Route to book an appointment
@app.route('/bookappointment', methods=['POST'])
def book_appointment():
    name = request.form['name']
    phone = request.form['phone']
    date = request.form['date']
    time_slot = request.form['time_slot']
    print(name, phone,date,time_slot)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (name, phone, date, time_slot) VALUES (?, ?, ?, ?)", (name, phone, date, time_slot))
    conn.commit()
    conn.close()

    return f'Appointment booked successfully! Reach on time {time_slot}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            # Set 'logged_in' session variable to True
            session['logged_in'] = True
            # Redirect to admin dashboard if login successful
            return redirect(url_for('admin_dashboard'))
        else:
            # Redirect back to login page with error message
            return render_template('login.html', error=True)
    # If GET request or login unsuccessful, render login page
    return render_template('login.html', error=False)

def fetch_bookings():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()
    conn.close()
    return bookings

@app.route('/admin')
def admin_dashboard():
    if session.get('logged_in'):
        bookings = fetch_bookings()
        return render_template('admin.html', bookings=bookings)
    else:
        return redirect(url_for('login'))

@app.route('/salesman', methods=['GET','POST'])
def salesman():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        product = request.form['product']
        
        # Insert data into the 'salesman' table
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO salesman (name, phone, product) VALUES (?, ?, ?)", (name, phone, product))
        conn.commit()
        conn.close()
        flash("Thank You, Your data has been submitted successfully. You will be contacted within a few days.", "success")

    return render_template('salesman.html')

@app.route('/details', methods=['GET'])
def get_salesman_details():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('example.db')  # Change 'your_database_name.db' to your actual database name
        cursor = conn.cursor()

        # Fetch all the details from the 'salesman' table
        cursor.execute('SELECT * FROM salesman')
        salesman_details = cursor.fetchall()

        # Convert the data to a list of dictionaries
        details_list = []
        for detail in salesman_details:
            detail_dict = {
                'id': detail[0],
                'name': detail[1],
                'phone': detail[2],
                'product_description': detail[3]
            }
            details_list.append(detail_dict)

        # Close the database connection
        conn.close()

        # Return the data in JSON format
        return jsonify(details_list)

    except sqlite3.Error as e:
        return jsonify({'error': str(e)})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_table()
    app.run(debug=True,host="0.0.0.0")
