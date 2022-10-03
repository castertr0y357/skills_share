from django.urls import path, include
from . import views

app_name = 'church_skills'
urlpatterns = [
    # -------------------------------------Main and Search--------------------------------------------------------------
    # ex: /
    path('', views.MainView.as_view(), name='main'),
    # ex: /search_results/
    path('search_results', views.SearchView.as_view(), name='search_results'),
    # --------------------------------------Categories------------------------------------------------------------------
    # ex: /Categories/
    path('Categories/', views.CategoryListView.as_view(), name='category_list'),
    # ex: /Categories/Beef/
    path('Categories/<slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('Categories/<path:slug>', views.CategoryDetailView.as_view(), name='category_detail'),
    # -----------------------------------Profiles-----------------------------------------------------------------------
    # ex: /Profiles/
    path('Profiles/', views.ProfileListView.as_view(), name='profile_list'),
    # ex: /Profiles/admin/
    path('Profiles/<username>', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('Profiles/<path:username>', views.ProfileDetailView.as_view(), name='profile_detail'),
    # --------------------------------Authentication--------------------------------------------------------------------
    # ex: /login/
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/create_account/', views.CreateUserView.as_view(), name='create_user'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
