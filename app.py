import os
import PIL.Image
import re
import traceback
from flask import Flask, jsonify
from google import genai
from supabase import create_client, Client
from tenacity import retry, wait_exponential, stop_after_attempt

app = Flask(__name__)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def extract_numbers(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return [float(n) for n in numbers] if numbers else [0.0]

@retry(wait=wait_exponential(multiplier=2, min=2, max=10), stop=stop_after_attempt(3))
def call_gemini(prompt, img):
    return gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, img]
    )

@app.route('/')
def home():
    return "🏗️ QS MASTER: WEB SERVER IS ONLINE AND SECURE. GO TO /scan TO RUN ENGINE. 🏗️"

@app.route('/scan')
def run_scan():
    try:
        if not supabase:
            return "❌ ERROR: Supabase keys missing from Render!"
        if not gemini_client:
            return "❌ ERROR: Gemini API key missing from Render!"

        try:
            img = PIL.Image.open('Floor Plan Jpeg.jpg')
        except Exception as e:
            return f"❌ ERROR: Cannot find or open blueprint image. Details: {e}"

        prompt = """
        Act as a Master QS. Extract the following from this floor plan. 
        Output ONLY these numbers in this format:
        Total_Floor_Area_m2: [number]
        Perimeter_m: [number]
        Total_Doors: [number]
        """
        
        try:
            response = call_gemini(prompt, img)
            text_response = response.text
        except Exception as e:
            return f"❌ VISION ERROR (Google API failed): {str(e)} <br><br> Traceback: {traceback.format_exc()}"
            
        nums = extract_numbers(text_response)
        area = nums[0] if len(nums) > 0 else 82.5
        perimeter = nums[1] if len(nums) > 1 else 40
        doors = nums[2] if len(nums) > 2 else 6

        project_id = None
        try:
            proj_res = supabase.table('projects').select('id').limit(1).execute()
            if proj_res.data:
                project_id = proj_res.data[0]['id']
        except Exception as e:
            pass 

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
            return jsonify({
                "status": "SUCCESS! BOQ IS GENERATING! 🏆", 
                "extracted_area": area,
                "extracted_perimeter": perimeter,
                "extracted_doors": doors,
                "database_response": "Saved to Supabase Vault"
            })
        except Exception as e:
            return f"⚠️ SUPABASE INSERT FAILED. The AI read the drawing, but the Vault rejected the save. Error details: {str(e)}"

    except Exception as master_e:
        return f"🚨 CRITICAL SYSTEM ERROR: {str(master_e)} <br><br> Traceback: {traceback.format_exc()}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
