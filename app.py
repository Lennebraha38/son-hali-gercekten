import os
import sys
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 1. Loglama Yapılandırması (Render üzerinde tüm detayları görmek için zorunludur)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# .env dosyasını yükle (Lokalde çalışırken gerekli, Render'da Environment kısmından okur)
load_dotenv()

app = Flask(__name__)

try:
    logging.info("Veritabanı bağlantısı başlatılıyor...")
    uri = os.getenv("DATABASE_URL")
    
    # Render loglarında adresin gelip gelmediğini şifreni gizleyerek kontrol edelim
    if uri:
        logging.info(f"DEBUG: DATABASE_URL bulundu (Karakter Sayısı: {len(uri)})")
    else:
        logging.error("KRİTİK HATA: DATABASE_URL çevre değişkeni boş veya bulunamadı!")
        raise ValueError("DATABASE_URL bulunamadı! Lütfen Render panelinden Environment Ayarlarını kontrol edin.")

    # SQLAlchemy modern PostgreSQL sürücü ismi düzeltmesi (postgres:// -> postgresql://)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    # Flask-SQLAlchemy Yapılandırması
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Veritabanı motorunu bağla
    db = SQLAlchemy(app)
    logging.info("SQLAlchemy başarıyla başlatıldı.")

except Exception as e:
    logging.exception("Uygulama başlatılırken kritik veritabanı hatası meydana geldi!")
    raise e

# 2. Örnek Model / Tablo Yapısı
class Kullanici(db.Model):
    __tablename__ = 'kullanicilar'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(80), nullable=False)
    eposta = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "isim": self.isim, "eposta": self.eposta}

# Tabloları Neon üzerinde otomatik oluştur (Yoksa yaratır)
with app.app_context():
    try:
        db.create_all()
        logging.info("Veritabanı tabloları kontrol edildi/oluşturuldu.")
    except Exception as e:
        logging.exception("Tablo oluşturma aşamasında hata!")

# 3. Örnek API Endpoint'leri
@app.route('/')
def ana_sayfa():
    logging.info("Ana sayfa ziyaret edildi.")
    return jsonify({"durum": "basarili", "mesaj": "Neon ve Flask Bağlantısı Aktif!"})

@app.route('/kullanici-ekle', methods=['POST'])
def kullanici_ekle():
    veri = request.get_json()
    if not veri or 'isim' not in veri or 'eposta' not in veri:
        return jsonify({"hata": "Eksik veri"}), 400
        
    try:
        yeni_kullanici = Kullanici(isim=veri['isim'], eposta=veri['eposta'])
        db.session.add(yeni_kullanici)
        db.session.commit()
        return jsonify({"durum": "basarili", "kullanici": yeni_kullanici.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Kullanıcı eklenirken hata: {str(e)}")
        return jsonify({"hata": "Veritabanı işlemi başarısız"}), 500

# Gunicorn doğrudan 'app' nesnesini çalıştırır, bu blok yerel testler içindir
if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
