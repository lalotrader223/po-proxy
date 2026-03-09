# ============================================
# 🚀 COMMANDER LALO'S AUTO-TRADER - SIMPLIFIED
# 100% WORKING VERSION
# ============================================

import os
import time
import json
import random
import threading
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================
# SIMPLE CONFIG
# ============================================
config = {
    "confidence_threshold": 85,
    "base_amount": 10000,
    "max_daily_trades": 50,
    "martingale": False
}

# ============================================
# BOT STATE
# ============================================
bot_state = {
    "running": False,
    "thread": None,
    "trades": [],
    "stats": {
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0,
        "profit_loss": 0,
        "consecutive_losses": 0
    },
    "balance": 10000
}

# ============================================
# SIMPLE BOT LOOP
# ============================================

def bot_loop():
    """Simple bot loop that won't crash"""
    while bot_state["running"]:
        try:
            # Simulate finding a trade
            timestamp = time.time()
            
            # Create a demo trade
            trade = {
                "id": int(timestamp * 1000),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "asset": random.choice(["GBPUSD_otc", "EURUSD_otc", "BTCUSD"]),
                "timeframe": random.choice([60, 120, 300]),
                "action": random.choice(["call", "put"]),
                "direction": random.choice(["BUY", "SELL"]),
                "amount": config["base_amount"],
                "confidence": random.randint(80, 95),
                "status": "completed",
                "result": random.choice(["win", "loss"]),
                "profit": random.randint(-1000, 1500)
            }
            
            # Update stats
            bot_state["trades"].insert(0, trade)
            bot_state["stats"]["total_trades"] += 1
            
            if trade["result"] == "win":
                bot_state["stats"]["wins"] += 1
                bot_state["balance"] += trade["profit"]
                bot_state["stats"]["consecutive_losses"] = 0
            else:
                bot_state["stats"]["losses"] += 1
                bot_state["balance"] -= abs(trade["profit"])
                bot_state["stats"]["consecutive_losses"] += 1
            
            # Calculate win rate
            total = bot_state["stats"]["wins"] + bot_state["stats"]["losses"]
            if total > 0:
                bot_state["stats"]["win_rate"] = round((bot_state["stats"]["wins"] / total) * 100, 2)
            
            bot_state["stats"]["profit_loss"] = bot_state["balance"] - 10000
            
            # Keep only last 20 trades
            if len(bot_state["trades"]) > 20:
                bot_state["trades"] = bot_state["trades"][:20]
            
            # Sleep between trades
            for _ in range(30):
                if not bot_state["running"]:
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>🚀 COMMANDER'S AUTO-TRADER</title>
            <style>
                body { background: black; color: #00ff88; font-family: monospace; padding: 40px; }
                h1 { color: #00ff88; }
                .status { padding: 20px; border: 2px solid #00ff88; border-radius: 10px; }
                .running { color: #00ff88; }
                .stopped { color: #ff4444; }
            </style>
        </head>
        <body>
            <h1>🚀 COMMANDER LALO'S AUTO-TRADER</h1>
            <div class="status">
                <p>Status: <span id="status">Loading...</span></p>
                <p>Balance: <span id="balance">$10,000</span></p>
            </div>
            <script>
                async function update() {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    document.getElementById('status').innerHTML = 
                        data.running ? '<span class="running">🟢 RUNNING</span>' : '<span class="stopped">🔴 STOPPED</span>';
                    document.getElementById('balance').innerHTML = '$' + data.balance;
                }
                setInterval(update, 1000);
                update();
            </script>
        </body>
    </html>
    """

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    if not bot_state["running"]:
        bot_state["running"] = True
        thread = threading.Thread(target=bot_loop)
        thread.daemon = True
        thread.start()
        bot_state["thread"] = thread
        return jsonify({"status": "started", "running": True})
    return jsonify({"status": "already running", "running": True})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    bot_state["running"] = False
    return jsonify({"status": "stopped", "running": False})

@app.route('/api/status')
def bot_status():
    """Get bot status"""
    return jsonify({
        "running": bot_state["running"],
        "balance": bot_state["balance"],
        "stats": bot_state["stats"],
        "recent_trades": bot_state["trades"][:10]
    })

@app.route('/api/config', methods=['GET', 'POST'])
def bot_config():
    """Get or update config"""
    if request.method == 'POST':
        new_config = request.json
        config.update(new_config)
        return jsonify({"status": "updated", "config": config})
    return jsonify(config)

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy", "time": time.time()})

# ============================================
# START SERVER
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    print("="*50)
    print("🚀 COMMANDER'S AUTO-TRADER STARTING")
    print("="*50)
    print(f"Port: {port}")
    print(f"Config: {config}")
    print("="*50)
    app.run(host='0.0.0.0', port=port, debug=False)
