from django.urls import path
from . import views

urlpatterns = [
    path('upload-testimonial-image/', views.upload_testimonial_image, name='upload_testimonial_image'),
]