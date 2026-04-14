import requests
import pandas as pd
import string
import time
import os

BASE_URL = "https://footystatistics.com/api/player-search?search="
PLAYER_STATS_URL = "https://footystatistics.com/api/player-stats?player_id={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_PATH = "data/footystats/games.csv"


def get_players():
    players = {}
    
    for letter in string.ascii_lowercase:
        print(f"🔍 Searching: {letter}")
        try:
            res = requests.get(BASE_URL + letter, headers=HEADERS, timeout=10)
            data = res.json()

            for p in data:
                players[p["player_id"]] = p

            time.sleep(0.5)  # polite rate limiting

        except Exception as e:
            print(f"❌ Error searching {letter}: {e}")

    print(f"✅ Found {len(players)} unique players")
    return players


def get_player_stats(player_id):
    try:
        url = PLAYER_STATS_URL.format(player_id)
        res = requests.get(url, headers=HEADERS, timeout=10)
        return res.json()
    except Exception as e:
        print(f"❌ Failed player {player_id}: {e}")
        return None


def run_scraper():
    players = get_players()
    all_rows = []

    for player_id, player_meta in players.items():
        print(f"📊 Fetching stats for {player_id}")

        data = get_player_stats(player_id)
        if not data:
            continue

        player_info = data.get("player", {})
        stats = data.get("stats", [])

        if not stats:
            continue

        for game in stats:
            try:
                row = {
                    "player_id": player_id,
                    "first_name": player_info.get("first_name"),
                    "last_name": player_info.get("last_name"),
                    "team": player_info.get("team_name"),
                    "position": player_info.get("positions_label"),

                    "year": game.get("year"),
                    "round": game.get("round_id"),
                    "round_display": game.get("round_display"),
                    "opponent": game.get("opponent"),

                    "minutes": game.get("time_on_ground"),
                    "tries": game.get("tries"),
                    "try_assists": game.get("try_assists"),
                    "line_breaks": game.get("line_breaks"),
                    "tackles": game.get("tackles"),
                    "missed_tackles": game.get("missed_tackles"),
                    "tackle_breaks": game.get("tackle_breaks"),
                    "offloads": game.get("offloads"),
                    "errors": game.get("errors"),

                    "metres": game.get("metres_gained"),

                    "fantasy_points": game.get("fantasy_points"),
                    "price": game.get("price"),
                    "be": game.get("be"),

                    "home_team": game.get("home_squad_name"),
                    "away_team": game.get("away_squad_name"),
                    "home_score": game.get("home_score"),
                    "away_score": game.get("away_score"),

                    "match_date": game.get("match_date")
                }

                all_rows.append(row)

            except Exception as e:
                print(f"⚠️ Skipping bad row for player {player_id}: {e}")

        time.sleep(0.2)

    # Create DataFrame
    df = pd.DataFrame(all_rows)

    if df.empty:
        print("⚠️ No valid game data found — exiting")
        return

    # Ensure output folder exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Save CSV
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_scraper()
