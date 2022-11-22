from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="newlisting"),
    path("listing/<int:listing_id>",views.listing_page,name="listing"),
    path("listing/<int:listing_id>/bid", views.bidding, name="bidding"),
    path("listing/<int:listing_id>/watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/closeauction", views.close_auction, name="close_auction")
]
