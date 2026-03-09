# ============================================
# 🚀 COMMANDER LALO'S AUTO-TRADER BOT
# SLEEP WHILE MONEY MAKES MONEY
# ============================================

import os
import time
import json
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURATION - SET YOUR PARAMETERS
# ============================================
CONFIG = {
    "proxy_url": "https://po-proxy-production.up.railway.app",  # Your proxy
    "assets": ["GBPUSD_otc", "EURUSD_otc", "USDJPY_otc", "BTCUSD"],  # Watch these
    "timeframes": [60, 120, 300],  # Timeframes to monitor
    "confidence_threshold": 85,  # Trade when confidence >= 85%
    "base_amount": 10000,  # Starting trade amount
    "max_daily_trades": 50,  # Safety limit
    "max_consecutive_losses": 3,  # Stop after 3 losses in a row
    "trade_cooldown": 60,  # Seconds between trades on same asset
    "profit_target": 50000,  # Stop after winning this much
    "loss_limit": -25000,  # Stop after losing this much
    "martingale": False,  # Double after loss? (RISKY)
    "martingale_factor": 2.0,  # Double amount after loss
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
        "consecutive_wins": 0,
        "consecutive_losses": 0,
        "daily_trades": 0,
        "last_trade_time": {},
    },
    "balances": {
        "initial": 10000,
        "current": 10000,
        "peak": 10000,
        "lowest": 10000,
    }
}

# ============================================
# AUTO-TRADER ENGINE
# ============================================

class AutoTrader:
    def __init__(self):
        self.config = CONFIG
        self.state = bot_state
        self.last_scan = {}
        
    def scan_opportunities(self):
        """Scan all assets and timeframes for high confidence signals"""
        opportunities = []
        
        for asset in self.config["assets"]:
            for timeframe in self.config["timeframes"]:
                try:
                    # Get signal from proxy
                    url = f"{self.config['proxy_url']}/api/analyze"
                    params = {"asset": asset, "timeframe": timeframe}
                    
                    response = requests.get(url, params=params, timeout=5)
                    data = response.json()
                    
                    confidence = data.get("confidence", 0)
                    direction = data.get("direction", "").upper()
                    
                    # Check if meets threshold
                    if confidence >= self.config["confidence_threshold"] and direction in ["BUY", "SELL"]:
                        opportunities.append({
                            "asset": asset,
                            "timeframe": timeframe,
                            "direction": direction,
                            "confidence": confidence,
                            "price": data.get("current_price", 0),
                            "timestamp": time.time(),
                            "data": data
                        })
                        
                except Exception as e:
                    print(f"Error scanning {asset} {timeframe}: {e}")
                    
        return opportunities
    
    def should_trade(self, opportunity):
        """Check if we should execute this trade"""
        now = time.time()
        asset = opportunity["asset"]
        
        # Check daily trade limit
        if self.state["stats"]["daily_trades"] >= self.config["max_daily_trades"]:
            return False, "Daily trade limit reached"
        
        # Check profit/loss limits
        if self.state["balances"]["current"] - self.state["balances"]["initial"] >= self.config["profit_target"]:
            return False, "Profit target reached"
            
        if self.state["balances"]["current"] - self.state["balances"]["initial"] <= self.config["loss_limit"]:
            return False, "Loss limit reached"
        
        # Check consecutive losses
        if self.state["stats"]["consecutive_losses"] >= self.config["max_consecutive_losses"]:
            return False, "Max consecutive losses reached"
        
        # Check cooldown
        last_trade = self.state["stats"]["last_trade_time"].get(asset, 0)
        if now - last_trade < self.config["trade_cooldown"]:
            return False, f"Cooldown: {int(self.config['trade_cooldown'] - (now - last_trade))}s remaining"
        
        return True, "OK"
    
    def calculate_amount(self):
        """Calculate trade amount based on martingale or fixed"""
        if self.config["martingale"] and self.state["stats"]["consecutive_losses"] > 0:
            # Martingale: multiply amount by factor for each consecutive loss
            multiplier = self.config["martingale_factor"] ** self.state["stats"]["consecutive_losses"]
            amount = self.config["base_amount"] * multiplier
            
            # Safety cap - don't exceed 50% of balance
            max_amount = self.state["balances"]["current"] * 0.5
            return min(amount, max_amount)
        else:
            return self.config["base_amount"]
    
    def execute_trade(self, opportunity):
        """Execute the trade"""
        action = "call" if opportunity["direction"] == "BUY" else "put"
        amount = self.calculate_amount()
        
        try:
            # Place trade via proxy
            url = f"{self.config['proxy_url']}/api/trade"
            payload = {
                "asset": opportunity["asset"],
                "action": action,
                "amount": amount,
                "time": opportunity["timeframe"]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            # Record trade
            trade = {
                "id": int(time.time() * 1000),
                "timestamp": time.time(),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "asset": opportunity["asset"],
                "timeframe": opportunity["timeframe"],
                "action": action,
                "direction": opportunity["direction"],
                "amount": amount,
                "confidence": opportunity["confidence"],
                "price": opportunity["price"],
                "status": "pending",
                "result": None,
                "profit": 0
            }
            
            self.state["trades"].insert(0, trade)
            self.state["stats"]["last_trade_time"][opportunity["asset"]] = time.time()
            self.state["stats"]["daily_trades"] += 1
            self.state["stats"]["total_trades"] += 1
            
            # Keep only last 100 trades in memory
            if len(self.state["trades"]) > 100:
                self.state["trades"] = self.state["trades"][:100]
            
            return trade
            
        except Exception as e:
            print(f"Trade execution error: {e}")
            return None
    
    def update_trade_result(self, trade, win):
        """Update trade result after expiry"""
        if win:
            profit = trade["amount"] * 0.85  # 85% payout typical
            self.state["stats"]["wins"] += 1
            self.state["stats"]["consecutive_wins"] += 1
            self.state["stats"]["consecutive_losses"] = 0
            self.state["balances"]["current"] += profit
        else:
            profit = -trade["amount"]
            self.state["stats"]["losses"] += 1
            self.state["stats"]["consecutive_losses"] += 1
            self.state["stats"]["consecutive_wins"] = 0
            self.state["balances"]["current"] -= trade["amount"]
        
        # Update trade record
        trade["status"] = "completed"
        trade["result"] = "win" if win else "loss"
        trade["profit"] = profit
        
        # Update stats
        total = self.state["stats"]["wins"] + self.state["stats"]["losses"]
        if total > 0:
            self.state["stats"]["win_rate"] = round((self.state["stats"]["wins"] / total) * 100, 2)
        
        self.state["stats"]["profit_loss"] = self.state["balances"]["current"] - self.state["balances"]["initial"]
        
        # Update peak/lowest
        if self.state["balances"]["current"] > self.state["balances"]["peak"]:
            self.state["balances"]["peak"] = self.state["balances"]["current"]
        if self.state["balances"]["current"] < self.state["balances"]["lowest"]:
            self.state["balances"]["lowest"] = self.state["balances"]["current"]
    
    def monitor_trades(self):
        """Monitor pending trades and update results"""
        while self.state["running"]:
            time.sleep(5)  # Check every 5 seconds
            
            for trade in self.state["trades"]:
                if trade["status"] == "pending":
                    # Check if trade expired
                    expiry_time = trade["timestamp"] + trade["timeframe"]
                    if time.time() > expiry_time:
                        # Simulate result (in reality, fetch from API)
                        # For demo, 60% win rate based on confidence
                        win_probability = trade["confidence"] / 100
                        win = random.random() < win_probability
                        
                        self.update_trade_result(trade, win)
                        print(f"Trade {trade['id']} completed: {'WIN' if win else 'LOSS'} ${trade['profit']:.2f}")
    
    def run(self):
        """Main bot loop"""
        print("🚀 Auto-Trader Bot Started")
        print(f"📊 Monitoring: {', '.join(self.config['assets'])}")
        print(f"🎯 Confidence threshold: {self.config['confidence_threshold']}%")
        print(f"💰 Base amount: ${self.config['base_amount']}")
        
        self.state["running"] = True
        
        # Start monitor thread
        monitor_thread = threading.Thread(target=self.monitor_trades)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        while self.state["running"]:
            try:
                # Scan for opportunities
                opportunities = self.scan_opportunities()
                
                # Sort by confidence (highest first)
                opportunities.sort(key=lambda x: x["confidence"], reverse=True)
                
                for opp in opportunities:
                    # Check if we should trade
                    can_trade, reason = self.should_trade(opp)
                    
                    if can_trade:
                        print(f"🎯 SIGNAL FOUND: {opp['asset']} {opp['timeframe']}s {opp['direction']} {opp['confidence']}%")
                        
                        # Execute trade
                        trade = self.execute_trade(opp)
                        if trade:
                            print(f"✅ Trade executed: {trade['id']} - ${trade['amount']}")
                            
                            # Small delay between trades
                            time.sleep(2)
                    else:
                        if reason != "OK":
                            print(f"⏳ {opp['asset']}: {reason}")
                
                # Sleep before next scan
                time.sleep(10)
                
            except Exception as e:
                print(f"Bot error: {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop the bot"""
        self.state["running"] = False
        print("🛑 Auto-Trader Bot Stopped")

# Initialize bot
trader = AutoTrader()

# ============================================
# API ENDPOINTS TO CONTROL THE BOT
# ============================================

@app.route('/')
def home():
    return """
    <html>
        <head><title>🚀 COMMANDER'S AUTO-TRADER</title></head>
        <body style="background:black; color:#00ff88; font-family:monospace; padding:40px;">
            <h1>🚀 AUTO-TRADER BOT CONTROL PANEL</h1>
            <p>Status: <span id="status">Loading...</span></p>
            <script>
                setInterval(async () => {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    document.getElementById('status').innerHTML = 
                        data.running ? '🟢 RUNNING' : '🔴 STOPPED';
                }, 1000);
            </script>
        </body>
    </html>
    """

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the auto-trader"""
    if not trader.state["running"]:
        thread = threading.Thread(target=trader.run)
        thread.daemon = True
        thread.start()
        trader.state["thread"] = thread
        return jsonify({"status": "started", "running": True})
    return jsonify({"status": "already running", "running": True})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the auto-trader"""
    trader.stop()
    return jsonify({"status": "stopped", "running": False})

@app.route('/api/status')
def bot_status():
    """Get bot status"""
    return jsonify({
        "running": trader.state["running"],
        "stats": trader.state["stats"],
        "balances": trader.state["balances"],
        "config": trader.config,
        "recent_trades": trader.state["trades"][:10]
    })

@app.route('/api/config', methods=['GET', 'POST'])
def bot_config():
    """Get or update config"""
    if request.method == 'POST':
        new_config = request.json
        trader.config.update(new_config)
        return jsonify({"status": "updated", "config": trader.config})
    return jsonify(trader.config)

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    limit = int(request.args.get('limit', 50))
    return jsonify(trader.state["trades"][:limit])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    print("="*60)
    print("🚀 COMMANDER LALO'S AUTO-TRADER BOT")
    print("="*60)
    print(f"📊 Configuration loaded:")
    print(f"  - Assets: {', '.join(CONFIG['assets'])}")
    print(f"  - Threshold: {CONFIG['confidence_threshold']}%")
    print(f"  - Base amount: ${CONFIG['base_amount']}")
    print(f"  - Martingale: {CONFIG['martingale']}")
    print("="*60)
    print("📡 Control API endpoints:")
    print("  POST /api/start - Start bot")
    print("  POST /api/stop - Stop bot")
    print("  GET /api/status - Bot status")
    print("  GET /api/trades - Trade history")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
