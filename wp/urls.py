from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('receiver.urls')),
    path('', include('receiver.urls')),  # This will catch the root URL
]

