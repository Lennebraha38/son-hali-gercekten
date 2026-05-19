import os
from flask import Flask, render_template, jsonify

# Klasör yollarını Linux sunucusuna %100 uyumlu hale getiren kesin çözüm
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

@app.route('/')
def home():
    # Flask zaten templates klasörünün içine bakar. 
    # Buraya ASLA 'templates\\index.html' veya '\\' yazma. Sadece dosya adı:
    return render_template('index.html')

# Yerel bilgisayar için (Render bunu otomatik ezebilir ama hata vermez)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
