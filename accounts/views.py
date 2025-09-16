from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]  # Explicit backend
            login(request, user)
            messages.success(request, "Account created successfully! You are now logged in.")
            return redirect("shop:product_list")
        else:
            messages.error(request, "This email is already in use. Please use a different one.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
