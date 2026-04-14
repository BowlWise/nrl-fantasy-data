import requests
import json
import csv
from datetime import datetime

# TEMP test endpoint (guaranteed to work)
URL = "https://jsonplaceholder.typicode.com/users"

response = requests.get(URL)

if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

data = response.json()

players = []

for p in data:
    player = {
        "id": p.get("id"),
        "name": p.get("name"),
        "team": p.get("company", {}).get("name"),
        "position": "N/A",
        "price": 0,
        "points": 0,
        "avg": 0,
        "minutes": 0,
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
