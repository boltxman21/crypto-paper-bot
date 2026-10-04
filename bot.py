import os
import datetime
import requests

# 1. Configuration & API Setup
API_KEY = os.getenv("COINGECKO_API_KEY")
HEADERS = {"x-cg-demo-api-key": API_KEY} if API_KEY else {}

# 2. Fetch Top 50 Cryptocurrencies by Market Cap in 1 Single Call
url = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
)

response = requests.get(url, headers=HEADERS)
coins_data = response.json()

# 3. Process the Market Data
timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
log_entries = [f"--- Market Snapshot: {timestamp} ---"]

# Filter out stablecoins (USDT, USDC, etc.) for ratio / deviation scanning
filtered_coins = [
    coin for coin in coins_data 
    if coin['symbol'].lower() not in ['usdt', 'usdc', 'steth', 'pyusd', 'usds']
]

# Pick top two non-stablecoin crypto assets to compute a pair ratio (e.g., BTC and ETH)
btc_data = next((c for c in coins_data if c['id'] == 'bitcoin'), None)
eth_data = next((c for c in coins_data if c['id'] == 'ethereum'), None)

if btc_data and eth_data:
    btc_price = btc_data['current_price']
    eth_price = eth_data['current_price']
    btc_eth_ratio = btc_price / eth_price
    log_entries.append(f"Anchor Pair: 1 BTC (\({btc_price:,.2f}) = {btc_eth_ratio:.4f} ETH (\){eth_price:,.2f})")

# Log summary of Top 5 assets tracked
log_entries.append("Top 5 Assets scanned:")
for coin in coins_data[:5]:
    name = coin['name']
    symbol = coin['symbol'].upper()
    price = coin['current_price']
    change_24h = coin.get('price_change_percentage_24h', 0) or 0
    log_entries.append(f"  - {name} ({symbol}): ${price:,.2f} ({change_24h:+.2f}% 24h)")

log_entries.append(f"Total coins tracked in this run: {len(coins_data)}\n")

# 4. Save to the Journal
full_log = "\n".join(log_entries) + "\n"
with open("trades.log", "a") as f:
    f.write(full_log)

print("Market scan completed successfully!")
print(full_log)
