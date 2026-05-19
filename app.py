import os
import sys
from flask import Flask, render_template, jsonify
import requests

# Bu akıllı satır, USB hangi harfi alırsa alsın (D, E, F) kendi yerini otomatik bulur:
ana_klasor = os.path.dirname(os.path.abspath(sys.argv[0]))
templates_konumu = os.path.join(ana_klasor, 'templates')

app = Flask(__name__, template_folder=templates_konumu)

# Güvenli API Bilgileri
API_KEY = "deneme_anahtari_xyz123"
API_BASE_URL = "https://httpbin.org/get"

@app.route('/')
def ana_sayfa():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <h3>Klasör Bulunamadı!</h3> 
        Python şu konuma bakıyor:<br>
        <code>{templates_konumu}\index.html</code><br><br>
        <strong>Lütfen Kontrol Edin:</strong><br>
        Sitenizin adının tam olarak <code>index.html</code> olduğundan ve <code>templates</code> klasörünün içinde durduğundan emin olun.
        """

@app.route('/api/veri-getir', methods=['GET'])
def veri_getir():
    try:
        parametreler = {
            "api_key": API_KEY,
            "status": "active"
        }
        response = requests.get(API_BASE_URL, params=parametreler, timeout=10)
        veri = response.json()
        
        return f"""
        <html>
            <head><title>API Sonuç Ekranı</title></head>
            <body style="font-family: sans-serif; padding: 40px; background: #f4f4f9;">
                <div style="max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #28a745; margin-top: 0;">✔ API Verileri Başarıyla Çekildi!</h2>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <h4>Gelen Veri (JSON):</h4>
                    <pre style="background: #e9ecef; padding: 20px; border-left: 5px solid #28a745; border-radius: 4px; font-family: monospace;">{str(veri)}</pre>
                    <br>
                    <a href="/" style="display: inline-block; background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px;">← Siteme Geri Dön</a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return f"<h3>Sistem Hatası!</h3> {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)