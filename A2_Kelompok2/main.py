import eel
import socket
import threading
import sys
import mysql.connector
import hashlib
import time
import json

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Global variables
CONN = None
IS_HOST = False
CLIENTS = [] 
CURRENT_USER = None
BROADCAST_PORT = 55555
STOP_THREADS = False

# --- DATABASE SETUP ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Discord"
}

def init_db():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    cursor.close()
    conn.close()

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(191) PRIMARY KEY,
            password_hash CHAR(64) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    cursor.close()
    conn.close()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

eel.init('web')
init_db()

# --- DISCOVERY SYSTEM (UDP) ---

def broadcast_presence(group_name, tcp_port):
    """Host runs this to shout 'I am here' to the network."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    message = json.dumps({
        "name": group_name,
        "port": tcp_port,
        "host_user": CURRENT_USER
    }).encode('utf-8')
    
    while not STOP_THREADS and IS_HOST:
        try:
            # Broadcast to 255.255.255.255 (everyone on LAN)
            udp.sendto(message, ('<broadcast>', BROADCAST_PORT))
            time.sleep(2)
        except Exception as e:
            print(f"Broadcast error: {e}")
            time.sleep(5)
    udp.close()

def scan_for_groups():
    """Joiner runs this to listen for hosts."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Bind to the broadcast port to listen
        udp.bind(('0.0.0.0', BROADCAST_PORT))
        udp.settimeout(3) # Don't block forever
    except Exception as e:
        print(f"Scanner bind error: {e}")
        return

    known_groups = set() # To avoid duplicates in UI

    while not STOP_THREADS and not IS_HOST:
        try:
            data, addr = udp.recvfrom(1024)
            info = json.loads(data.decode('utf-8'))
            host_ip = addr[0]
            
            # Unique ID for the group
            group_id = f"{host_ip}:{info['port']}"
            
            if group_id not in known_groups:
                known_groups.add(group_id)
                # Send to UI
                eel.ui_add_group(info['name'], info['host_user'], host_ip, info['port'])
                
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Scan error: {e}")
            break
    udp.close()

@eel.expose
def start_scanning():
    """Called by JS when user opens the Join tab."""
    global STOP_THREADS
    STOP_THREADS = False
    threading.Thread(target=scan_for_groups, daemon=True).start()

# --- AUTH FUNCTIONS ---

@eel.expose
def register_user(username, password):
    if not username or not password:
        return "Username and password required."

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hash_pass(password))
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return "Username already taken."
    except Exception as e:
        return f"Error: {e}"
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

@eel.expose
def login_user(username, password):
    global CURRENT_USER
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM users WHERE username=%s",
            (username,)
        )
        row = cursor.fetchone()
    except Exception:
        row = None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    if row and row[0] == hash_pass(password):
        CURRENT_USER = username
        return True

    return "Invalid username or password."

# --- NETWORKING FUNCTIONS ---

def receive_loop(connection):
    buffer = ""
    while True:
        try:
            chunk = connection.recv(4096 * 4) 
            if not chunk: break
            buffer += chunk.decode('utf-8', errors='ignore')
            while "<EOF>" in buffer:
                message_payload, buffer = buffer.split("<EOF>", 1)
                parts = message_payload.split("|", 3)
                if len(parts) >= 4:
                    sender, msg_type, filename, content = parts
                    eel.js_receive_message(sender, msg_type, filename, content)
                    if IS_HOST: broadcast(message_payload + "<EOF>", connection)
        except Exception as e:
            break

def broadcast(raw_message, sender_conn):
    for client in CLIENTS:
        if client != sender_conn:
            try: client.send(raw_message.encode('utf-8'))
            except: CLIENTS.remove(client)

@eel.expose
def host_chat(group_name):
    global CONN, IS_HOST, CURRENT_USER, STOP_THREADS
    if not CURRENT_USER: return "Not logged in"
    IS_HOST = True
    STOP_THREADS = False # Reset flag
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 0))
        actual_port = server.getsockname()[1]
        server.listen(5)
        
        # Start Beacon in background
        threading.Thread(target=broadcast_presence, args=(group_name, actual_port), daemon=True).start()
        
        def accept_clients():
            while True:
                client_sock, addr = server.accept()
                CLIENTS.append(client_sock)
                threading.Thread(target=receive_loop, args=(client_sock,), daemon=True).start()
                eel.js_receive_message("System", "text", "", f"Client connected from {addr[0]}")

        threading.Thread(target=accept_clients, daemon=True).start()
        return True
    except Exception as e:
        return f"Error: {str(e)}"

@eel.expose
def join_chat(ip, port):
    global CONN, IS_HOST, STOP_THREADS
    IS_HOST = False
    STOP_THREADS = True # Stop scanning
    try:
        CONN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CONN.connect((ip, int(port)))
        threading.Thread(target=receive_loop, args=(CONN,), daemon=True).start()
        return True
    except Exception as e:
        return f"Error: {str(e)}"

@eel.expose
def send_data_py(msg_type, filename, content, username):
    payload = f"{username}|{msg_type}|{filename}|{content}<EOF>"
    try:
        if IS_HOST: 
            broadcast(payload, None)
            eel.js_receive_message(username, msg_type, filename, content)
        elif CONN: CONN.send(payload.encode('utf-8'))
    except Exception as e: pass

@eel.expose
def trigger_notification(sender, message):
    if HAS_PLYER:
        try: notification.notify(title=f"New from {sender}", message=message, app_name='Eel Chat', timeout=3)
        except: pass

if __name__ == '__main__':
    try: eel.start('index.html', size=(1000, 750), port=0)
    except (SystemExit, KeyboardInterrupt): sys.exit(0)