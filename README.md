# Relevancy Check App

Monitors project alert emails (BTG/Catalant), scores consultant relevancy using Claude, sends match emails, and stores results in MongoDB.

## Run locally

1. Create `.env` with required values.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start monitor:
   - `python evaluator.py`

## Test mode

- `python evaluator.py --test`
- Uses sample JD and (by default) does not send test emails.
