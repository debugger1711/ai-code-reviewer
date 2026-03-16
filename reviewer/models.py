from django.db import models

class CodeReview(models.Model):
    # Yeh field user ka code save karega
    code_input = models.TextField()
    
    # Yeh automatically time save kar lega jab code submit hoga
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Code Snippet {self.id}"
    
    # Purana CodeReview class waise hi rehne dena
# Uske niche yeh naya class add karna:

class ReviewResult(models.Model):
    # Yeh naya table purane CodeReview table se juda hoga (OneToOne relation)
    review = models.OneToOneField(CodeReview, on_delete=models.CASCADE, related_name='result')
    
    # AI se jo feedback aayega usko alag-alag dabbon (fields) me save karenge
    time_complexity = models.CharField(max_length=100, blank=True)
    space_complexity = models.CharField(max_length=100, blank=True)
    bugs_detected = models.TextField(blank=True)
    optimization_suggestions = models.TextField(blank=True)
    code_quality_feedback = models.TextField(blank=True)
    
    def __str__(self):
        return f"AI Result for Review #{self.review.id}"