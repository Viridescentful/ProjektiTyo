from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/vastaus')
def vastausfunktio(): #127.0.0.1:5000/vastaus
    vastaus = {
        "Teksti": "Hello, World!",
    }

    return vastaus

if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)