from django.contrib import admin
from .models import CodeReview, ReviewResult # ReviewResult ko yahan import kiya

admin.site.register(CodeReview)
admin.site.register(ReviewResult) # Yahan register kar diya