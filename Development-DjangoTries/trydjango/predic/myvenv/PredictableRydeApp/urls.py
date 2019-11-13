from django.urls import path
from django.contrib import admin

from PredictableRydeApp import views as PredictableRydeApp_views

urlpatterns = [
 path('PredictableRyde/', PredictableRydeApp_views.PredictableRydeform),
 path('results/', PredictableRydeApp_views.PredictableRydeform),

path('', admin.site.urls),
]
