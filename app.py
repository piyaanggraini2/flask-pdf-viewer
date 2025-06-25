
from flask import Flask, render_template, request, redirect, session, send_file
from functools import wraps
import random
import string

app = Flask(__name__)
app.secret_key = 'rahasia-super-aman'

# Fungsi pembuat kode acak
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Middleware login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '123':
            session['logged_in'] = True
            return redirect('/viewer/soal1')
        return 'Login gagal!'
    return render_template('login.html')

# Viewer dinamis untuk dokumen
@app.route('/viewer/<doc>')
@login_required
def viewer(doc):
    if session.get(f'reauth_{doc}', False):
        return redirect(f'/reauth/{doc}')
    return render_template('viewer.html', doc=doc)

# Reauth untuk dokumen
@app.route('/reauth/<doc>', methods=['GET', 'POST'])
def reauth(doc):
    if request.method == 'POST':
        input_code = request.form['code']
        if input_code == session.get(f'reauth_code_{doc}'):
            session[f'reauth_{doc}'] = False
            return redirect(f'/viewer/{doc}')
        return 'Kode salah!'
    return render_template('reauth.html', doc=doc)

# Force reauth saat user keluar dari halaman
@app.route('/force_reauth/<doc>')
def force_reauth(doc):
    session[f'exit_count_{doc}'] = session.get(f'exit_count_{doc}', 0) + 1
    session[f'reauth_{doc}'] = True

    if session[f'exit_count_{doc}'] > 1:
        session[f'reauth_code_{doc}'] = generate_code()
    else:
        session[f'reauth_code_{doc}'] = 'KODE123'

    print(f"[DEBUG] Kode untuk {doc}: {session[f'reauth_code_{doc}']}")
    return '', 204

# Menyajikan file PDF
@app.route('/pdf/<doc>')
@login_required
def serve_pdf(doc):
    try:
        return send_file(f'protected/{doc}.pdf')
    except FileNotFoundError:
        return 'Dokumen tidak ditemukan', 404

# Jalankan server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
