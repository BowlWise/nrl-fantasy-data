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
    empty_streak = 0

    # 🎯 Target realistic range
    for player_id in range(1, 20000):

        if player_id % 100 == 0:
            print(f"🔍 Checking player_id: {player_id}")

        data = get_player_stats(player_id)

        # ❌ No data
        if not data or "stats" not in data:
            empty_streak += 1

            # 🛑 Stop if we hit long run of empty IDs
            if empty_streak > 300:
                print("🛑 No players found for a while — stopping early")
                break

            continue

        # ✅ Reset streak if valid player found
        empty_streak = 0

        player_info = data.get("player", {})
        stats = data.get("stats", [])

        if not stats:
            continue

        print(f"✅ Found player {player_id}")

        for game in stats:
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

        # ⚡ Faster but still safe
        time.sleep(0.05)

    if not all_rows:
        print("⚠️ No data found")
        return

    df = pd.DataFrame(all_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_scraper()
