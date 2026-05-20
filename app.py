from flask import Flask, request, jsonify, render_template
from datetime import datetime
import pymongo

app = Flask(__name__)

# Kopyaladığın linki buraya yapıştır. <username> ve <password> kısımlarını kendi belirlediklerinle değiştir!
MONGO_URI = "mongodb+srv://kullanici_adin:SIFREN@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.lennebraha38_db
    kullanicilar_tablosu = db.users
    hareket_kayitlari_tablosu = db.logs
    print("MongoDB Atlas bağlantısı başarılı!")
except Exception as e:
    print(f"Veritabanı bağlantı hatası: {e}")

@app.route('/')
def index():
    # Şablon klasöründeki index.html dosyanı render eder
    return render_template('index.html')

# 1. HAREKETLERİ İŞLEM ALTINA ALMA (LOG) API'Sİ
@app.route('/api/log-ekle', methods=['POST'])
def log_ekle():
    try:
        veri = request.json
        kullanici_id = veri.get('userId', 'Anonim')
        yapilan_islem = veri.get('islem')  # Örn: "Giriş Yapıldı", "Profil Güncellendi"
        detay = veri.get('detay', '')
        
        log_verisi = {
            "userId": kullanici_id,
            "islem": yapilan_islem,
            "detay": detay,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        hareket_kayitlari_tablosu.insert_one(log_verisi)
        return jsonify({"durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": str(e)}), 500

# 2. KULLANICI PROFİLİNİ BULUTA KAYDETME API'Sİ
# KULLANICI PROFİLİNİ BULUTA KAYDETME API'Sİ (MongoDB Atlas İçin)
@app.route('/api/profil-kaydet', methods=['POST'])
def profil_kaydet():
    try:
        veri = request.json
        kullanici_id = veri.get('userId')
        profil_data = veri.get('profil') # JavaScript'ten gelen profilPaketi
        
        # Kullanıcının profil bilgilerini MongoDB'deki 'users' tablosunda güncelle veya oluştur
        kullanicilar_tablosu.update_one(
            {"userId": kullanici_id},
            {"$set": profil_data},
            upsert=True
        )
        
        # Profil güncellendiğinde bunu otomatik olarak hareket kayıtlarına (logs) işleyelim
        hareket_kayitlari_tablosu.insert_one({
            "userId": kullanici_id,
            "islem": "Profil Güncelleme",
            "detay": f"{profil_data.get('ad')} {profil_data.get('soyad')} profil bilgilerini güncelledi.",
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return jsonify({"durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": str(e)}), 500
