from django.urls import path
# from django.contrib.auth.decorators import login_required
from . import views

app_name = 'hotsearch_analysis'
urlpatterns = [
    path('', views.HotSearchAnalysisView.as_view(), name='hotsearch_analysis'),
    path('<int:days>/<int:pk>/', views.HotSearchAnalysisView.as_view(), name='hotsearch_analysis'),
    path('details/<int:pk>/', views.HotsearchDetailView.as_view(), name='hotsearch_detail'),
    path('trace/', views.trace_hotsearch, name='trace hotsearch'),
    path('trend/', views.HotsearchTrendView.as_view(), name='hotsearch trend')
    # path('<int:uid>/', views.HomeView.as_view(), name='home')
    # path('login_request/', views.LoginView.login_request, name='login_request')
    # path('', views.index, name="index")
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
