import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- GÜVENLİK VE VERİTABANI AYARLARI ---
# Oturum işlemleri ve hata mesajları (flash) için gizli anahtar
app.config['SECRET_KEY'] = 'teknofest_api_projem_2026'

# Veritabanının Render'da silinmesini önlemek için kalıcı dosya yolu oluşturur
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'veritabani.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- VERİTABANI MODELİ (TABLOSU) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # Şifreler hash'lenerek saklanacak

# --- SAYFA YÖNLENDİRMELERİ VE LOGIC ---

# 1. Ana Sayfa (Giriş veya Panel Görünümü)
@app.route('/')
def index():
    if 'logged_in' in session:
        return f"Hoş geldiniz, {session['username']}! Başarıyla giriş yaptınız. <a href='/logout'>Çıkış Yap</a>"
    return redirect(url_for('login_page'))

# 2. Giriş Sayfasını Gösterme (GET) ve Giriş Yapma İşlemi (POST)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Veritabanında bu kullanıcıyı ara
        user = User.query.filter_by(username=username).first()
        
        # Kullanıcı varsa ve şifresi doğruysa içeri al
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return "Kullanıcı adı veya şifre yanlış!", 401
            
    # Eğer GET isteği gelirse senin o meşhur giriş HTML'ini ekrana basar
    # Not: Giriş HTML dosyanın adını buraya tam yazmalısın (örn: 'login.html' veya 'index.html')
    return render_template('login.html') 

# 3. Kayıt Olma İşlemi (POST)
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return "Kullanıcı adı ve şifre boş bırakılamaz!", 400
        
    # Kullanıcı adı daha önce alınmış mı kontrol et
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        return "Bu kullanıcı adı zaten sistemde kayıtlı!", 400
        
    # Şifreyi kırılması imkansız güvenli bir koda (hash) dönüştür
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Yeni kullanıcıyı veritabanına ekle
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return "Kayıt başarılı! Şimdi giriş yapabilirsiniz.", 201

# 4. Çıkış Yapma İşlemi
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- UYGULAMAYI BAŞLATMA VE OTOMATİK SİGORTA ---
if __name__ == '__main__':
    # Kod canlıya çıktığında veya yerelde çalıştığında veritabanı dosyası yoksa otomatik sıfırdan oluşturur
    with app.app_context():
        db.create_all()
        
    # Hem bilgisayardan hem telefondan erişim için host 0.0.0.0 ayarlı
    app.run(host='0.0.0.0', port=5000, debug=True)
