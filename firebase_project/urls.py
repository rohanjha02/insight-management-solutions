from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('display_data.urls')),  # Include the URLs of the display_data app
]
