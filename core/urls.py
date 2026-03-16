from django.contrib import admin
from django.urls import path
from reviewer import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('history/', views.history_view, name='history'),
    # 👇 Yeh nayi line add karni hai 👇
    path('review/<int:review_id>/', views.review_detail_view, name='review_detail'), 
]