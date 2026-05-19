import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Klasör yollarını Linux sunucusuna %100 uyumlu hale getiren kesin çözüm
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
# Veritabanının silinmesini engellemek için kalıcı bir dosya yolu oluşturur
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'veritabani.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'teknofest_gizli_anahtar_2026' # Güvenli oturumlar için

db = SQLAlchemy(app)

@app.route('/')
def home():
    # Flask zaten templates klasörünün içine bakar. 
    # Buraya ASLA 'templates\\index.html' veya '\\' yazma. Sadece dosya adı:
    return render_template('index.html')

# Yerel bilgisayar için (Render bunu otomatik ezebilir ama hata vermez)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
