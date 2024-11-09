import re
import requests

generic_headers = {
    "User-Agent": "EsportUsernames/1.0 (Anonymous)"
}


def get_player_pages(wiki: str, headers=generic_headers) -> list:
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


def find_matching_items(items, pattern):
    """Pre-processing step to strip the extra brackets stuff which is usually used to distinguish players with the same name (which we don't want!)."""
    # Use list comprehension to filter items that match the pattern
    matching_items = [item for item in items if re.search(pattern, item)]
    
    return matching_items
