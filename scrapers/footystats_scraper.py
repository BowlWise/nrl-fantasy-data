import requests
import pandas as pd
import time
import string

BASE_URL = "https://footystatistics.com/api"

HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0"
}

# -----------------------------------
# STEP 1: GET ALL PLAYERS VIA SEARCH
# -----------------------------------
def get_all_players():
    players = {}

    for letter in string.ascii_lowercase:
        print(f"🔍 Searching: {letter}")
        try:
            r = requests.get(
                f"{BASE_URL}/search?q={letter}",
                headers=HEADERS
            )
            results = r.json()

            for p in results:
                if "player_id" in p:
                    players[p["player_id"]] = {
                        "player_id": p["player_id"],
                        "name": p.get("name"),
                        "team": p.get("team"),
                        "position": p.get("position")
                    }

            time.sleep(0.3)

        except Exception as e:
            print(f"❌ Error on letter {letter}: {e}")

    print(f"✅ Found {len(players)} unique players")
    return list(players.values())


# -----------------------------------
# STEP 2: GET PLAYER STATS
# -----------------------------------
def get_player_stats(player_id):
    try:
        r = requests.get(
            f"{BASE_URL}/player-stats?player_id={player_id}",
            headers=HEADERS
        )

        data = r.json()

        # Handle list response
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict):
            return data
        else:
            return None

    except Exception as e:
        print(f"❌ Failed stats for {player_id}: {e}")
        return None


# -----------------------------------
# STEP 3: MAIN SCRAPER
# -----------------------------------
def run_scraper():
    players = get_all_players()
    dataset = []

    for i, player in enumerate(players):
        print(f"📊 ({i+1}/{len(players)}) {player['name']}")

        stats = get_player_stats(player["player_id"])

        if stats:
            combined = {
                **player,
                "cost": stats.get("cost"),
                "avg_points": stats.get("avg_points"),
                "high_score": stats.get("high_score"),
                "low_score": stats.get("low_score"),
                "last_3_avg": stats.get("last_3_avg"),
                "last_5_avg": stats.get("last_5_avg"),
                "owned_by": stats.get("owned_by"),
                "team_name": stats.get("team_name"),
                "positions": stats.get("positions_label"),
                "updated_at": stats.get("updated_at")
            }

            dataset.append(combined)

        time.sleep(0.3)

    df = pd.DataFrame(dataset)

    # Save to repo structure
    output_path = "data/footystats/players.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ DONE — saved to {output_path}")
    print(f"📦 Total players scraped: {len(df)}")


# -----------------------------------
# RUN
# -----------------------------------
if __name__ == "__main__":
    run_scraper()