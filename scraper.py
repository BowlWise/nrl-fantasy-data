import requests
import json
import csv
from datetime import datetime

# Real NRL Fantasy endpoint (working pattern)
URL = "https://fantasy.nrl.com/api/v1/players"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

response = requests.get(URL, headers=headers)

if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

data = response.json()

players = []

for p in data.get("players", []):
    player = {
        "id": p.get("id"),
        "name": p.get("full_name"),
        "team": p.get("team"),
        "position": p.get("position"),
        "price": p.get("price"),
        "points": p.get("total_points"),
        "avg": p.get("avg_points"),
        "breakeven": p.get("breakeven"),
        "ownership": p.get("ownership"),
        "updated_at": datetime.utcnow().isoformat()
    }
    players.append(player)

# Save JSON
with open("players.json", "w") as f:
    json.dump(players, f, indent=2)

# Save CSV
filename = f"players_{datetime.utcnow().date()}.csv"

with open(filename, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=players[0].keys())
    writer.writeheader()
    writer.writerows(players)

print("Fantasy data updated successfully")
