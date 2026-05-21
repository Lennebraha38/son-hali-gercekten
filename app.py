import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

app = Flask(__name__)

# SQLAlchemy entegrasyonu
# Önemli: Neon adresi 'postgres://' ile başlar ancak SQLAlchemy modern sürümlerinde 'postgresql://' ister.
# Bu yüzden adresi koda alırken küçük bir düzeltme yapıyoruz.
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URL'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Örnek Model (Tablo Yapısı)
class Kullanici(db.Model):
    __tablename__ = 'kullanicilar'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(80), nullable=False)
    eposta = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Kullanici {self.isim}>'

# Tabloları Neon üzerinde otomatik oluşturmak için (İlk çalıştırmada bir kez gerekir)
with app.app_context():
    db.create_all()

@app.route('/')
def ana_sayfa():
    return "Neon Veritabanı Bağlantısı Başarılı!"

if __name__ == '__main__':
    app.run(debug=True)
