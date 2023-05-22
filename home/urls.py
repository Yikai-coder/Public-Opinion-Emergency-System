from django.urls import path
# from django.contrib.auth.decorators import login_required
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='default_home'),
    path('<int:uid>/', views.HomeView.as_view(), name='home')
    # path('login_request/', views.LoginView.login_request, name='login_request')
    # path('', views.index, name="index")
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
