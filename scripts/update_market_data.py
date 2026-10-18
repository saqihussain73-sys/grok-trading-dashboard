"""Fetch public indicative quotes. No trading, secrets, or portfolio performance."""
import csv
import io
import json
import math
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "GrokTradingLabResearch/1.0 (public static dashboard)", "Accept": "application/json"}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8")

def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("Invalid quote")
    return round(number, 6)

def fetch_stock():
    data = list(csv.DictReader(io.StringIO(get("https://stooq.com/q/d/l/?s=aapl.us&i=d"))))
    if not data:
        raise ValueError("Stock data empty")
    last = data[-1]
    observed = datetime.strptime(last["Date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if (datetime.now(timezone.utc) - observed).days > 7:
        raise ValueError("Stock quote stale")
    return {"symbol": "AAPL", "price": positive(last["Close"]), "currency": "USD",
            "as_of": last["Date"], "source": "Stooq daily historical close", "status": "available",
            "disclaimer": "Last daily close; not a live executable quote"}

def fetch_crypto():
    data = json.loads(get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_last_updated_at=true"))
    item = data["bitcoin"]
    updated = datetime.fromtimestamp(int(item["last_updated_at"]), tz=timezone.utc)
    if abs((datetime.now(timezone.utc) - updated).total_seconds()) > 86400:
        raise ValueError("Crypto quote stale")
    return {"symbol": "BTC", "price": positive(item["usd"]), "currency": "USD",
            "as_of": updated.isoformat(), "source": "CoinGecko public API", "status": "available",
            "disclaimer": "Indicative quote; not executable and may be delayed"}

def main():
    path = ROOT / "data" / "status.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    for market, fetch in (("stocks", fetch_stock), ("crypto", fetch_crypto)):
        try:
            data["markets"][market] = fetch()
        except (ValueError, KeyError, TypeError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            data["markets"][market] = {"status": "unavailable", "reason": type(exc).__name__,
                                        "disclaimer": "Feed unavailable; no quote shown"}
    data["markets"]["memecoins"] = {"status": "not_connected"}
    data["updated_at"] = now
    data["source"] = "public_stooq_and_coingecko"
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({m: data["markets"][m]["status"] for m in ("stocks", "crypto", "memecoins")}))

if __name__ == "__main__":
    main()
