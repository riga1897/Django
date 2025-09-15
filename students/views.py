from django.shortcuts import render
from django.http import HttpResponse

def show_data(request):
    if request.method != 'GET':
        return None
    return render(request, 'app/data.html')


def submit_data(request):
    # Обработка данных формы
    if request.method != 'POST':
        return None
    return HttpResponse("Данные отправлены!")

def show_item(request, item_id):
    return render(request, "app/item.html", {"item_id": item_id})


def students_list(request):
    return None


def about(request):
    return render(request, "students/about.html")
