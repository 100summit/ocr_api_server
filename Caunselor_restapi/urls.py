from django.contrib import admin
from django.urls import path, include
from ocrdatas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ocrdata', views.ocrdata_list),
    path('ttest', views.ttest),
    path('ocrUpload', views.ocr_upload),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]