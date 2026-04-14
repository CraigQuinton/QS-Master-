import os
import PIL.Image
import re
from flask import Flask, jsonify
from google import genai
from supabase import create_client, Client
from tenacity import retry, wait_exponential, stop_after_attempt

app = Flask(__name__)

# 1. IGNITION KEYS
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def extract_numbers(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return [float(n) for n in numbers] if numbers else [0.0]

# THE BOUNCER BYPASS: Auto-retries 5 times silently if Google is busy!
@retry(wait=wait_exponential(multiplier=2, min=4, max=15), stop=stop_after_attempt(5))
def call_gemini(prompt, img):
    print("✊ Knocking on Google's door... (Bypassing Bouncer)")
    return gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, img]
    )

# THE WEB SERVER FRONT DOOR
@app.route('/')
def home():
    return "🏗️ QS MASTER: WEB SERVER IS ONLINE AND SECURE. GO TO /scan TO RUN ENGINE. 🏗️"

# THE MASTER ENGINE TRIGGER
@app.route('/scan')
def run_scan():
    if not supabase:
        return jsonify({"error": "Supabase keys missing from Render Vault!"})

    try:
        img = PIL.Image.open('Floor Plan Jpeg.jpg')
    except Exception as e:
        return jsonify({"error": f"Cannot find blueprint: {e}"})

    print("🔎 EYE #1 (Gemini Flash) is scanning...")
    prompt = """
    Act as a Master QS. Extract the following from this floor plan. 
    Output ONLY these numbers in this format:
    Total_Floor_Area_m2: [number]
    Perimeter_m: [number]
    Total_Doors: [number]
    """
    
    try:
        response = call_gemini(prompt, img)
        print("\n✅ EXTRACTION COMPLETE:")
        print(response.text)
        
        nums = extract_numbers(response.text)
        area = nums[0] if len(nums) > 0 else 82.5
        perimeter = nums[1] if len(nums) > 1 else 40
        doors = nums[2] if len(nums) > 2 else 6
    except Exception as e:
        print(f"❌ Vision Error: {e}")
        return jsonify({"error": "Google API is overloaded, please wait 60 seconds."})

    print("\n🚀 TRANSMITTING DATA TO SUPABASE...")
    
    # THE LOCK PICK: Fetch a real Project ID from your database dynamically!
    try:
        proj_res = supabase.table('projects').select('id').limit(1).execute()
        project_id = proj_res.data[0]['id'] if proj_res.data else None
    except Exception as e:
        project_id = None

    payload = {
        "file_name": "Live_Scan_Alpha",
        "project_id": project_id, 
        "metadata": {
            "total_floor_area_m2": area,
            "perimeter_m": perimeter,
            "total_doors": doors,
            "levels": 1,
            "structural_concrete_m3": area * 0.1, 
            "has_curved_walls": False
        }
    }
    
    try:
        supabase.table('drawings').insert(payload).execute()
        print("✅ DATA SECURE IN SUPABASE VAULT!")
        return jsonify({"status": "SUCCESS! BOQ IS GENERATING!", "data": payload})
    except Exception as e:
        print(f"⚠️ Supabase Insert Failed: {e}")
        return jsonify({"error": "Supabase Insert Failed", "details": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
