"""
Fetch all NRL players from the NRL Fantasy API, then retrieve per-match
statistics for each player from footystatistics.com and save the combined
dataset to data/nrl_player_stats_full.csv.
"""

import time
import requests
import pandas as pd

NRL_PLAYERS_URL = "https://fantasy.nrl.com/data/nrl/players.json"
FOOTYSTATS_URL = "https://footystatistics.com/api/player-stats"
OUTPUT_PATH = "data/nrl_player_stats_full.csv"
DELAY_SECONDS = 0.5

HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0",
}


def fetch_nrl_players():
    """Return a list of dicts with player_id, first_name, last_name."""
    print("Fetching NRL players...")
    response = requests.get(NRL_PLAYERS_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    # The endpoint returns a list of player objects.
    players = []
    items = data if isinstance(data, list) else data.values()
    for p in items:
        player_id = p.get("id")
        if player_id is not None:
            players.append(
                {
                    "player_id": player_id,
                    "first_name": p.get("first_name", ""),
                    "last_name": p.get("last_name", ""),
                }
            )

    print(f"Found {len(players)} players.")
    return players


def fetch_player_stats(player_id):
    """
    Fetch per-match stats from footystatistics.com for a given player_id.
    Returns the raw JSON response dict, or None on error.
    """
    try:
        response = requests.get(
            FOOTYSTATS_URL,
            params={"player_id": player_id},
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  Error fetching stats for player_id={player_id}: {e}")
        return None


def extract_rows(player, api_response):
    """
    Build a list of flat row dicts from the API response for one player.

    The footystatistics.com response has the shape:
        {
          "player": { ... },
          "stats":  [ { per-match record }, ... ],
          ...
        }
    """
    if api_response is None:
        return []

    match_records = []
    if isinstance(api_response, dict):
        match_records = api_response.get("stats") or []
    elif isinstance(api_response, list):
        match_records = api_response

    rows = []
    for record in match_records:
        if not isinstance(record, dict):
            continue
        row = {
            "player_id": player["player_id"],
            "first_name": player["first_name"],
            "last_name": player["last_name"],
            # Match context
            "season": record.get("year"),
            "round_id": record.get("round_id"),
            "opponent": record.get("opponent"),
            "position_match": record.get("position_match"),
            "match_date": record.get("match_date"),
            # Fantasy fields
            "fantasy_points": record.get("fantasy_points"),
            "price": record.get("price"),
            "break_even": record.get("be"),
            # Physical
            "time_on_ground": record.get("time_on_ground"),
            # Attack
            "tries": record.get("tries"),
            "try_assists": record.get("try_assists"),
            "line_breaks": record.get("line_breaks"),
            "line_break_assists": record.get("line_break_assists"),
            "metres_gained": record.get("metres_gained"),
            # Defence
            "tackles": record.get("tackles"),
            "missed_tackles": record.get("missed_tackles"),
            # Ball-carrying / kicking
            "tackle_breaks": record.get("tackle_breaks"),
            "offloads": record.get("offloads"),
            "errors": record.get("errors"),
            "kick_metres": record.get("kick_metres"),
        }
        rows.append(row)

    return rows


def main():
    players = fetch_nrl_players()
    all_rows = []

    for i, player in enumerate(players, start=1):
        player_id = player["player_id"]
        name = f"{player['first_name']} {player['last_name']}".strip()
        print(f"({i}/{len(players)}) {name} (id={player_id})")

        api_response = fetch_player_stats(player_id)
        rows = extract_rows(player, api_response)

        if rows:
            all_rows.extend(rows)
            print(f"  -> {len(rows)} match record(s) added.")
        else:
            print(f"  -> No match data returned.")

        time.sleep(DELAY_SECONDS)

    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"\nSaved {len(df)} rows to {OUTPUT_PATH}")
    else:
        print("\nNo data collected — empty CSV not written.")


if __name__ == "__main__":
    main()
