import google.generativeai as genai
import os
import PIL.Image

# 1. CONNECT THE KEY FROM THE SECURE VAULT
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("=========================================")
print("🏗️ QS MASTER: PHASE 1 VISION ACTIVE 🏗️")
print("=========================================")

def analyze_blueprint():
    # 2. LOAD THE UPLOADED BLUEPRINT
    try:
        img = PIL.Image.open('Floor Plan Jpeg.jpg')
    except Exception as e:
        print(f"❌ ERROR: Cannot find blueprint: {e}")
        return

    # 3. THE "EYE 1" COMMAND (Psychologically Optimized)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = """
    Act as a Senior Quantity Surveyor and AI Data Scientist. 
    Analyze the attached AutoCAD-generated PDF/JPEG. 
    1. Identify the 'Master Dimensions' (External Width and Length).
    2. Extract/Calculate the Total Internal Floor Area (m2).
    3. Extract/Calculate the Total External Perimeter (m).
    
    CRITICAL: Cross-check the numbers against the room dimensions (e.g. HALL 528X372).
    If any calculation feels inconsistent, flag it.
    
    Output format:
    AREA: [number]
    PERIMETER: [number]
    NOTES: [any spatial observations]
    """

    print("🔎 Eye #1 (Gemini) is scanning...")
    response = model.generate_content([prompt, img])
    
    # 4. SHADOW LEARNING LOG (This saves the data for our future custom model)
    print("📂 Saving to Shadow-Vault for custom training...")
    # (In Phase 2, this will push the image + result to your Supabase training table)
    
    print("\n✅ EXTRACTION RESULTS:")
    print(response.text)

if __name__ == "__main__":
    analyze_blueprint()
