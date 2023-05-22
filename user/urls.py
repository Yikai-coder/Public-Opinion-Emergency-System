from django.urls import path

from . import views

app_name = 'login'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout')
    # path('login_request/', views.LoginView.login_request, name='login_request')
    # path('', views.index, name="index")
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
