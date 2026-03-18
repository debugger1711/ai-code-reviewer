import json
import os
from google import genai
from django.shortcuts import render, get_object_or_404
from .models import CodeReview, ReviewResult
from dotenv import load_dotenv

load_dotenv() 
API_KEY = os.environ.get("GEMINI_API_KEY")

def home_view(request):
    print("\n" + "="*50)
    print("👉 1. BROWSER NE BACKEND KO CALL KIYA!")
    
    if request.method == "POST":
        print("👉 2. USER NE FORM SUBMIT KIYA (POST REQUEST)!")
        
        user_code = request.POST.get('code_input')
        selected_language = request.POST.get('output_language', 'English')
        
        print(f"👉 3. LANGUAGE CHUNI GAYI: {selected_language}")
        print(f"👉 4. CODE JO BHEJA GAYA: '{user_code}'")
        
        # Check kar rahe hain ki code khali toh nahi hai
        if user_code and user_code.strip() != "":
            print("👉 5. CODE KHALI NAHI HAI, AI KO BHEJ RAHE HAIN... 🤖")
            try:
                review_instance = CodeReview.objects.create(code_input=user_code)
                client = genai.Client(api_key=API_KEY)
                
                # 👇 YAHAN NAYA STRICT PROMPT LAGA HAI 👇
                prompt = f"""
                You are an expert AI Code Reviewer. Analyze the code snippet.
                CRITICAL: Explanations MUST be in "{selected_language}" language.
                
                Code:
                {user_code}
                
                Provide the output ONLY in a valid JSON format. Escape all newlines (\\n) and quotes (\\") inside strings.
                
                CRITICAL FORMATTING INSTRUCTION FOR EDGE CASES, TEST CASES, AND DRY RUN:
                Do NOT write long paragraphs. Write them STRICTLY as code snippets where explanations are just inline comments (using // or #). Keep it extremely concise.
                
                Use exactly these keys:
                {{
                    "original_time_complexity": "O(?) - short",
                    "original_space_complexity": "O(?) - short",
                    "optimized_time_complexity": "O(?) - short",
                    "optimized_space_complexity": "O(?) - short",
                    "bugs_detected": "Bugs in {selected_language} or 'No bugs'",
                    "optimization_suggestions": "Suggestions in {selected_language}",
                    "code_quality_feedback": "Feedback in {selected_language}",
                    "optimized_code": "The full refactored code. CRITICAL: Remove ALL comments (//, #, /* */) from this code. Make it 100% comment-free.",
                    "edge_cases": "Write 2-3 edge cases as code. Example: \ncheck_empty([]) // Handles empty array input",
                    "test_cases": "Write 2-3 test cases as code. Example: \nassert solve(2) == 4 // Basic even number test",
                    "dry_run": "Write 1 dry run as step-by-step code. Example: \nval = 5 // Initial value \nval = val * 2 // Becomes 10"
                }}
                """
                
                print("👉 6. AI KA WAIT KAR RAHE HAIN... ⏳")
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                print("👉 7. AI NE JAWAB DE DIYA! JSON EXTRACT KAR RAHE HAIN...")
                ai_text = response.text
                cleaned_text = ai_text.replace('```json', '').replace('```', '').strip()
                ai_data = json.loads(cleaned_text)
                
                print("👉 8. DATABASE MEIN SAVE KAR RAHE HAIN...")
                result_obj = ReviewResult.objects.create(
                    review=review_instance,
                    time_complexity=ai_data.get('original_time_complexity', ''),
                    space_complexity=ai_data.get('original_space_complexity', ''),
                    optimized_time_complexity=ai_data.get('optimized_time_complexity', ''),
                    optimized_space_complexity=ai_data.get('optimized_space_complexity', ''),
                    edge_cases=ai_data.get('edge_cases', ''),
                    test_cases=ai_data.get('test_cases', ''),
                    dry_run=ai_data.get('dry_run', ''),
                    bugs_detected=ai_data.get('bugs_detected', ''),
                    optimization_suggestions=ai_data.get('optimization_suggestions', ''),
                    code_quality_feedback=ai_data.get('code_quality_feedback', ''),
                    optimized_code=ai_data.get('optimized_code', '')
                )
                
                print("👉 9. SUCCESS! SCREEN PAR RESULT BHEJ RAHE HAIN! 🎉")
                print("="*50 + "\n")
                return render(request, 'reviewer/home.html', {
                    'result': result_obj, 
                    'user_code': user_code
                })
                
            except Exception as e:
                print("\n🚨🚨🚨 ASLI ERROR YAHAN HAI 🚨🚨🚨")
                print(f"Error details: {e}")
                print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨\n")
                return render(request, 'reviewer/home.html', {'error': f"AI ya Database ka Error: {e}"})
        else:
            print("❌ ERROR: BHAII BOX KHALI THA! AI KO KYA BHEJU?")
            return render(request, 'reviewer/home.html', {'error': "Bhai code toh daalo pehle! Khali dabba review nahi ho sakta."})

    return render(request, 'reviewer/home.html')

def review_detail_view(request, review_id):
    review_instance = get_object_or_404(CodeReview.objects.select_related('result'), id=review_id)
    return render(request, 'reviewer/detail.html', {'review': review_instance})

def history_view(request):
    all_reviews = CodeReview.objects.all().select_related('result').order_by('-created_at')
    return render(request, 'reviewer/history.html', {'reviews': all_reviews})

def about_view(request):
    return render(request, 'reviewer/about.html')

def contact_view(request):
    return render(request, 'reviewer/contact.html')