from django.urls import path
from .views import createUser
from .views import listUser, loginUser, profile,update_profile, logout
urlpatterns = [
    path('create/', createUser, name='create'),
    path('list/', listUser, name='listUser'),
    path('login/', loginUser, name='loginUser'),
    path('profile/', profile, name='profilePage'),
    path('update/', update_profile, name='updateProfile'),
    path('logout/', logout, name='logoutUser')
]