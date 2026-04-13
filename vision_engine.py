import google.generativeai as genai
import os

print("=========================================")
print("🏗️ QS MASTER: VISION ENGINE INITIATED 🏗️")
print("=========================================")

# 1. AUTHENTICATE THE BRAIN (API Key goes here later)
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. THE PROMPT (Commanding the AI)
prompt = """
Act as an elite Quantity Surveyor. Review the attached architectural floor plan.
Extract the overall external width and length (in meters).
Then, calculate the Total Floor Area (sqm) and the Total External Perimeter (m).
Output ONLY the raw numbers in this format:
Area: [number]
Perimeter: [number]
"""

print("✅ SCRIPT READY. WAITING FOR BLUEPRINT AND API KEY TO IGNITE.")
print("=========================================")
