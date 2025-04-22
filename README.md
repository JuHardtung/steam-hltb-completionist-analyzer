# 🎮 Steam HLTB Completionist Analyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-lightgrey.svg)]()

> Analyze your Steam library and estimate how long it would take to 100% complete each game using data from HowLongToBeat.com.

---

## 📦 Features

- ✅ Fetches your owned Steam games via the Steam Web API  
- 🏆 Filters out games with no achievements or already 100% completed  
- ⏱ Retrieves *completionist* time from HowLongToBeat  
- ⚡ Uses local caching to reduce redundant API calls  
- 🧹 Sanitizes game titles to improve matching accuracy  
- 📊 Generates CSV, JSON, and histogram of your backlog  
- 📁 Saves unmatched game titles for manual review

---

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/steam-hltb-analyzer.git
cd steam-hltb-analyzer
```

### 2. Install dependencies

`pip install -r requirements.txt`

Requirements:
```
    requests
    howlongtobeatpy
    matplotlib
    seaborn
    numpy
```

### 3. Add your Steam credentials

Open the script (`steam_hltb_completionist_analyzer.py`) and update:

```
API_KEY = 'YOUR_STEAM_API_KEY'
STEAM_ID = 'YOUR_STEAM_ID_64'
```

Get your API key: https://steamcommunity.com/dev/apikey

Find your SteamID64: https://steamid.io/

## 🧪 Usage
Run the script:
`python -u steam_hltb_completionist_analyzer.py`

This will:
- Fetch your Steam games
- Filter games without achievements or already 100% complete
- Retrieve completionist times from HowLongToBeat
- Save results and generate graphs

## 📊 Output Files
| File	| Description |
| ------------- | ------- |
| completionist_times.csv	| Sorted list of games with estimated times |
| completionist_times.json	| JSON format of all processed results |
| unmatched_games.csv	| Games not matched on HowLongToBeat |
| hltb_cache.json	| Local cache for HLTB results |
| completionist_distribution.png	| Bell curve of completionist times |

## 📈 Example Output

CSV Sample:
|      Month    |   AppID | Completionist Hours |
| ------------- | ------- | ------- |
| Portal        | 400    | 6 |
| Hollow Knight | 367520 | 60 |
