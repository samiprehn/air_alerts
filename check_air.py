import json
import os

import requests

NTFY_TOPIC = os.environ['NTFY_TOPIC']
AIRNOW_API_KEY = os.environ['AIRNOW_API_KEY']
ZIP_CODE = os.environ['ZIP']
THRESHOLD = int(os.environ.get('AQI_THRESHOLD') or '101')

SEEN_FILE = 'seen.json'


def load_state():
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {'alerted': False, 'last_aqi': None}


def save_state(state):
    with open(SEEN_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_current():
    url = 'https://www.airnowapi.org/aq/observation/zipCode/current/'
    params = {
        'format': 'application/json',
        'zipCode': ZIP_CODE,
        'distance': 25,
        'API_KEY': AIRNOW_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    observations = [o for o in resp.json() if o.get('AQI') is not None and o['AQI'] >= 0]
    if not observations:
        return None
    worst = max(observations, key=lambda o: o['AQI'])
    return {
        'aqi': worst['AQI'],
        'pollutant': worst['ParameterName'],
        'category': worst['Category']['Name'],
        'area': worst.get('ReportingArea', ZIP_CODE),
    }


def notify(obs):
    title = f"Air quality: {obs['category']}"
    message = f"AQI {obs['aqi']} ({obs['pollutant']}) in {obs['area']}."
    priority = 'high' if obs['aqi'] >= 151 else 'default'
    requests.post(
        f'https://ntfy.sh/{NTFY_TOPIC}',
        data=message.encode(),
        headers={
            'Title': title,
            'Priority': priority,
            'Click': 'https://www.airnow.gov/',
        },
    )


def main():
    state = load_state()
    obs = fetch_current()

    if obs is None:
        print(f"No observations returned for {ZIP_CODE}")
        return

    print(f"ZIP {ZIP_CODE}: AQI {obs['aqi']} ({obs['pollutant']}) — {obs['category']}")

    bad = obs['aqi'] >= THRESHOLD
    was_alerted = state.get('alerted', False)

    if bad and not was_alerted:
        notify(obs)
        state['alerted'] = True
        print(f"Alerted: AQI crossed to {obs['aqi']} (threshold {THRESHOLD})")
    elif not bad and was_alerted:
        state['alerted'] = False
        print(f"Cleared: AQI dropped to {obs['aqi']}, below threshold {THRESHOLD}")
    else:
        print(f"No change (alerted={was_alerted}, bad={bad})")

    state['last_aqi'] = obs['aqi']
    state['last_pollutant'] = obs['pollutant']
    state['last_category'] = obs['category']

    save_state(state)


if __name__ == '__main__':
    main()
