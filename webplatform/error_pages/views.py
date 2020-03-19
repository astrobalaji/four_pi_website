from django.shortcuts import render

# Create your views here.
def handler404(request, exception):
    return render(request, '404_page.html', status = 404)

def handler500(request):
    return render(request, 'Other_errors.html', status=500)

def handler502(request, exception):
    return render(request, 'Other_errors.html', status = 502)
