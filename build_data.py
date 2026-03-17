import csv, json, urllib.request, io

# 🔴 PASTE YOUR SHEET ID HERE:
SHEET_ID = "1Ws_W_sz2TJj5Et-r9LxcvkHMxozxHk_EkDLSdQMZagk/edit?gid=804247053#gid=804247053"

def get_csv(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    req = urllib.request.urlopen(url)
    return list(csv.DictReader(io.StringIO(req.read().decode('utf-8'))))

print("Fetching data from Google Sheets...")

# 1. Get Version Settings
settings_data = get_csv("Settings")
version_num = 0.0
for row in settings_data:
    if row.get("key") == "version":
        version_num = float(row.get("value"))

# 2. Get Variables
vars_data = get_csv("Variables")
variables = {}
for row in vars_data:
    if row.get("variable_name"):
        variables[row["variable_name"]] = row.get("value", "")

# 3. Get Intents
intents_data = get_csv("Intents")
intents = []
for row in intents_data:
    # Only grab it if isActive is TRUE
    if row.get("isActive", "").upper() == "TRUE":
        # Clean up keywords and split them by comma
        raw_keywords = row.get("keywords", "").split(",")
        clean_keywords = [k.strip() for k in raw_keywords if k.strip()]
        
        intents.append({
            "intent": row.get("intent", ""),
            "keywords": clean_keywords,
            "response": row.get("response", "")
        })

# Final JSON Structure
final_data = {
    "version": version_num,
    "variables": variables,
    "intents": intents
}

# Write uogData.json
with open("public/uogData.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2)

# Write version.json
with open("public/version.json", "w", encoding="utf-8") as f:
    json.dump({"version": version_num}, f, indent=2)

print(f"Success! Built version {version_num} with {len(intents)} active intents.")