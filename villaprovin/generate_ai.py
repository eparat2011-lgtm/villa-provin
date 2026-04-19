#!/usr/bin/env python3
import os, base64, requests, time, json
from pathlib import Path

API_TOKEN = "r8_0w6rnfZlUKOZJtJlhSQsIsZ09yQrbmk274WjT"
MODEL_VERSION = "7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"
BASE = "/home/marian_rachow/.openclaw/workspace/villaprovin/backup_20260305/img/villaprovin"
OUT_DIR = Path("/home/marian_rachow/.openclaw/workspace/villaprovin/ai_images")
OUT_DIR.mkdir(exist_ok=True)

STYLE = "cinematic photography, golden hour lighting, luxury villa, South of France, Côte d'Azur, photorealistic, 8k, professional real estate photography, warm mediterranean light"
NEG = "blurry, distorted, ugly, deformed, low quality, cartoon, painting, drawing, overexposed"

IMAGES = [
    ("011-pool/pool-1.jpg",              "luxury infinity pool Côte d'Azur golden hour",           "ai_pool_1.jpg"),
    ("011-pool/pool-6.jpg",              "Mediterranean pool terrace sunset atmosphere",             "ai_pool_6.jpg"),
    ("010-view/view-1.jpg",              "panoramic Mediterranean sea view from villa terrace",      "ai_view_1.jpg"),
    ("010-view/view-2.jpg",              "Côte d'Azur aerial view golden light",                    "ai_view_2.jpg"),
    ("012-villa/villa-1.jpg",            "luxury Provençal villa exterior South of France",          "ai_villa_1.jpg"),
    ("002-kitchen/kitchen-1.jpg",        "modern luxury kitchen Provence natural light",             "ai_kitchen_1.jpg"),
    ("000-living-room/livingroom-1.jpg", "elegant living room Mediterranean villa",                 "ai_livingroom_1.jpg"),
    ("013-barbecue/barbecue-1.jpg",      "outdoor dining terrace Côte d'Azur evening",             "ai_barbecue_1.jpg"),
]

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
    "Prefer": "wait"
}

results = []

for src, prompt_base, out_name in IMAGES:
    src_path = Path(BASE) / src
    if not src_path.exists():
        print(f"SKIP (not found): {src}")
        results.append({"name": out_name, "status": "not_found"})
        continue

    print(f"\nProcessing: {src} -> {out_name}")
    
    # Encode image as base64 data URI
    with open(src_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    data_uri = f"data:image/jpeg;base64,{img_b64}"
    
    full_prompt = f"{prompt_base}, {STYLE}"
    
    payload = {
        "version": MODEL_VERSION,
        "input": {
            "prompt": full_prompt,
            "negative_prompt": NEG,
            "image": data_uri,
            "prompt_strength": 0.55,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 30,
            "disable_safety_checker": True,
            "apply_watermark": False
        }
    }
    
    try:
        resp = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=120
        )
        data = resp.json()
        
        if data.get("status") == "succeeded" and data.get("output"):
            url = data["output"][0] if isinstance(data["output"], list) else data["output"]
            print(f"  Got output URL: {url}")
            # Poll if needed
        elif data.get("id"):
            pred_id = data["id"]
            print(f"  Polling prediction {pred_id}...")
            for i in range(60):
                time.sleep(5)
                r2 = requests.get(
                    f"https://api.replicate.com/v1/predictions/{pred_id}",
                    headers={"Authorization": f"Token {API_TOKEN}"}
                )
                d2 = r2.json()
                status = d2.get("status")
                print(f"  Status: {status} ({i+1})")
                if status == "succeeded":
                    url = d2["output"][0] if isinstance(d2["output"], list) else d2["output"]
                    break
                elif status in ("failed", "canceled"):
                    print(f"  FAILED: {d2.get('error')}")
                    url = None
                    break
            else:
                url = None
        else:
            print(f"  ERROR: {json.dumps(data)[:200]}")
            url = None
        
        if url:
            # Download
            img_resp = requests.get(url, timeout=60)
            out_path = OUT_DIR / out_name
            with open(out_path, "wb") as f:
                f.write(img_resp.content)
            print(f"  Saved: {out_path} ({len(img_resp.content)//1024}KB)")
            results.append({"name": out_name, "status": "ok", "url": url, "path": str(out_path)})
        else:
            results.append({"name": out_name, "status": "failed"})
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append({"name": out_name, "status": "error", "error": str(e)})

print("\n=== RESULTS ===")
for r in results:
    print(json.dumps(r))

# Save results
with open(OUT_DIR / "results.json", "w") as f:
    json.dump(results, f, indent=2)
