from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:id>", views.watchlist, name="watchlist"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("listing/<int:id>/bid", views.bid, name="bid"),
    path("listing/<int:id>/comment", views.comment, name="comment"),
    path("listing/<int:id>/close", views.close, name="close"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category")
]
