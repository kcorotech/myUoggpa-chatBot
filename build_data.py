import csv, json, urllib.request, io, os

# 🔴 PASTE YOUR TWO SHEET IDs HERE:
DEV_SHEET_ID = "1oZHa17ggoM2TQCd_xOnBds-xhLMasbZyKKFhicphSvY"
PROD_SHEET_ID = "1Ws_W_sz2TJj5Et-r9LxcvkHMxozxHk_EkDLSdQMZagk"

def get_csv(sheet_id, tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    req = urllib.request.urlopen(url)
    return list(csv.DictReader(io.StringIO(req.read().decode('utf-8'))))

def build_json_for_env(sheet_id, prefix):
    print(f"Building {prefix.upper()} environment...")
    
    # 1. Get Version
    settings_data = get_csv(sheet_id, "Settings")
    version_num = 0.0
    for row in settings_data:
        if row.get("key") == "version":
            version_num = float(row.get("value"))

    # 2. Get Variables
    vars_data = get_csv(sheet_id, "Variables")
    variables = {}
    for row in vars_data:
        if row.get("variable_name"):
            variables[row["variable_name"]] = row.get("value", "")

    # 3. Get Intents
    intents_data = get_csv(sheet_id, "Intents")
    intents = []
    for row in intents_data:
        if row.get("isActive", "").upper() == "TRUE":
            raw_keywords = row.get("keywords", "").split(",")
            clean_keywords = [k.strip() for k in raw_keywords if k.strip()]
            intents.append({
                "intent": row.get("intent", ""),
                "keywords": clean_keywords,
                "response": row.get("response", "")
            })

    final_data = {
        "version": version_num,
        "variables": variables,
        "intents": intents
    }

    # Ensure public folder exists
    os.makedirs("public", exist_ok=True)

    # Write Data JSON
    with open(f"public/{prefix}_uogData.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)

    # Write Version JSON
    with open(f"public/{prefix}_version.json", "w", encoding="utf-8") as f:
        json.dump({"version": version_num}, f, indent=2)
        
    print(f"✅ {prefix.upper()} built successfully! Version: {version_num}")

# Run for both environments
build_json_for_env(DEV_SHEET_ID, "dev")
build_json_for_env(PROD_SHEET_ID, "prod")