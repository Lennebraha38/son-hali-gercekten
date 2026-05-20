import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teknofest_api_projem_2026'

# --- GEÇİCİ BELLEK (Veritabanı yerine verileri burada tutuyoruz) ---
# Sunucu açık olduğu sürece veriler burada saklanır
SAHTE_VERITABANI_USERS = {
    # Test etmen için örnek bir kullanıcı bırakıyorum:
    # Kullanıcı adı: faruk , Şifre: 123456
    "faruk": generate_password_hash("123456", method='pbkdf2:sha256')
}
SAHTE_VERITABANI_LOGS = []

# --- HER HAREKETİ OTOMATİK KAYDETME FONKSİYONU ---
@app.before_request
def log_every_action():
    if request.endpoint and 'static' not in request.endpoint:
        aktif_user = session.get('username', 'Giriş Yapılmamış Ziyaretçi')
        sayfa = f"Sayfa İstendi: {request.path} [{request.method}]"
        
        yeni_log = {
            "ip_address": request.remote_addr,
            "username": aktif_user,
            "action": sayfa,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        SAHTE_VERITABANI_LOGS.append(yeni_log)

# --- SİTE ROTASI (GİRİŞ - ÇIKIŞ - KAYIT) ---

@app.route('/')
def index():
    if 'logged_in' in session:
        return f"""
        <h1>Sistem Başarıyla Çalışıyor, Faruk!</h1>
        <p>Hoş geldiniz, {session['username']}!</p>
        <p>Şu an veritabanı olmadan, belleğe kayıt yapılıyor.</p>
        <br>
        <a href='/logs'>Sistem Loglarını Gör (Yaptığın Hareketler)</a> | 
        <a href='/logout'>Sistemden Çıkış Yap</a>
        """
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Bellekte kullanıcı var mı kontrol et
        hashed_password = SAHTE_VERITABANI_USERS.get(username)
        
        if hashed_password and check_password_hash(hashed_password, password):
            session['logged_in'] = True
            session['username'] = username
            
            # Başarılı girişi logla
            SAHTE_VERITABANI_LOGS.append({
                "ip_address": request.remote_addr,
                "username": username,
                "action": "Başarılı Giriş Yaptı",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return redirect(url_for('index'))
        else:
            return "Kullanıcı adı veya şifre yanlış!", 401
            
    try: return render_template('index.html')
    except: return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password: 
        return "Boş bırakılamaz!", 400
        
    if username in SAHTE_VERITABANI_USERS:
        return "Bu kullanıcı adı zaten alınmış!", 400
        
    # Kullanıcıyı belleğe kaydet
    SAHTE_VERITABANI_USERS[username] = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Log kaydı ekle
    SAHTE_VERITABANI_LOGS.append({
        "ip_address": request.remote_addr,
        "username": username,
        "action": "Yeni Hesap Oluşturdu",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return "Kayıt başarılı! Şimdi giriş yapabilirsiniz.", 201

# --- LOGLARI İZLEME SAYFASI ---
@app.route('/logs')
def show_logs():
    if 'logged_in' not in session:
        return redirect(url_for('login_page'))
        
    log_satirlari = ""
    for log in reversed(SAHTE_VERITABANI_LOGS):
        log_satirlari += f"<li>[{log['timestamp']}] IP: {log['ip_address']} | Kullanıcı: {log['username']} | Eylem: {log['action']}</li>"
        
    return f"""
    <h1>Sistem Hareket Logları</h1>
    <a href='/'>Ana Sayfaya Dön</a>
    <hr>
    <ul>
        {log_satirlari}
    </ul>
    """

@app.route('/logout')
def logout():
    if 'username' in session:
        SAHTE_VERITABANI_LOGS.append({
            "ip_address": request.remote_addr,
            "username": session['username'],
            "action": "Sistemden Çıkış Yaptı",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
