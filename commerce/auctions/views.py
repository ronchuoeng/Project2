from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Category


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
    description = forms.CharField(label="Description", widget=forms.Textarea)
    s_bid = forms.DecimalField(label="Starting Bid", max_digits=8, decimal_places=2, validators=[MinValueValidator(0.05),MaxValueValidator(99999999)])
    img = forms.URLField(label="Image")
    category = forms.ModelChoiceField(label="Category", required=False, queryset=Category.objects.all() , widget=forms.Select())

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
            return render(request, "auctions/listing.html")
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
    return render(request, "auctions/listing.html",{
        "listing": listing 
    })