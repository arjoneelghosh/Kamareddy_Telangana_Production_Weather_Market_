"""Run March 2026 forecast for multiple crops against the live backend."""
import requests, json

base = "http://127.0.0.1:8000"

crops = [
    {"commodity": "tomato",        "district": "Hyderabad",   "month": 3, "year": 2026},
    {"commodity": "paddy",         "district": "Warangal",    "month": 3, "year": 2026},
    {"commodity": "cotton",                                   "month": 3, "year": 2026},
    {"commodity": "maize",         "district": "Karimnagar",  "month": 3, "year": 2026},
    {"commodity": "red gram",      "district": "Adilabad",    "month": 3, "year": 2026},
    {"commodity": "bengal gram",   "district": "Nizamabad",   "month": 3, "year": 2026},
    {"commodity": "chillies(dry)", "district": "Khammam",     "month": 3, "year": 2026},
]

print("=" * 72)
print("  AGRIFORE — March 2026 Price Predictions")
print("  Model: M2 Base XGBoost  |  Date: 2026-03-17")
print("=" * 72)
print()

results = []
for payload in crops:
    r = requests.post(f"{base}/predict-price", json=payload)
    loc = payload.get("district", "Statewide")
    label = f"{payload['commodity'].title()} / {loc}"
    entry = {"label": label, "status": r.status_code, "response": r.json(), "input": payload}
    results.append(entry)

    if r.status_code == 200:
        d = r.json()
        price = d["predicted_price"]
        conf  = d["confidence"]
        strategy = {0.85: "XGBoost model", 0.7: "2024 CSV fallback", 0.5: "Historical avg"}
        strat = strategy.get(conf, f"conf={conf}")
        print(f"  {label:40s}  =>  Rs {price:>7,}/qtl   [{strat}]")
    else:
        detail = r.json().get("detail", "unknown error")
        print(f"  {label:40s}  =>  FAILED ({r.status_code}: {detail})")

print()
print("=" * 72)

# Save
with open(r"C:\Users\footb\Desktop\AgriFore\march2026_forecast.json", "w") as f:
    json.dump(results, f, indent=2)
print("Results saved to march2026_forecast.json")
