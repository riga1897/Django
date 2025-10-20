from .models import Student, Grade

class StudentService:

    @staticmethod
    def get_full_name(student_id):
        # Получаем полное имя студента по его ID
        student = Student.objects.get(id=student_id)
        return f"{student.first_name} {student.last_name}"

    @staticmethod
    def calculate_average_grade(student_id):
        # Получаем все оценки студента
        grades = Grade.objects.filter(student_id=student_id)
        # Если оценок нет, возвращаем None
        if not grades.exists():
            return None
        # Вычисляем сумму всех оценок
        total_score = sum(grade.score for grade in grades)
        # Вычисляем средний балл
        average_score = total_score / grades.count()
        return average_score

    @staticmethod
    def has_passed(student_id, passing_score=60):
        # Вычисляем средний балл студента
        average_grade = StudentService.calculate_average_grade(student_id)
        # Если средний балл не вычислен (нет оценок), возвращаем False
        if average_grade is None:
            return False
        # Проверяем, сдал ли студент предмет (средний балл >= проходному баллу)
        return average_grade >= passing_score
