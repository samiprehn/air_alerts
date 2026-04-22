# Air Alerts

Polls [AirNow](https://www.airnow.gov/) hourly and sends an [ntfy](https://ntfy.sh/) push notification when the air quality in a given zip code crosses into unhealthy territory.

Alerts once per bad-air event. Stays quiet while air remains bad, and silences when it clears. No daily summaries, no forecasts — just a ping when it's time to close the windows.

## Fork this for your own zip code

1. **Fork this repo** (top right). Keep it public or make it private — up to you; the ntfy topic is the only thing worth keeping secret.
2. **Get a free AirNow API key** — sign up at [docs.airnowapi.org/login](https://docs.airnowapi.org/login), confirm email, log in, copy your key.
3. **Pick an ntfy topic** — any unique string, e.g. `air-alerts-yourname-randomchars`. No registration needed; just pick something nobody else would guess.
4. **Install ntfy on your phone** — [iOS](https://apps.apple.com/us/app/ntfy/id1625396347) or [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) — subscribe to your topic.
5. **Add repository secrets** (Settings → Secrets and variables → Actions → New repository secret):
   - `AIRNOW_API_KEY` — from step 2
   - `NTFY_TOPIC` — from step 3
   - `ZIP` — your 5-digit US zip code
   - `AQI_THRESHOLD` *(optional)* — AQI level that triggers an alert. Default `101`. Use `151` for Unhealthy-or-worse only, or `51` to be notified about any non-Good air.
6. **Allow the workflow to commit back** — Settings → Actions → General → Workflow permissions → Read and write permissions.
7. **Trigger a test run** — Actions tab → Check Air Quality → Run workflow.

## How "bad" is defined

| AQI | Category | |
|---|---|---|
| 0–50 | Good | |
| 51–100 | Moderate | |
| **101–150** | **Unhealthy for Sensitive Groups** | ← default threshold |
| 151–200 | Unhealthy | ntfy priority bumped to high |
| 201–300 | Very Unhealthy | |
| 301+ | Hazardous | |

The script pulls AQI for both PM2.5 and ozone from AirNow and uses whichever is worse.

## Files

- `check_air.py` — main script
- `seen.json` — tracks whether we've already alerted for the current bad-air event (auto-updated by the workflow)
- `.github/workflows/check.yml` — hourly GitHub Actions workflow

## Running locally

```
export AIRNOW_API_KEY=...
export NTFY_TOPIC=...
export ZIP=92117
python check_air.py
```

To force a test alert regardless of current AQI, set `AQI_THRESHOLD=0` for the run.
