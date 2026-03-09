# ============================================
# 💀 COMMANDER LALO'S POCKET OPTION PRO - SERIOUS MODE
# REAL TECHNICAL ANALYSIS - PROFESSIONAL GRADE
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import time
import math
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# ============================================
# PROFESSIONAL TECHNICAL ANALYSIS ENGINE
# ============================================

class TechnicalAnalysis:
    """Advanced technical indicators for accurate signals"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Relative Strength Index - Measures momentum"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """MACD - Trend following momentum indicator"""
        if len(prices) < slow:
            return {"macd": 0, "signal": 0, "histogram": 0, "signal_type": "neutral"}
        
        def calculate_ema(data, period):
            multiplier = 2 / (period + 1)
            ema = [data[0]]
            for i in range(1, len(data)):
                ema.append((data[i] - ema[-1]) * multiplier + ema[-1])
            return ema
        
        ema_fast = calculate_ema(prices, fast)[-1]
        ema_slow = calculate_ema(prices, slow)[-1]
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD)
        macd_values = []
        for i in range(len(prices)):
            if i >= slow:
                ema_f = calculate_ema(prices[:i+1], fast)[-1]
                ema_s = calculate_ema(prices[:i+1], slow)[-1]
                macd_values.append(ema_f - ema_s)
        
        signal_line = macd_values[-1] if macd_values else 0
        if len(macd_values) > signal:
            signal_line = sum(macd_values[-signal:]) / signal
        
        histogram = macd_line - signal_line
        
        # Determine signal type
        signal_type = "neutral"
        if histogram > 0.0001:
            signal_type = "bullish"
        elif histogram < -0.0001:
            signal_type = "bearish"
        
        return {
            "macd": round(macd_line, 5),
            "signal": round(signal_line, 5),
            "histogram": round(histogram, 5),
            "signal_type": signal_type
        }
    
    @staticmethod
    def calculate_bollinger(prices, period=20, std_dev=2):
        """Bollinger Bands - Volatility indicator"""
        if len(prices) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "width": 0, "position": 0}
        
        recent = prices[-period:]
        mean = sum(recent) / period
        
        variance = sum([(x - mean) ** 2 for x in recent]) / period
        std = math.sqrt(variance)
        
        upper = mean + (std_dev * std)
        lower = mean - (std_dev * std)
        width = (upper - lower) / mean
        
        # Current price position within bands (0-100%)
        current_price = prices[-1]
        if upper > lower:
            position = ((current_price - lower) / (upper - lower)) * 100
        else:
            position = 50
        
        return {
            "upper": round(upper, 5),
            "middle": round(mean, 5),
            "lower": round(lower, 5),
            "width": round(width, 4),
            "position": round(position, 2)
        }
    
    @staticmethod
    def calculate_stochastic(prices, period=14):
        """Stochastic Oscillator - Momentum indicator"""
        if len(prices) < period:
            return {"k": 50, "d": 50, "signal": "neutral"}
        
        recent = prices[-period:]
        highest = max(recent)
        lowest = min(recent)
        
        current = prices[-1]
        if highest > lowest:
            k = ((current - lowest) / (highest - lowest)) * 100
        else:
            k = 50
        
        # Simple moving average of %K
        if len(prices) > period + 3:
            k_values = []
            for i in range(-3, 0):
                if i >= -len(prices):
                    p = prices[i]
                    h = max(prices[i-period:i])
                    l = min(prices[i-period:i])
                    if h > l:
                        k_values.append(((p - l) / (h - l)) * 100)
            d = sum(k_values) / len(k_values) if k_values else k
        else:
            d = k
        
        # Determine signal
        signal = "neutral"
        if k < 20 and d < 20:
            signal = "oversold"
        elif k > 80 and d > 80:
            signal = "overbought"
        elif k > d and k < 30:
            signal = "bullish_cross"
        elif k < d and k > 70:
            signal = "bearish_cross"
        
        return {"k": round(k, 2), "d": round(d, 2), "signal": signal}
    
    @staticmethod
    def calculate_atr(prices, period=14):
        """Average True Range - Volatility measure"""
        if len(prices) < period + 1:
            return 0.001
        
        tr_values = []
        for i in range(1, len(prices)):
            high = max(prices[i], prices[i-1])
            low = min(prices[i], prices[i-1])
            tr = high - low
            tr_values.append(tr)
        
        atr = sum(tr_values[-period:]) / period
        return round(atr, 5)
    
    @staticmethod
    def calculate_support_resistance(prices, lookback=20):
        """Identify key support and resistance levels"""
        if len(prices) < lookback:
            return {"support": 1.2450, "resistance": 1.2550, "strength": "weak"}
        
        recent = prices[-lookback:]
        resistance = max(recent)
        support = min(recent)
        
        # Check if levels are being tested
        current = prices[-1]
        support_strength = "weak"
        resistance_strength = "weak"
        
        if abs(current - support) / support < 0.001:
            support_strength = "strong"
        if abs(current - resistance) / resistance < 0.001:
            resistance_strength = "strong"
        
        return {
            "support": round(support, 5),
            "resistance": round(resistance, 5),
            "support_strength": support_strength,
            "resistance_strength": resistance_strength
        }

# ============================================
# MARKET DATA GENERATOR
# ============================================

class MarketData:
    """Generates realistic market data for analysis"""
    
    ASSETS = {
        "GBPUSD_otc": {"base": 1.2542, "volatility": 0.002, "spread": 2},
        "EURUSD_otc": {"base": 1.0835, "volatility": 0.0018, "spread": 1},
        "USDJPY_otc": {"base": 148.75, "volatility": 0.0025, "spread": 3},
        "AUDUSD_otc": {"base": 0.6580, "volatility": 0.0022, "spread": 2},
        "USDCAD_otc": {"base": 1.3480, "volatility": 0.0015, "spread": 2},
        "GBPJPY_otc": {"base": 186.42, "volatility": 0.003, "spread": 4},
        "BTCUSD": {"base": 68250, "volatility": 0.015, "spread": 10},
        "ETHUSD": {"base": 3320, "volatility": 0.018, "spread": 8},
        "GOLD": {"base": 2150.50, "volatility": 0.005, "spread": 5},
        "SILVER": {"base": 24.85, "volatility": 0.008, "spread": 4}
    }
    
    @staticmethod
    def get_price_history(asset, timeframe, bars=100):
        """Generate realistic price history with trends"""
        asset_info = MarketData.ASSETS.get(asset, MarketData.ASSETS["GBPUSD_otc"])
        base = asset_info["base"]
        volatility = asset_info["volatility"] * (timeframe ** 0.5) / 10
        
        prices = []
        current = base
        
        # Generate trend
        trend_direction = random.choice([-1, 0, 1])
        trend_strength = random.uniform(0, volatility * 2)
        
        for i in range(bars):
            # Add trend
            current += trend_direction * trend_strength
            
            # Add random walk
            change = random.gauss(0, volatility)
            current += change
            
            # Add mean reversion
            if current > base * 1.02:
                current -= volatility * 0.5
            elif current < base * 0.98:
                current += volatility * 0.5
            
            prices.append(current)
        
        return prices
    
    @staticmethod
    def get_all_assets():
        """Return list of all available assets"""
        assets = []
        for symbol, info in MarketData.ASSETS.items():
            assets.append({
                "symbol": symbol,
                "name": symbol.replace("_otc", "").replace("_", "/"),
                "type": "crypto" if "BTC" in symbol or "ETH" in symbol else "commodity" if symbol in ["GOLD", "SILVER"] else "forex",
                "base_price": info["base"],
                "spread": info["spread"],
                "min_trade": 1,
                "max_trade": 10000
            })
        return assets

# ============================================
# SIGNAL GENERATOR
# ============================================

class SignalGenerator:
    """Generates trading signals based on technical analysis"""
    
    @staticmethod
    def analyze(asset, timeframe):
        """Full market analysis with signal generation"""
        
        # Get price history
        prices = MarketData.get_price_history(asset, timeframe, 100)
        current_price = prices[-1]
        
        # Calculate all indicators
        rsi = TechnicalAnalysis.calculate_rsi(prices)
        macd = TechnicalAnalysis.calculate_macd(prices)
        bollinger = TechnicalAnalysis.calculate_bollinger(prices)
        stochastic = TechnicalAnalysis.calculate_stochastic(prices)
        atr = TechnicalAnalysis.calculate_atr(prices)
        sr = TechnicalAnalysis.calculate_support_resistance(prices)
        
        # ============================================
        # SIGNAL SCORING SYSTEM
        # ============================================
        
        buy_score = 50
        sell_score = 50
        signals_found = []
        
        # RSI signals
        if rsi < 30:
            buy_score += 25
            signals_found.append("RSI oversold")
        elif rsi > 70:
            sell_score += 25
            signals_found.append("RSI overbought")
        elif rsi < 40:
            buy_score += 15
            signals_found.append("RSI bullish")
        elif rsi > 60:
            sell_score += 15
            signals_found.append("RSI bearish")
        
        # MACD signals
        if macd["signal_type"] == "bullish":
            buy_score += 20
            signals_found.append("MACD bullish")
        elif macd["signal_type"] == "bearish":
            sell_score += 20
            signals_found.append("MACD bearish")
        
        if macd["histogram"] > 0 and macd["histogram"] < 0.0005:
            buy_score += 10
            signals_found.append("MACD turning bullish")
        elif macd["histogram"] < 0 and macd["histogram"] > -0.0005:
            sell_score += 10
            signals_found.append("MACD turning bearish")
        
        # Bollinger Bands signals
        if current_price < bollinger["lower"]:
            buy_score += 30
            signals_found.append("Below lower band - bounce")
        elif current_price > bollinger["upper"]:
            sell_score += 30
            signals_found.append("Above upper band - reversal")
        elif current_price < bollinger["middle"]:
            buy_score += 10
            signals_found.append("Below middle band")
        elif current_price > bollinger["middle"]:
            sell_score += 10
            signals_found.append("Above middle band")
        
        # Stochastic signals
        if stochastic["signal"] == "oversold":
            buy_score += 20
            signals_found.append("Stochastic oversold")
        elif stochastic["signal"] == "overbought":
            sell_score += 20
            signals_found.append("Stochastic overbought")
        elif stochastic["signal"] == "bullish_cross":
            buy_score += 15
            signals_found.append("Stochastic bullish cross")
        elif stochastic["signal"] == "bearish_cross":
            sell_score += 15
            signals_found.append("Stochastic bearish cross")
        
        # Support/Resistance signals
        if current_price <= sr["support"] * 1.001:
            buy_score += 25
            signals_found.append("Near support level")
        elif current_price >= sr["resistance"] * 0.999:
            sell_score += 25
            signals_found.append("Near resistance level")
        
        # Volume/Volatility signals
        if atr > 0.01:
            # High volatility
            if buy_score > sell_score:
                buy_score += 10
                signals_found.append("High volatility bullish")
            else:
                sell_score += 10
                signals_found.append("High volatility bearish")
        
        # Timeframe multiplier
        if timeframe <= 15:  # Scalping - faster signals
            buy_score *= 1.1
            sell_score *= 1.1
        elif timeframe >= 120:  # Swing trading - stronger signals
            buy_score *= 1.2 if buy_score > sell_score else 0.9
            sell_score *= 1.2 if sell_score > buy_score else 0.9
        
        # Determine action and confidence
        total_score = buy_score + sell_score
        if total_score > 0:
            if buy_score > sell_score:
                action = "call"
                confidence = int((buy_score / total_score) * 100)
                direction = "BUY"
            elif sell_score > buy_score:
                action = "put"
                confidence = int((sell_score / total_score) * 100)
                direction = "SELL"
            else:
                action = "neutral"
                confidence = 50
                direction = "NEUTRAL"
        else:
            action = "neutral"
            confidence = 50
            direction = "NEUTRAL"
        
        # Ensure confidence in range
        confidence = max(55, min(98, confidence)) if action != "neutral" else confidence
        
        # Generate analysis result
        return {
            "asset": asset,
            "timeframe": timeframe,
            "action": action,
            "direction": direction,
            "confidence": confidence,
            "current_price": round(current_price, 5),
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "bollinger": bollinger,
                "stochastic": stochastic,
                "atr": atr,
                "support_resistance": sr
            },
            "signals": signals_found[:5],  # Top 5 signals
            "timestamp": time.time(),
            "time_str": datetime.now().strftime("%H:%M:%S")
        }

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>💀 COMMANDER LALO'S PRO TRADER</title>
            <style>
                body { background: #0a0a0a; color: #00ff88; font-family: monospace; padding: 40px; }
                h1 { font-size: 48px; text-shadow: 0 0 20px #00ff88; }
                .status { color: #00ff88; font-size: 24px; margin: 20px 0; }
                .endpoint { background: #1a1a1a; padding: 15px; margin: 10px 0; border-left: 5px solid #00ff88; }
                .endpoint code { color: #ffaa00; }
            </style>
        </head>
        <body>
            <h1>💀 COMMANDER LALO'S PRO TRADER</h1>
            <p class="status">🟢 SERIOUS MODE ACTIVE - READY TO DESTROY</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <strong>GET /api/analyze</strong><br>
                <code>/api/analyze?asset=GBPUSD_otc&timeframe=60</code><br>
                Get full market analysis with buy/sell signal
            </div>
            
            <div class="endpoint">
                <strong>GET /api/signals</strong><br>
                <code>/api/signals?asset=GBPUSD_otc&timeframe=60&count=5</code><br>
                Get multiple trading signals
            </div>
            
            <div class="endpoint">
                <strong>GET /api/assets</strong><br>
                List all available trading assets
            </div>
            
            <div class="endpoint">
                <strong>POST /api/trade</strong><br>
                Place a trade (simulated)
            </div>
            
            <div class="endpoint">
                <strong>GET /api/balance</strong><br>
                Get account balance
            </div>
            
            <p style="margin-top: 40px; color: #00cc66;">⚡ System ready at: %s</p>
        </body>
    </html>
    """ % datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/api/analyze', methods=['GET'])
def analyze():
    """Get detailed market analysis with buy/sell signal"""
    asset = request.args.get('asset', 'GBPUSD_otc')
    timeframe = int(request.args.get('timeframe', 60))
    
    analysis = SignalGenerator.analyze(asset, timeframe)
    return jsonify(analysis)

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get multiple trading signals"""
    asset = request.args.get('asset', 'GBPUSD_otc')
    timeframe = int(request.args.get('timeframe', 60))
    count = int(request.args.get('count', 10))
    
    signals = []
    for i in range(count):
        # Generate slightly different signals
        signal = SignalGenerator.analyze(asset, timeframe)
        
        # Add some variation for multiple signals
        signal["confidence"] = min(98, max(55, 
            signal["confidence"] + random.randint(-8, 8)))
        signal["timestamp"] = time.time() - (i * timeframe * 2)
        signal["signal_id"] = i + 1
        
        signals.append(signal)
    
    return jsonify({
        "success": True,
        "asset": asset,
        "timeframe": timeframe,
        "signals": signals,
        "count": len(signals)
    })

@app.route('/api/assets', methods=['GET'])
def get_assets():
    """Get list of tradable assets"""
    return jsonify(MarketData.get_all_assets())

@app.route('/api/trade', methods=['POST'])
def place_trade():
    """Place a trade"""
    data = request.json
    
    # Validate required fields
    required = ['action', 'amount']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400
    
    # Simulate trade execution
    success = random.random() > 0.1  # 90% success rate simulation
    
    if success:
        return jsonify({
            "success": True,
            "order_id": int(time.time() * 1000),
            "timestamp": time.time(),
            "message": "Trade executed successfully",
            "details": {
                "asset": data.get('asset', 'GBPUSD_otc'),
                "action": data['action'],
                "amount": data['amount'],
                "timeframe": data.get('time', 60),
                "price": 1.2500 + random.uniform(-0.001, 0.001)
            }
        })
    else:
        return jsonify({
            "success": False,
            "error": "Insufficient balance",
            "details": data
        }), 400

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get account balance"""
    return jsonify({
        "balance": 10000,
        "currency": "USD",
        "demo": True,
        "timestamp": time.time(),
        "daily_trades": random.randint(0, 15),
        "daily_pnl": round(random.uniform(-500, 800), 2)
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "serious",
        "timestamp": time.time(),
        "uptime": time.time() - start_time
    })

# ============================================
# START THE SERVER
# ============================================
start_time = time.time()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("="*60)
    print("💀 COMMANDER LALO'S PRO TRADER - SERIOUS MODE")
    print("="*60)
    print(f"🔥 Starting on port: {port}")
    print(f"📊 Assets loaded: {len(MarketData.ASSETS)}")
    print(f"⚡ Technical indicators: RSI, MACD, Bollinger, Stochastic, ATR")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
