import requests
import pandas as pd
import time
import random

BASE_URL = "https://footystatistics.com/api/player-stats?player_id={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}


def fetch_player(player_id):
    try:
        url = BASE_URL.format(player_id)
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if not data or len(data) == 0:
            return None

        return data

    except Exception as e:
        print(f"❌ Error for {player_id}: {e}")
        return None


def run_scraper():
    all_data = []
    empty_streak = 0

    START_ID = 1000
    MAX_ID = 2000000
    EMPTY_LIMIT = 300  # stop after this many misses in a row

    for player_id in range(START_ID, MAX_ID):
        print(f"🔍 Player ID: {player_id}")

        data = fetch_player(player_id)

        if data:
            empty_streak = 0

            for game in data:
                all_data.append(game)

        else:
            empty_streak += 1

        # 🧠 Stop if we hit a long run of empty IDs
        if empty_streak >= EMPTY_LIMIT:
            print(f"🛑 Stopping early at ID {player_id} (no more players likely)")
            break

        # ⏱️ Rate limiting (important)
        time.sleep(random.uniform(0.2, 0.5))

    print(f"✅ Total records collected: {len(all_data)}")

    if len(all_data) == 0:
        print("⚠️ No data found — exiting")
        return

    df = pd.DataFrame(all_data)

    output_path = "data/footystats/games.csv"
    df.to_csv(output_path, index=False)

    print(f"💾 Saved to {output_path}")


if __name__ == "__main__":
    run_scraper()
