from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView

from .models import Student, MyModel


class MyModelCreateView(CreateView):
    model = MyModel
    fields = ["name", "description"]
    template_name = "students/mymodel_form.html"
    success_url = reverse_lazy("students:mymodel_list")

class MyModelListView(ListView):
    model = MyModel
    template_name = "students/mymodel_list.html"
    context_object_name = "mymodels"


class MyModelDetailView(DetailView):
    model = MyModel
    template_name = "students/mymodel_detail.html"
    context_object_name = "mymodel"


class MyModelUpdateView(UpdateView):
    model = MyModel
    fields = ["name", "description"]
    template_name = "students/mymodel_form.html"
    success_url = reverse_lazy("students:mymodel_list")


class MyModelDeleteView(DeleteView):
    model = MyModel
    template_name = "students/mymodel_confirm_delete.html"
    success_url = reverse_lazy("students:mymodel_list")


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


def student_detail(request, student_id):
    student = Student.objects.get(id=student_id)
    context = {'student': student}
    return render(request, 'students/student_detail.html', context)


def student_list(request):
    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'students/student_list.html', context)
