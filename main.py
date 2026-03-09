from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import random
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "⚡ COMMANDER PROXY IS LIVE ⚡"

@app.route('/api/signals')
def get_signals():
    asset = request.args.get('asset', 'GBPUSD_otc')
    timeframe = request.args.get('timeframe', '60')
    
    # Generate signals
    signals = []
    for i in range(5):
        confidence = random.randint(65, 95)
        action = 'call' if random.random() > 0.4 else 'put'
        
        signals.append({
            'asset': asset,
            'timeframe': timeframe,
            'action': action,
            'confidence': confidence,
            'price': round(1.2500 + random.random() * 0.01, 5)
        })
    
    return jsonify({'signals': signals})

@app.route('/api/analyze')
def analyze():
    timeframe = request.args.get('timeframe', '60')
    
    rsi = random.randint(30, 70)
    if rsi < 35:
        action = 'BUY'
        confidence = random.randint(75, 95)
    elif rsi > 65:
        action = 'SELL'
        confidence = random.randint(75, 95)
    else:
        action = 'NEUTRAL'
        confidence = random.randint(40, 60)
    
    return jsonify({
        'action': action,
        'confidence': confidence,
        'rsi': rsi,
        'timeframe': timeframe
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
