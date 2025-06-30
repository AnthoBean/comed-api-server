from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
FEED_URL = "https://hourlypricing.comed.com/api?type=5minutefeed"
AVG_URL = "https://hourlypricing.comed.com/api?type=currenthouraverage"

def get_formatted_time(dt):
    return dt.strftime("%Y%m%d%H%M")

def fetch_5min_prices():
    now = datetime.utcnow()
    end = get_formatted_time(now)
    start = get_formatted_time(now - timedelta(minutes=5))
    url = f"{FEED_URL}&datestart={start}&dateend={end}"
    resp = requests.get(url)
    data = resp.json()
    latest = sorted(data, key=lambda x: x["millisUTC"])
    curr = float(latest[-1]["price"])
    prev = float(latest[-2]["price"]) if len(latest)>1 else curr
    ts = datetime.utcfromtimestamp(latest[-1]["millisUTC"]/1000).strftime("%I:%M %p")
    return curr, prev, ts

def fetch_hour_avg():
    data = requests.get(AVG_URL).json()
    return float(data[-1]["price"]) if data else None

def status(p):
    return "✅ Green Light" if p<=4 else ("⚠️ Maybe Wait" if p<=8 else "❌ Nope")

@app.route("/data")
def comed_status():
    try:
        curr, nxt, ts = fetch_5min_prices()
        avg = fetch_hour_avg()
        return jsonify([{
            "current_price": curr,
            "current_status": status(curr),
            "next_price": nxt,
            "next_status": status(nxt),
            "hour_avg": avg,
            "timestamp": ts
        }])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)