import json
from google import genai
from django.shortcuts import render, get_object_or_404
from .models import CodeReview, ReviewResult

# ⚠️ YAHAN APNI ASLI API KEY DAALNA (Quotes "" ke andar)
import os
from dotenv import load_dotenv

# .env file se secret data load karna
load_dotenv() 

# Ab key direct nahi, .env file se aayegi
API_KEY = os.environ.get("GEMINI_API_KEY")

def home_view(request):
    print("👉 CHECK 1: Page load hua ya button daba!")
    
    if request.method == "POST":
        print("👉 CHECK 2: Form Submit hua")
        user_code = request.POST.get('code_input')
        
        if user_code:
            print("👉 CHECK 3: User ne code daala hai...")
            try:
                # 1. User code save karna
                review_instance = CodeReview.objects.create(code_input=user_code)
                print("👉 CHECK 4: CodeReview table mein data save ho gaya!")
                
                # 2. Naye Client ke sath AI setup
                client = genai.Client(api_key=API_KEY)
                
                prompt = f"""
                Aap ek expert AI Code Reviewer ho. Niche diye gaye Python code ko analyze karo:
                
                {user_code}
                
                Aur mujhe sirf aur sirf ek valid JSON format me result do (uske alawa koi text mat likhna). Format yeh hona chahiye:
                {{
                    "time_complexity": "O(?)",
                    "space_complexity": "O(?)",
                    "bugs_detected": "koi bug hai toh batao warna likho no bugs",
                    "optimization_suggestions": "code ko fast ya clean kaise karein",
                    "code_quality_feedback": "naming conventions, PEP8 rules etc"
                }}
                """
                
                print("👉 CHECK 5: Naye AI ko request bhej rahe hain (gemini-2.5-flash)...")
                
                # 3. AI ko call karna (Aapki list wala model use kar rahe hain)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                print("👉 CHECK 6: AI ka response wapas aa gaya!")
                
                ai_text = response.text
                cleaned_text = ai_text.replace('```json', '').replace('```', '').strip()
                ai_data = json.loads(cleaned_text)
                
                # 4. Result save karna
                result_obj = ReviewResult.objects.create(
                    review=review_instance,
                    time_complexity=ai_data.get('time_complexity', ''),
                    space_complexity=ai_data.get('space_complexity', ''),
                    bugs_detected=ai_data.get('bugs_detected', ''),
                    optimization_suggestions=ai_data.get('optimization_suggestions', ''),
                    code_quality_feedback=ai_data.get('code_quality_feedback', '')
                )
                print("👉 CHECK 7: Chamatkar! Sab kuch database mein save ho gaya! 🎉")
                
                return render(request, 'reviewer/home.html', {'result': result_obj, 'user_code': user_code})
                
            except Exception as e:
                print(f"❌❌❌ ERROR PAKDA GAYA: {e} ❌❌❌")
                return render(request, 'reviewer/home.html', {'error': f"AI Error: {e}"})

    return render(request, 'reviewer/home.html')



# ... (Aapka purana code yahan rahega) ...

def review_detail_view(request, review_id):
    # ID ke hisaab se us specific code aur uske result ko dhoondhna
    review_instance = get_object_or_404(CodeReview.objects.select_related('result'), id=review_id)
    
    # Detail page par bhej dena
    return render(request, 'reviewer/detail.html', {'review': review_instance})

# Yeh views.py ke aakhiri mein aayega
def history_view(request):
    # Database se saare review nikal rahe hain
    all_reviews = CodeReview.objects.all().select_related('result').order_by('-created_at')
    return render(request, 'reviewer/history.html', {'reviews': all_reviews})