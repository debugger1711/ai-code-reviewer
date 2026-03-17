import json
import os
from google import genai
from django.shortcuts import render, get_object_or_404
from .models import CodeReview, ReviewResult
from dotenv import load_dotenv

# .env file se secret data (API Key) load karna
load_dotenv() 

# Ab key direct nahi, .env file se aayegi
API_KEY = os.environ.get("GEMINI_API_KEY")

def home_view(request):
    print("👉 CHECK 1: Page load hua ya button daba!")
    
    if request.method == "POST":
        print("👉 CHECK 2: Form Submit hua")
        user_code = request.POST.get('code_input')
        
        # 👇 YAHAN CHANGE KIYA: User ki select ki hui language pakad rahe hain 👇
        selected_language = request.POST.get('output_language', 'English')
        
        if user_code:
            print("👉 CHECK 3: User ne code daala hai...")
            try:
                # 1. User code save karna
                review_instance = CodeReview.objects.create(code_input=user_code)
                print("👉 CHECK 4: CodeReview table mein data save ho gaya!")
                
                # 2. Naye Client ke sath AI setup
                client = genai.Client(api_key=API_KEY)
                
                # 👇 YAHAN CHANGE KIYA: Prompt mein selected language set kar di 👇
                prompt = f"""
                You are an expert AI Code Reviewer. Analyze the following code snippet.
                
                CRITICAL INSTRUCTION: You MUST write your explanations and feedback strictly in the "{selected_language}" language.
                
                Code to analyze:
                {user_code}
                
                Provide the output ONLY in a valid JSON format. Do not include any markdown formatting like ```json. Use these keys:
                {{
                    "time_complexity": "O(?) - keep it short",
                    "space_complexity": "O(?) - keep it short",
                    "bugs_detected": "explain any bugs found in {selected_language}, or say no bugs",
                    "optimization_suggestions": "how to make code faster/cleaner in {selected_language}",
                    "code_quality_feedback": "naming conventions, best practices in {selected_language}"
                }}
                """
                
                print(f"👉 CHECK 5: Naye AI ko request bhej rahe hain ({selected_language} ke liye)...")
                
                # 3. AI ko call karna
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
                
                return render(request, 'reviewer/home.html', {
                    'result': result_obj, 
                    'user_code': user_code
                })
                
            except Exception as e:
                print(f"❌❌❌ ERROR PAKDA GAYA: {e} ❌❌❌")
                return render(request, 'reviewer/home.html', {'error': f"AI Error: {e}"})

    return render(request, 'reviewer/home.html')


def review_detail_view(request, review_id):
    # ID ke hisaab se us specific code aur uske result ko dhoondhna
    review_instance = get_object_or_404(CodeReview.objects.select_related('result'), id=review_id)
    
    # Detail page par bhej dena
    return render(request, 'reviewer/detail.html', {'review': review_instance})


def history_view(request):
    # Database se saare review nikal rahe hain
    all_reviews = CodeReview.objects.all().select_related('result').order_by('-created_at')
    return render(request, 'reviewer/history.html', {'reviews': all_reviews})

# Yeh views.py ke aakhiri mein add karna hai
def about_view(request):
    return render(request, 'reviewer/about.html')

def contact_view(request):
    return render(request, 'reviewer/contact.html')