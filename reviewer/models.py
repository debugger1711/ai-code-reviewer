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
    review = models.OneToOneField(CodeReview, on_delete=models.CASCADE, related_name='result')
    
    # Original Code Info
    time_complexity = models.TextField(blank=True, null=True)
    space_complexity = models.TextField(blank=True, null=True)
    
    # 👇 NAYE COLUMNS 👇
    optimized_time_complexity = models.TextField(blank=True, null=True)
    optimized_space_complexity = models.TextField(blank=True, null=True)
    edge_cases = models.TextField(blank=True, null=True)
    test_cases = models.TextField(blank=True, null=True)
    dry_run = models.TextField(blank=True, null=True)
    
    bugs_detected = models.TextField(blank=True, null=True)
    optimization_suggestions = models.TextField(blank=True, null=True)
    code_quality_feedback = models.TextField(blank=True, null=True)
    optimized_code = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"AI Result for Review #{self.review.id}"