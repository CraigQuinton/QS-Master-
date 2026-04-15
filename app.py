import os
import PIL.Image
import json
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

# THE BATTERING RAM: 10 Knocks. Relentless.
@retry(wait=wait_exponential(multiplier=2, min=4, max=15), stop=stop_after_attempt(10))
def call_gemini(prompt, img):
    print("✊ Knocking on Google's door... (Bypassing Bouncer)")
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

        # THE OMEGA 21 INJECTION PROMPT
        prompt = """
        Act as a Master Quantity Surveyor. Analyze this floor plan and extract the core measurements. 
        If a measurement isn't explicitly written, use your expert QS logic to estimate it based on standard building practices and the footprint area.
        You MUST return ONLY a raw JSON object. No markdown formatting, no explanations, just the JSON string matching exactly these keys:
        {
            "footprint_area_m2": 0,
            "total_floor_area_m2": 0,
            "total_wall_area_m2": 0,
            "roof_area_m2": 0,
            "total_window_area_m2": 0,
            "total_doors": 0,
            "perimeter_m": 0,
            "levels": 1,
            "plumbing_points": 0,
            "electrical_points": 0,
            "slab_concrete_mpa": 25,
            "structural_concrete_m3": 0,
            "steel_tonnage": 0,
            "demolition_m2": 0,
            "needs_piling": false,
            "piling_depth_m": 0,
            "roof_pitch_degrees": 15,
            "roof_type": "tiles",
            "sanitary_fittings": 0,
            "has_curved_walls": false
        }
        """
        
        try:
            response = call_gemini(prompt, img)
            text_response = response.text.strip()
            
            # Bulletproof JSON cleaner just in case Google adds formatting
            if text_response.startswith("```json"):
                text_response = text_response[7:-3].strip()
            elif text_response.startswith("```"):
                text_response = text_response[3:-3].strip()
                
            ai_data = json.loads(text_response)
            
        except Exception as e:
            return f"❌ VISION OR PARSING ERROR: {str(e)} <br><br> Traceback: {traceback.format_exc()}"

        project_id = None
        try:
            proj_res = supabase.table('projects').select('id').limit(1).execute()
            if proj_res.data:
                project_id = proj_res.data[0]['id']
        except Exception as e:
            pass 

        # Passing the FULL AI JSON directly into the Vault's Metadata!
        payload = {
            "file_name": "Live_Scan_Omega_21",
            "project_id": project_id, 
            "storage_path": "alpha_scans/floor_plan.jpg",
            "metadata": ai_data 
        }
        
        try:
            supabase.table('drawings').insert(payload).execute()
            return jsonify({
                "status": "SUCCESS! OMEGA 21 BOQ FUEL DELIVERED TO VAULT! 🏆", 
                "ai_extracted_data": ai_data,
                "database_response": "Saved to Supabase Vault. Edge Function is calculating BOQ now!"
            })
        except Exception as e:
            return f"⚠️ SUPABASE INSERT FAILED. Error details: {str(e)}"

    except Exception as master_e:
        return f"🚨 CRITICAL SYSTEM ERROR: {str(master_e)} <br><br> Traceback: {traceback.format_exc()}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
