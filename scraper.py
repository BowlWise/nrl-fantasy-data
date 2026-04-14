import requests
import json
import csv
from datetime import datetime

URL = "https://fantasy.nrl.com/data/nrl/players.json"

response = requests.get(URL)

if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

data = response.json()

players = []

for p in data.values():  # key difference: it's a dict, not list
    player = {
        "id": p.get("id"),
        "name": p.get("first_name") + " " + p.get("last_name"),
        "team": p.get("team"),
        "position": p.get("position"),
        "price": p.get("price"),
        "total_points": p.get("total_points"),
        "avg": p.get("avg"),
        "last_3_avg": p.get("last_3_avg"),
        "breakeven": p.get("breakeven"),
        "minutes": p.get("minutes"),
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

print("NRL Fantasy data updated successfully")