from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Category, Bidding, Watchlist, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Create the form of New Listing by user.
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField(label="Description",max_length=1000, widget=forms.Textarea)
    s_bid = forms.DecimalField(label="Starting Bid", max_digits=8, decimal_places=2, validators=[MinValueValidator(0.05),MaxValueValidator(99999999)])
    img = forms.URLField(label="ImageUrl", initial="https://")
    category = forms.ModelChoiceField(label="Category", required=False, queryset=Category.objects.all().order_by('title'), widget=forms.Select())


def new_listing(request):
    # 1. POST the new listing by user. 
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            newlisting = Listing(
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                s_bid = form.cleaned_data["s_bid"],
                img = form.cleaned_data["img"],
                category = form.cleaned_data["category"],
                seller = request.user
            )
            newlisting.save()      
            return HttpResponseRedirect(reverse("listing", args=(newlisting.id,)))
        else:
            return render(request, "auctions/newlisting.html", {
                "form": form
            })
    # 2. GET the page.       
    return render(request, "auctions/newlisting.html", {
        "form": NewListingForm()
    })


def listing_page(request,listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except ObjectDoesNotExist:
        return HttpResponse("The listing doesn't exist or has already expired.")
    comments = Comment.objects.filter(listing=listing)
    # If not login.
    if not request.user.is_authenticated:
        return render(request, ("auctions/listing.html"), {
            "listing": listing,
            "bidding": PlaceBidForm(),
            "comments": comments
        }) 
    # If login.
    user = User.objects.get(pk=request.user.id)
    # Display different watchlist button according to watchlist
    if user.watchers.exists():
        watcher = Watchlist.objects.get(user=user)
        return render(request, ("auctions/listing.html"), {
            "watcher": watcher.listings.all(),
            "listing": listing,
            "bidding": PlaceBidForm(),
            "comments": comments
        })
    else:
        return render(request, ("auctions/listing.html"), {
            "listing": listing,
            "bidding": PlaceBidForm(),
            "comments": comments
        })


class PlaceBidForm(forms.Form):
    bid = forms.DecimalField(label="Place Bid", max_digits=8, decimal_places=2, validators=[MinValueValidator(0.05),MaxValueValidator(99999999)])


@login_required(login_url="login")
def bidding(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        form = PlaceBidForm(request.POST)
        if form.is_valid():
            bidding = Bidding(
                bidder=request.user, 
                bid_price=form.cleaned_data["bid"]
                )
            if listing.c_off == None:
                if bidding.bid_price >= listing.s_bid:
                    listing.c_off = bidding
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bidding": form,
                        "message": "Your bid should higher than the Starting Bid/Current Offer."
                    })
            else: 
                if bidding.bid_price > listing.c_off.bid_price:
                    listing.c_off = bidding
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bidding": form,
                        "message": "Your bid should higher than the Starting Bid/Current Offer."
                    })
            bidding.save()
            listing.save() 
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required(login_url="login")
def watchlist(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk=request.user.id)
        # 1. Check the user has a watchlist or not, if has
        if user.watchers.exists():
            watcher = Watchlist.objects.get(user=user)
            # The function to add or remove the listing watchlist.
            if listing in watcher.listings.all():
                watcher.listings.remove(listing)
            else:
                watcher.listings.add(listing)
        else:
        # 2. If no, Create a watchlist for user, then add the listing to watchlist.
            watcher = Watchlist.objects.create(user=user)
            watcher.listings.add(listing)

        return HttpResponseRedirect(reverse("listing", args=[listing.id,]))


@login_required(login_url="login")
def watchlist_view(request):
    user = User.objects.get(pk=request.user.id)
    if user.watchers.exists():
        # If user's have a watchlist
        watchlist = Watchlist.objects.get(user=user)
    else:
        # If don't have
        return HttpResponse("You don't have a watchlist yet.")
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist.listings.all()
    })

       
def close_auction(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.active = False
        listing.save()

        return HttpResponseRedirect(reverse("listing", args=[listing.id,]))


@login_required(login_url="login")
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk=request.user.id)
        new_comment = Comment(
            listing=listing, 
            user=user, 
            comment=request.POST["comment"]
            )
        new_comment.save()
            
        return HttpResponseRedirect(reverse("listing", args=[listing.id,]))


def categories(request):
    categories = Category.objects.all().order_by('title')

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request,category_id):
    category = Category.objects.get(pk=category_id)
    listing = Listing.objects.filter(category=category)

    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listing
    })
