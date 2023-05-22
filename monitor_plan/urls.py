from django.urls import path
# from django.contrib.auth.decorators import login_required
from . import views

app_name = 'monitor_plan'
urlpatterns = [
    path('delete/', views.plan_delete, name='plan_delete'),
    path('details/<int:pk>/', views.PlanView.as_view(), name='monitor_plan'),
    path('modify/<int:pk>/', views.ModifyView.as_view(), name='modify'),
    path('add/', view=views.AddView.as_view(), name='add')
    # path('<int:uid>/', views.HomeView.as_view(), name='home')
    # path('login_request/', views.LoginView.login_request, name='login_request')
    # path('', views.index, name="index")
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
