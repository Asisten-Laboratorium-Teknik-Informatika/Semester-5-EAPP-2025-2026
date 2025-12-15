import eel
from database import (
    connect,
    add_user,
    get_all_movies,
    get_seats,
    book_multiple_seats,
    add_transaction,
    get_user_tickets,
)
from auth import check_login, get_user, register_user
from fpdf import FPDF
import random
import string
import os
import datetime
import pymysql # pyright: ignore[reportMissingModuleSource]
from pymysql.cursors import DictCursor # pyright: ignore[reportMissingModuleSource]

# ----------------------
# SETUP
# ----------------------
eel.init('web')
os.makedirs('web/reports', exist_ok=True)
user_session = {}

# ----------------------
# KONVERSI KE PYMYSQL
# ----------------------
def connect():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="cinema_db",
        cursorclass=DictCursor
    )

pymysql.install_as_MySQLdb()


# ----------------------
# AUTH
# ----------------------
@eel.expose
def login(username, password):
    role = check_login(username, password)
    if role:
        user = get_user(username)
        user_session['user_id'] = user['id']
        user_session['role'] = role
        return role
    return None

@eel.expose
def get_user_id():
    return user_session.get('user_id')

@eel.expose
def register(username, password):
    return register_user(username, password)

# ----------------------
# MOVIES & SCHEDULES
# ----------------------
@eel.expose
def get_movies():
    return get_all_movies()

@eel.expose
def get_schedule(movie_id):
    print("get_schedule dipanggil dengan movie_id:", movie_id)
    from database import get_schedule as db_schedule
    result = db_schedule(int(movie_id))
    print("jadwal dari DB:", result)
    return result

@eel.expose
def get_seats(schedule_id):
    from database import get_seats as db_get_seats
    return db_get_seats(int(schedule_id))

# ----------------------
# BOOKING
# ----------------------
@eel.expose
def save_booking(booking_data):

    user_id = user_session.get('user_id')
    if not user_id:
        return {'success': False, 'message': 'Login dulu!'}

    schedule_id = int(booking_data.get('schedule_id', 0))
    seats_list = booking_data.get('seats', []) or []

    try:
        total_from_js = float(booking_data.get('total', 0))
    except:
        total_from_js = 0

    if not seats_list or schedule_id == 0:
        return {'success': False, 'message': 'Seats atau jadwal tidak valid!'}

    price_per_seat = 42000
    expected_total = len(seats_list) * price_per_seat

    if int(total_from_js) != int(expected_total):
        return {'success': False, 'message': f'Total harus Rp {expected_total}'}

    booking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    seats_str = ",".join(seats_list)

    # Save transaction
    if not add_transaction(user_id, schedule_id, expected_total, booking_code, seats_str):
        return {
            'success': False,
            'message': 'Gagal menyimpan transaksi! Kursi mungkin sudah dibooking.'
        }

    # Update seats
    db = connect()
    try:
        cur = db.cursor()
        for seat in seats_list:
            cur.execute("""
                UPDATE seats 
                SET is_booked = 1 
                WHERE schedule_id = %s AND seat_number = %s
            """, (schedule_id, seat))
        db.commit()
    except Exception as e:
        print("Seat update error:", e)
    finally:
        db.close()

    # Ambil detail film
    db = connect()
    detail = {'title': 'Unknown', 'day': 'Unknown', 'show_time': 'Unknown'}

    cur = db.cursor()
    cur.execute("""
        SELECT m.title, s.day, s.show_time
        FROM schedules s
        JOIN movies m ON s.movie_id = m.id
        WHERE s.id = %s
    """, (schedule_id,))
    row = cur.fetchone()

    if row:
        detail = row

    cur.close()
    db.close()

    # PDF
    pdf_file = generate_ticket(booking_code, seats_list, detail, expected_total)

    return {
        'success': True,
        'booking_code': booking_code,
        'total': expected_total,
        'pdf': pdf_file,
        'film_title': detail['title'],
        'hari': detail['day'],
        'jam': detail['show_time']
    }

# ----------------------
# GENERATE PDF
# ----------------------
@eel.expose
def generate_ticket(booking_code, seats_list, detail, total_price):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="E-Ticket PoMovi", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Kode: {booking_code}", ln=True)
    pdf.cell(200, 10, txt=f"Film: {detail['title']}", ln=True)
    pdf.cell(200, 10, txt=f"Hari: {detail['day']}", ln=True)
    pdf.cell(200, 10, txt=f"Jam: {detail['show_time']}", ln=True)
    pdf.cell(200, 10, txt=f"Kursi: {', '.join(seats_list)}", ln=True)
    pdf.cell(200, 10, txt=f"Total: Rp {total_price}", ln=True)

    filename = f"web/reports/{booking_code}.pdf"
    pdf.output(filename)
    return filename

# ----------------------
# GET TICKET DETAILS
# ----------------------
@eel.expose
def get_ticket_details(booking_code):
    db = connect()
    cur = db.cursor()

    cur.execute("""
        SELECT t.*, m.title, m.duration, s.day, s.show_time, t.total_price
        FROM transactions t
        JOIN schedules s ON t.schedule_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE t.booking_code = %s
    """, (booking_code,))

    ticket = cur.fetchone()
    cur.close()
    db.close()

    if not ticket:
        return {"error": "Tiket tidak ditemukan"}

    seats = ticket.get("seats", "")
    ticket["seats_list"] = seats.split(",") if seats else []

    show_time = ticket.get("show_time")
    if show_time and not isinstance(show_time, str):
        try:
            ticket["show_time"] = show_time.strftime('%H:%M')
        except:
            ticket["show_time"] = str(show_time)
    elif not show_time:
        ticket["show_time"] = "-"

    ticket["total"] = float(ticket.get("total_price", 0))

    return ticket


# ----------------------
# START APP
# ----------------------
eel.start('login.html', size=(900, 600), port=0)