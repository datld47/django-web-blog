from django.urls import path
from . import views


urlpatterns = [
    path("",views.StartingPageView.as_view(),name="starting-page"),
    path("login",views.LoginFormView.as_view(),name="login-page"),
    path("register",views.RegiserFormView.as_view() , name="register-page"),
    path("hello",views.HelloView.as_view() , name="hello-page")
    # path("posts/<slug:slug>",views.SinglePostView.as_view(),name="post-detail-page"),   #/posts/my-first-post
    # path("read-later",views.ReadLaterView.as_view(),name='read-later')
]
