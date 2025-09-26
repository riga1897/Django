from django.http import HttpResponse
from django.shortcuts import render
from .models import Student


def show_data(request):
    if request.method != "GET":
        return None
    return render(request, "app/data.html")


def submit_data(request):
    # Обработка данных формы
    if request.method != "POST":
        return None
    return HttpResponse("Данные отправлены!")


def show_item(request, item_id):
    return render(request, "app/item.html", {"item_id": item_id})


# def students_list(request):
#     return None


def about(request):
    return render(request, "students/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        return HttpResponse(f"Спасибо, {name}! Ваше сообщение: {message} получено.")

    return render(request, "students/contact.html")


def example_view(request):
    return render(request, 'students/example.html')


def index(request):
    student: Student = Student.objects.get(id=1)
    context = {
        'student_name': f"{student.first_name} {student.last_name}",
        'student_year': student.get_year_display(),
    }
    return render(request, 'students/index.html', context)


def student_detail(request):
    student = Student.objects.get(id=1)
    context = {'student': student}
    return render(request, 'students/student_detail.html', context)
