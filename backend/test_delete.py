import requests
import json

# 1. Fetch recent predictions
res = requests.get("http://localhost:8000/predictions")
preds = res.json().get("predictions", [])
print(f"Current prediction count: {len(preds)}")

if preds:
    target_id = preds[0]["id"]
    print(f"Attempting to delete prediction #{target_id}...")
    del_res = requests.delete(f"http://localhost:8000/predictions/{target_id}")
    print("Delete response:", del_res.json())

    # 2. Verify deletion
    res_after = requests.get("http://localhost:8000/predictions")
    preds_after = res_after.json().get("predictions", [])
    print(f"Prediction count after deletion: {len(preds_after)}")
