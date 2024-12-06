import re
import requests

generic_headers = {
    "User-Agent": "EsportUsernames/1.0 (Anonymous)"
}


def get_player_pages(wiki: str, headers: dict = generic_headers) -> list:
    """Retrieve all player pages from a specific game's Liquidipedia."""
    url = f"https://liquipedia.net/{wiki}/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Players",
        "cmlimit": "max",  # Fetch the maximum number of pages per request (usually 500)
    }

    all_players = []
    continue_token = None

    # Pagination
    while True:
        if continue_token:
            params['cmcontinue'] = continue_token

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        all_players.extend(data["query"]["categorymembers"])

        # Check if there's more data to fetch
        if "continue" in data:
            continue_token = data["continue"]["cmcontinue"]
        else:
            break

    return all_players


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
