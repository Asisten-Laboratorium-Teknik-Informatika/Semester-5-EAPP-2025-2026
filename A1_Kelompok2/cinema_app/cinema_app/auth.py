from database import get_user, add_user
def check_login(username, password):
    user = get_user(username)
    if user and user['password'] == password:
        print(f"Login sukses untuk {username}, role: {user['role']}") # Debug
        return user['role']
    print(f"Login gagal untuk {username}") # Debug
    return None
def register_user(username, password):
    print(f"Register attempt: {username}") # Debug
    if get_user(username):
        print(f"Username {username} sudah ada!") # Debug
        return {'success': False, 'message': 'Username sudah ada!'}
    if add_user(username, password):
        print(f"Register sukses: {username}") # Debug
        return {'success': True, 'message': 'Registrasi berhasil! Silakan login.'}
    else:
        print(f"Register gagal di DB untuk {username}") # Debug
        return {'success': False, 'message': 'Gagal registrasi. Coba lagi.'}