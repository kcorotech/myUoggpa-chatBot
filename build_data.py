import csv, json, urllib.request, io, os

# 🔴 PASTE YOUR SHEET IDs HERE:
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
        # Check all keys to avoid spacing issues
        keys = list(row.keys())
        if len(keys) >= 2 and str(row.get(keys[0], "")).strip().lower() == "version":
            version_num = float(row.get(keys[1], 0.0))

    # 2. Get Variables (Foolproof: grabs whatever is in Col A and Col B)
    vars_data = get_csv(sheet_id, "Variables")
    variables = {}
    for row in vars_data:
        keys = list(row.keys())
        if len(keys) >= 2:
            var_name = str(row.get(keys[0], "")).strip()
            var_value = str(row.get(keys[1], "")).strip()
            if var_name:
                variables[var_name] = var_value

    # 2.5 Get Programs and auto-build the JSON strings
    try:
        programs_data = get_csv(sheet_id, "Programs")
        undergrad, grad, doc = [], [], []
        for row in programs_data:
            keys = list(row.keys())
            if len(keys) >= 5:
                lvl = str(row.get(keys[0], "")).strip().upper()
                prog_obj = {
                    "d": str(row.get(keys[1], "")).strip(),
                    "p": str(row.get(keys[2], "")).strip(),
                    "f": str(row.get(keys[3], "")).strip(),
                    "t": str(row.get(keys[4], "")).strip()
                }
                # Sort them into the right buckets
                if "UNDER" in lvl: undergrad.append(prog_obj)
                elif "GRAD" in lvl: grad.append(prog_obj)
                elif "DOC" in lvl or "PHD" in lvl: doc.append(prog_obj)
        
        # Inject them directly into the variables dictionary!
        if undergrad: variables["[DATA_UNDERGRAD]"] = json.dumps(undergrad, ensure_ascii=False)
        if grad: variables["[DATA_GRADUATE]"] = json.dumps(grad, ensure_ascii=False)
        if doc: variables["[DATA_DOCTORATE]"] = json.dumps(doc, ensure_ascii=False)
    except Exception as e:
        print("No Programs tab found, skipping...")

    try:
        drives_data = get_csv(sheet_id, "Drives")
        drives_list = []
        for row in drives_data:
            keys = list(row.keys())
            if len(keys) >= 4 and str(row.get(keys[0], "")).strip() != "":
                drives_list.append({
                    "d": str(row.get(keys[0], "")).strip(), # Department
                    "s": str(row.get(keys[1], "")).strip(), # Semester
                    "n": str(row.get(keys[2], "")).strip(), # Name
                    "l": str(row.get(keys[3], "")).strip()  # Link
                })
        
        if drives_list: 
            variables["[DATA_DRIVES]"] = json.dumps(drives_list, ensure_ascii=False)
    except Exception as e:
        print("No Drives tab found, skipping...")
    # 👆👆👆 END OF NEW BLOCK 👆👆👆
    
    # 3. Get Intents
    intents_data = get_csv(sheet_id, "Intents")
    intents = []
    for row in intents_data:
        keys = list(row.keys())
        if len(keys) >= 4:
            is_active = str(row.get(keys[0], "")).strip().upper()
            if is_active == "TRUE":
                raw_keywords = str(row.get(keys[2], "")).split(",")
                clean_keywords = [k.strip() for k in raw_keywords if k.strip()]
                intents.append({
                    "intent": str(row.get(keys[1], "")).strip(),
                    "keywords": clean_keywords,
                    "response": str(row.get(keys[3], "")).strip()
                })

    final_data = {
        "version": version_num,
        "variables": variables,
        "intents": intents
    }

    os.makedirs("public", exist_ok=True)

    # ensure_ascii=False keeps the real emojis!
    with open(f"public/{prefix}_uogData.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    with open(f"public/{prefix}_version.json", "w", encoding="utf-8") as f:
        json.dump({"version": version_num}, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {prefix.upper()} built successfully! Version: {version_num}")

# Run for DEV
if DEV_SHEET_ID and DEV_SHEET_ID != "YOUR_DEV_SHEET_ID_HERE":
    build_json_for_env(DEV_SHEET_ID, "dev")

# Run for PROD
if PROD_SHEET_ID and PROD_SHEET_ID != "YOUR_PROD_SHEET_ID_HERE":
    build_json_for_env(PROD_SHEET_ID, "prod")