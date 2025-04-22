'''
Created Date: 20.04.2025 18:03:42
Author: Julian Hardtung

Last Modified: 22.04.2025 13:20:26
Modified By: Julian Hardtung

Description: Analyzes Steam games owned by a user and fetches 
              completionist times from HowLongToBeat
'''

import requests
from howlongtobeatpy import HowLongToBeat
import time
import json
import csv
import random
import os
import unicodedata
import re
import seaborn as sns
import matplotlib.pyplot as plt

API_KEY = 'YOUR_STEAM_API_KEY'
STEAM_ID = 'YOUR_STEAM_ID64'
CACHE_FILE = 'hltb_cache.json'

# Load or create cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        hltb_cache = json.load(f)
else:
    hltb_cache = {}

def sanitize_title(title: str) -> str:
    # Remove all non-ASCII characters (including symbols like ™, ®, emojis, etc.)
    ascii_encoded = title.encode('ascii', 'ignore').decode('ascii')
    cleaned = re.sub(r'\s+', ' ', ascii_encoded).strip()
    if title != cleaned:
        print(f"Sanitized title: {title} -> {cleaned}", flush=True)
    return cleaned

def get_steam_games(api_key, steam_id):
    print("Fetching Steam game list...", flush=True)
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching games: {response.status_code} - {response.text}", flush=True)
        return []
    games = response.json().get('response', {}).get('games', [])
    print(f"Retrieved {len(games)} games from Steam", flush=True)
    return games

def has_100_percent_achievements(appid, api_key, steam_id):
    url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?appid={appid}&key={api_key}&steamid={steam_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not fetch achievements for appid {appid}", flush=True)
        return None
    try:
        achievements = response.json()['playerstats']['achievements']
        if not achievements:
            print(f"No achievements found for appid {appid}", flush=True)
            return None
        total = len(achievements)
        unlocked = sum(1 for a in achievements if a['achieved'] == 1)
        return unlocked == total
    except KeyError:
        print(f"No achievement data for appid {appid}", flush=True)
        return None

def get_completionist_time(game_name):
    sanitized_name = sanitize_title(game_name)
    if sanitized_name in hltb_cache:
        print(f"Using cached HLTB data for: {sanitized_name}", flush=True)
        return hltb_cache[sanitized_name], True  # Include cache flag

    print(f"Searching HLTB for: {sanitized_name}", flush=True)
    hltb = HowLongToBeat()
    try:
        results = hltb.search(sanitized_name)
        if not results:
            print(f"No results found for: {sanitized_name}", flush=True)
            hltb_cache[sanitized_name] = None
            return None, False
        best_match = max(results, key=lambda x: x.similarity)
        hours = best_match.completionist
        print(f"Found match: {best_match.game_name} | Completionist: {hours} hrs", flush=True)
        hltb_cache[sanitized_name] = hours
        return hours, False  # Not cached
    except Exception as e:
        print(f"Error fetching HLTB data for {sanitized_name}: {e}", flush=True)
        #hltb_cache[sanitized_name] = None
        return None, False
      
def save_to_csv(data, filename='completionist_times.csv'):
    # Filter out None values and sort by completionist_hours
    filtered = [entry for entry in data if entry['completionist_hours'] is not None]
    sorted_data = sorted(filtered, key=lambda x: x['completionist_hours'])

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'AppID', 'Completionist Hours'])

        for game in sorted_data:
            writer.writerow([game['name'], game['appid'], game['completionist_hours']])

    print(f"CSV saved as {filename}", flush=True)
    
def save_unmatched_games(data, filename='unmatched_games.csv'):
    unmatched = [entry for entry in data if entry['completionist_hours'] is None]

    if not unmatched:
        print("No unmatched games to save.", flush=True)
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'AppID'])
        for game in unmatched:
            writer.writerow([game['name'], game['appid']])

    print(f"Unmatched games saved as {filename}", flush=True)

def plot_completionist_distribution(data, save_png=True, filename='completionist_distribution.png'):
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    hours_list = [entry['completionist_hours'] for entry in data if entry['completionist_hours'] is not None]

    if not hours_list:
        print("No valid HLTB hour data to plot.")
        return

    # Compute stats
    mean_hours = np.mean(hours_list)
    median_hours = np.median(hours_list)

    # Setup plot
    plt.figure(figsize=(14, 6))
    sns.histplot(hours_list, bins=30, kde=True, color='skyblue', edgecolor='black')

    # Add vertical lines
    plt.axvline(mean_hours, color='green', linestyle='--', label=f'Mean: {mean_hours:.1f}h')
    plt.axvline(median_hours, color='orange', linestyle='--', label=f'Median: {median_hours:.1f}h')

    # Optional: highlight very long games
    over_100 = len([h for h in hours_list if h > 100])
    if over_100:
        plt.axvline(100, color='red', linestyle=':', label='100h threshold')

    # Labels
    plt.title("Distribution of Completionist Times", fontsize=16)
    plt.xlabel("Completionist Hours", fontsize=12)
    plt.ylabel("Number of Games", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    if save_png:
        plt.savefig(filename)
        print(f"Plot saved as: {filename}", flush=True)

    plt.show()


def main():
    games = get_steam_games(API_KEY, STEAM_ID)
    data = []

    skipped_100 = 0
    skipped_none = 0
    processed = 0

    print("Filtering and processing games...\n", flush=True)
    for i, game in enumerate(games, start=1):
        appid = game['appid']
        name = game['name']
        print(f"[{i}/{len(games)}] Checking: {name}", flush=True)

        ach_result = has_100_percent_achievements(appid, API_KEY, STEAM_ID)
        if ach_result is None:
            print(f"Skipping {name} (no achievements)", flush=True)
            skipped_none += 1
            continue
        if ach_result:
            print(f"Skipping {name} (100% achievements)", flush=True)
            skipped_100 += 1
            continue

        sanitized_name = sanitize_title(name)
        cached = sanitized_name in hltb_cache and hltb_cache[sanitized_name] is not None
        time_needed, from_cache = get_completionist_time(name)

        data.append({
            'name': name,
            'appid': appid,
            'completionist_hours': time_needed
        })
        processed += 1

        if not from_cache:
            sleep_time = random.uniform(5, 10)
            print(f"Waiting {sleep_time:.2f} seconds to avoid rate limits...\n", flush=True)
            time.sleep(sleep_time)

    print("\nSaving results to completionist_times.json...", flush=True)
    with open('completionist_times.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("Saving updated HLTB cache...", flush=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(hltb_cache, f, indent=2)

    save_to_csv(data)
    save_unmatched_games(data)
    print("\n Done!", flush=True)
    print(f"  Total games checked: {len(games)}", flush=True)
    print(f"  Processed (with incomplete achievements): {processed}", flush=True)
    print(f"  Skipped (no achievements): {skipped_none}", flush=True)
    print(f"  Skipped (100% achievements): {skipped_100}", flush=True)
    
    plot_completionist_distribution(data)

if __name__ == "__main__":
    main()
