import os
import PIL.Image
import re
from google import genai
from supabase import create_client, Client

print("==================================================")
print("🏗️ QS MASTER: VISION-TO-SUPABASE UPLINK ACTIVE 🏗️")
print("==================================================")

# 1. IGNITION KEYS
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY)

# Connect to the Master Calculator (Supabase)
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ SUPABASE UPLINK: CONNECTED")
else:
    print("⚠️ SUPABASE UPLINK: OFFLINE (Missing Keys)")

def extract_numbers(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return [float(n) for n in numbers] if numbers else [0.0]

def run_vision_and_uplink():
    try:
        img = PIL.Image.open('Floor Plan Jpeg.jpg')
    except Exception as e:
        print(f"❌ ERROR: Cannot find blueprint: {e}")
        return

    # PHASE 1: THE EYES (Flash)
    print("🔎 EYE #1 (Gemini Flash) is scanning the blueprint...")
    prompt = """
    Act as a Master QS. Extract the following from this floor plan. 
    Output ONLY these numbers in this format:
    Total_Floor_Area_m2: [number]
    Perimeter_m: [number]
    Total_Doors: [number]
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        print("\n✅ EXTRACTION COMPLETE:")
        print(response.text)
        
        # Grab the raw numbers
        nums = extract_numbers(response.text)
        area = nums[0] if len(nums) > 0 else 82.5
        perimeter = nums[1] if len(nums) > 1 else 40
        doors = nums[2] if len(nums) > 2 else 6
        
    except Exception as e:
        print(f"Vision Error: {e}")
        return

    # PHASE 2: THE COURIER (Sending to Supabase)
    print("\n🚀 TRANSMITTING DATA TO SUPABASE OMEGA-21 ENGINE...")
    
    payload = {
        "file_name": "Live_Scan_Alpha",
        "metadata": {
            "total_floor_area_m2": area,
            "perimeter_m": perimeter,
            "total_doors": doors,
            "levels": 1,
            "structural_concrete_m3": area * 0.1, 
            "has_curved_walls": False
        }
    }
    
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            data, count = supabase.table('drawings').insert(payload).execute()
            print("✅ DATA SECURE IN SUPABASE VAULT!")
            print("➡️ Awaiting Edge Function Trigger to generate BOQ...")
        except Exception as e:
            print(f"⚠️ Supabase Insert Failed: {e}")
    else:
        print("Payload Ready (Add Supabase Keys to transmit):", payload)

if __name__ == "__main__":
    run_vision_and_uplink()
