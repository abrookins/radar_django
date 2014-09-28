from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {'request': request, 'user': request.user})


def compare(request, lon, lat):
    return render(request, 'compare_location.html', {
        'request': request,
        'user': request.user,
        'longitude': lon,
        'latitude': lat
    })
