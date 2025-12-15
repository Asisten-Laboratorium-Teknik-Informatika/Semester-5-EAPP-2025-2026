import pymysql
from pymysql.cursors import DictCursor

def connect():
    try:
        return pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="cinema_db",
            cursorclass=DictCursor
        )
    except Exception as err:
        print(f"DB Connection Error: {err}")
        return None


# ================== USERS ==================
def get_user(username):
    db = connect()
    if not db:
        return None
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    db.close()
    return user


def add_user(username, password, role="user"):
    db = connect()
    if not db:
        return False
    try:
        cur = db.cursor()
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
        """, (username, password, role))
        db.commit()
        return True
    except Exception as err:
        print(f"Error add_user: {err}")
        return False
    finally:
        db.close()


# ================== MOVIES ==================
def get_all_movies():
    db = connect()
    if not db:
        return []
    cur = db.cursor()
    cur.execute("SELECT * FROM movies")
    data = cur.fetchall()
    db.close()
    return data


# ================== SCHEDULES ==================
def get_schedule(movie_id):
    db = connect()
    if not db:
        return []

    cur = db.cursor()
    cur.execute("""
        SELECT id, movie_id, show_time, day
        FROM schedules 
        WHERE movie_id = %s
        ORDER BY show_time ASC
    """, (movie_id,))

    rows = cur.fetchall()
    cur.close()
    db.close()

    # convert datetime
    for row in rows:
        if not isinstance(row['show_time'], str):
            try:
                row['show_time'] = row['show_time'].strftime('%Y-%m-%d %H:%M:%S')
            except:
                row['show_time'] = str(row['show_time'])

    return rows


# ================== SEATS ==================
def get_seats(schedule_id):
    db = connect()
    if not db:
        return []
    cur = db.cursor()
    cur.execute("""
        SELECT seat_number, is_booked
        FROM seats
        WHERE schedule_id = %s
    """, (schedule_id,))
    data = cur.fetchall()
    cur.close()
    db.close()
    return data


def book_multiple_seats(schedule_id, seats_list):
    db = connect()
    if not db:
        return False
    try:
        cur = db.cursor()

        for seat in seats_list:
            cur.execute("""
                SELECT is_booked FROM seats
                WHERE schedule_id=%s AND seat_number=%s
            """, (schedule_id, seat))
            result = cur.fetchone()

            if result and result['is_booked'] == 1:
                return False

            cur.execute("""
                UPDATE seats SET is_booked=1
                WHERE schedule_id=%s AND seat_number=%s
            """, (schedule_id, seat))

        db.commit()
        return True

    except Exception as err:
        print(f"Error book_multiple_seats: {err}")
        return False

    finally:
        db.close()


# ================== TRANSACTIONS ==================
def add_transaction(user_id, schedule_id, total_price, booking_code, seats):
    db = connect()
    if not db:
        return False
    
    try:
        cur = db.cursor()
        cur.execute("""
            INSERT INTO transactions (user_id, schedule_id, total_price, booking_code, seats)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, schedule_id, total_price, booking_code, seats))
        
        db.commit()
        return True

    except Exception as e:
        print("DB ERROR add_transaction:", e)
        return False

    finally:
        db.close()


# ================== TICKETS ==================
def get_user_tickets(user_id):
    db = connect()
    if not db:
        return []

    cur = db.cursor()
    cur.execute("""
        SELECT t.id, t.booking_code, t.seats, t.total_price, t.created_at,
               m.title, m.duration, s.day, s.show_time
        FROM transactions t
        JOIN schedules s ON t.schedule_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE t.user_id=%s
        ORDER BY t.created_at DESC
    """, (user_id,))

    tickets = cur.fetchall()
    db.close()

    for ticket in tickets:
        ticket["seats_list"] = ticket["seats"].split(",")

    return tickets


# ================== REPORTS ==================
def get_reports():
    db = connect()
    if not db:
        return []

    cur = db.cursor()
    cur.execute("""
        SELECT t.id, u.username, m.title, m.duration, 
               s.show_time, t.seats, t.total_price, 
               t.created_at, t.booking_code
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN schedules s ON t.schedule_id = s.id
        JOIN movies m ON s.movie_id = m.id
        ORDER BY t.created_at DESC
    """)

    result = cur.fetchall()
    db.close()
    return result