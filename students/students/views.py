import datetime
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseForbidden

from .forms import StudentForm
from .models import Student, MyModel


def next_year(student_year):
    return student_year + datetime.timedelta(days=365)


class PromoteStudentView(LoginRequiredMixin, View):
    @staticmethod
    def post(request: Any, student_id: Any, student_year: Any = None):
        student = get_object_or_404(Student, id=student_id)

        if request.user.has_perm("can_promote_student"):
            for_return = HttpResponseForbidden("У вас нет прав для перевода студента")
        else:
            student.year = next_year(student_year)
            student.save()
            for_return = redirect("student:student_list")

        return for_return


class ExpelStudentView(LoginRequiredMixin, View):
    @staticmethod
    def post(request: Any, student_id: Any):
        student = get_object_or_404(Student, id=student_id)

        if request.user.has_perm("can_expel_student"):
            for_return = HttpResponseForbidden("У вас нет прав для исключения студента")
        else:
            student.delete()
            for_return = redirect("student:student_list")

        return for_return


class StudentListView(ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        if not self.request.user.has_perm("students.view_student"):
            for_return = Student.objects.all()
        else:
            for_return = Student.objects.none()

        return for_return


class StudentCreateView(CreateView):
    model = Student  # Указываем модель, с которой будет работать это представление
    # fields = ['first_name', 'last_name', 'year', 'email', 'enrollment_date',]
    form_class = StudentForm  # Указываем форму, которая будет использоваться для ввода данных
    template_name = 'students/student_form.html'  # Шаблон, который будет использоваться для отображения формы
    success_url = reverse_lazy(
        "students:student_list")  # URL, на который будет перенаправлен пользователь после успешной отправки формы


class StudentUpdateView(UpdateView):
    model = Student  # Указываем модель, с которой будет работать это представление
    # fields = ['first_name', 'last_name', 'year', 'email', 'enrollment_date', ]
    form_class = StudentForm  # Указываем форму, которая будет использоваться для ввода данных
    template_name = 'students/student_form.html'  # Шаблон, который будет использоваться для отображения формы
    success_url = reverse_lazy(
        "students:student_list")  # URL, на который будет перенаправлен пользователь после успешной отправки формы


class MyModelCreateView(CreateView):
    model = MyModel
    fields = ["name", "description"]
    template_name = "students/mymodel_form.html"
    success_url = reverse_lazy("students:mymodel_list")

    def form_valid(self, form):
        form.instance.create_by = self.request.user

        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        # response.context_data["error_message"] = "Пожалуйста, исправьте ошибки"

        return response


class MyModelDetailView(DetailView):
    model = MyModel
    template_name = "students/mymodel_detail.html"
    context_object_name = "mymodel"

    # def get_additional_data(self):
    #     return "Это дополнительная информация"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # # context["additional_data"] = "Это дополнительная информация"
        # context["additional_data"] = self.get_additional_data()

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404("Объект не найден")


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
        # 'student_year': student.get_year_display(),
    }
    return render(request, 'students/index.html', context)

# def student_detail(request, student_id):
#     student = Student.objects.get(id=student_id)
#     context = {'student': student}
#     return render(request, 'students/student_detail.html', context)
#
#
# def student_list(request):
#     students = Student.objects.all()
#     context = {'students': students}
#     return render(request, 'students/student_list.html', context)
