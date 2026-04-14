import requests
import json
import csv
from datetime import datetime

# ⚠️ TEMP endpoint (we will replace later if needed)
URL = "https://fantasy.nrl.com/api/players"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

response = requests.get(URL, headers=headers)

# Safety check
if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

data = response.json()

players = []

for p in data:
    player = {
        "id": p.get("id"),
        "name": p.get("full_name"),
        "team": p.get("team"),
        "position": p.get("position"),
        "price": p.get("price"),
        "points": p.get("total_points"),
        "avg": p.get("avg_points"),
        "minutes": p.get("avg_minutes"),
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

print("Data updated successfully")
