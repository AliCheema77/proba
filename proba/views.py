from django.shortcuts import render

from proba.utility import login, ulla_bot, load_conf_file


def scrap_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        reset = request.POST.get("reset")
        followers = request.POST.get("followers")
        print('NAME', email, password, reset, followers)
        ulla_bot(email, password, reset, followers)
    return render(request, "proba.html")

