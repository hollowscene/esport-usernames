import os
import re
import requests
import time
from datetime import datetime

import pandas as pd


generic_headers = {
    "User-Agent": "EsportUsernames/1.0 (Anonymous)"
}


def clean_username(regex_pattern: str, player_name: str) -> str:
    """Isolates username by removing additional context in brackets."""
    if re.search(regex_pattern, player_name):
        index = player_name.rfind(" (")

        # Slice string after the last instance of a left bracket
        if index != -1:
            return player_name[:index]
        else:
            raise ValueError("Regex pattern must be wrong")

    else:
        return player_name


def filter_items(regex_pattern: str, items: list) -> list:
    """Filter input list for items that match given regex pattern."""
    matching_items = [item for item in items if re.search(regex_pattern, item)]
    return matching_items


def get_players(wiki: str, headers: dict = generic_headers, throttle_delay: int = 1) -> list:
    """Retrieve all players from a specific game's Liquipedia."""
    url = f"https://liquipedia.net/{wiki}/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Players",
        "cmlimit": "max",
    }

    players = []
    continue_token = None

    # Pagination
    # print(f"Pulling player names for {wiki}.")
    while True:
        if continue_token:
            params["cmcontinue"] = continue_token

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        players.extend(data["query"]["categorymembers"])
        time.sleep(throttle_delay)

        # Check if there's more data to fetch
        if "continue" in data:
            continue_token = data["continue"]["cmcontinue"]
        else:
            break

    return players


def ingest(wikis: list, pattern: str = re.compile(r".+\ \(.+\)$"), headers: dict = generic_headers, save_as_csv: bool = False, csv_path: str = "data", csv_name: str = None):
    """Main ingest function."""
    df = None
    exec_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    for wiki in wikis:
        print(f"Ingesting player name data for {wiki}.")
        players = get_players(wiki=wiki, headers=headers)
        df_wiki = pd.DataFrame.from_dict(players)

        # Player names only have a namespace value of 0
        df_wiki = df_wiki[df_wiki["ns"] == 0]

        # Create new columns
        df_wiki["cleantitle"] = df_wiki.apply(lambda row: clean_username(pattern, row["title"]), axis=1)
        df_wiki["cleantitleupper"] = df_wiki.apply(lambda row: clean_username(pattern, row["title"]).upper(), axis=1)
        df_wiki["wiki"] = wiki

        if df is None:
            df = df_wiki
        else:
            df = pd.concat([df, df_wiki], ignore_index=True)

    if save_as_csv:
        if csv_name is None:
            csv_name = f"players_{exec_datetime}.csv"
        df.to_csv(os.path.join(csv_path, csv_name), index=False)
        print(f"Saved data to {os.path.join(csv_path, csv_name)}.")

    return df
