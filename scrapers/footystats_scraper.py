import requests
import pandas as pd
import time
import os

PLAYER_STATS_URL = "https://footystatistics.com/api/player-stats?player_id={}"
OUTPUT_PATH = "data/footystats/games.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_player_stats(player_id):
    try:
        res = requests.get(
            PLAYER_STATS_URL.format(player_id),
            headers=HEADERS,
            timeout=10
        )

        if res.status_code != 200:
            return None

        return res.json()

    except:
        return None


def run_scraper():
    all_rows = []

    # ✅ NEW: batching via environment variables
    START_ID = int(os.getenv("START_ID", 1))
    END_ID = int(os.getenv("END_ID", 10000))

    print(f"🚀 Running batch: {START_ID} → {END_ID}")

    for player_id in range(START_ID, END_ID):

        if player_id % 500 == 0:
            print(f"🔍 Checking player_id: {player_id}")

        data = get_player_stats(player_id)

        if not data or "stats" not in data:
            continue

        player_info = data.get("player", {})
        stats = data.get("stats", [])

        if not stats:
            continue

        print(f"✅ Found player {player_id}")

        for game in stats:
            row = {
                # 🧍 Player
                "player_id": player_id,
                "first_name": player_info.get("first_name"),
                "last_name": player_info.get("last_name"),
                "team": player_info.get("team_name"),
                "position": player_info.get("positions_label"),

                # 📅 Match Info
                "year": game.get("year"),
                "round": game.get("round_id"),
                "round_display": game.get("round_display"),
                "opponent": game.get("opponent"),
                "match_date": game.get("match_date"),

                # 🏟 Game Context
                "home_team": game.get("home_squad_name"),
                "away_team": game.get("away_squad_name"),
                "home_score": game.get("home_score"),
                "away_score": game.get("away_score"),

                # ⏱ Usage
                "minutes": game.get("time_on_ground"),

                # ⚔️ Attack
                "tries": game.get("tries"),
                "try_assists": game.get("try_assists"),
                "line_breaks": game.get("line_breaks"),
                "line_break_assists": game.get("line_break_assists"),
                "tackle_breaks": game.get("tackle_breaks"),
                "metres": game.get("metres_gained"),

                # 🛡 Defence
                "tackles": game.get("tackles"),
                "missed_tackles": game.get("missed_tackles"),

                # 🔁 Other stats
                "offloads": game.get("offloads"),
                "errors": game.get("errors"),
                "kick_metres": game.get("kick_metres"),

                # 💰 Fantasy
                "fantasy_points": game.get("fantasy_points"),
                "price": game.get("price"),
                "break_even": game.get("be")
            }

            all_rows.append(row)

        # ⚡ Speed vs safety balance
        time.sleep(0.02)

    if not all_rows:
        print("⚠️ No data found")
        return

    df = pd.DataFrame(all_rows)

    # ensure folder exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # ✅ NEW: append instead of overwrite
    if os.path.exists(OUTPUT_PATH):
        df.to_csv(OUTPUT_PATH, mode='a', header=False, index=False)
    else:
        df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_scraper()
