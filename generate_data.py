import os
import django
# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VEST.settings")
# Initialize Django
django.setup()
import random
from django.contrib.auth.models import User, Group
from users.models import Profile, Student, School
from vocational.models import *

import random
import string
from datetime import date, timedelta

from faker import Faker
fake = Faker()
import gender_guesser.detector as gender
gd = gender.Detector()

def generate_student_data(school_abbreviation, num_students=10):
    school = School.objects.get(abbreviation=school_abbreviation)
    ethics_1=EthicsLevel.objects.get(id=1)
    class_ethics=VocationalClass.objects.get(id=1)

    for _ in range(num_students):
        # Create a user for the student
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"US_{school_abbreviation}_{first_name}{last_name}"
        password = "password123"
        email = f"{first_name}{last_name}@{school_abbreviation}.com"
        user = User.objects.create_user(username=username, password=password, email=email,
                                        first_name=first_name, last_name=last_name)
        group = Group.objects.get(name='student')
        user.groups.add(group)

        # Create a profile for the user
        profile = Profile.objects.create(user=user, phone_number="1234567890", school=school)

        # Calculate birthdate and graduation year
        current_year = datetime.datetime.now().year

        birth_year = current_year - random.randint(14, 18)
        graduation_year = max(birth_year + random.randint(16, 19), 2024)
        gender = gd.get_gender(first_name)


        if gender == 'male':
            gender_choice = 'm'
        elif gender == 'female' or 'mostly_female':
            gender_choice = 'f'
        else:
            gender_choice = random.choice(['m', 'f'])

        # Create a student
        student = Student.objects.create(user=user, birthday=datetime.date(birth_year, 4, 1),
                                         gender=gender_choice,
                                         graduation_year=graduation_year)
        VocationalStatus.objects.create(student=student, vocational_level=ethics_1, vocational_class=class_ethics)

        # Make the user a parent of the student
        p_fn = fake.first_name()
        p_ln = last_name
        parent_user = User.objects.create_user(username=f"US_{school_abbreviation}_{p_fn}{p_ln}", password=password,
                                               email= f"{p_fn}.{p_ln}@trialemail.iot", first_name = p_fn,
                                               last_name = p_ln)
        group = Group.objects.get(name='parent')
        parent_user.groups.add(group)

        profile = Profile.objects.create(user=parent_user, phone_number="9876543210", school=school)
        student.parent.add(parent_user)

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def generate_formative_grade_records(school_abbreviation, quarter_id, type, evaluation_date):

    school = School.objects.get(abbreviation=school_abbreviation)
    quarter = Quarter.objects.get(id=quarter_id)
    studentassignment = StudentAssignment.objects.filter(department__school__id=school.id).order_by(
        '-quarter__school_year', '-quarter__name')
    student = Student.objects.filter(id__in=studentassignment.values_list('student', flat=True),
                                     user__is_active=True)

    for s in student:
        student_assignment = StudentAssignment.objects.filter(department__school__id=school.id, student=s).order_by(
            '-quarter__school_year', '-quarter__name')
        department= Department.objects.filter(id__in=student_assignment.values_list('department', flat=True)).first()

        instructor_assignment = InstructorAssignment.objects.get(department=department)
        assigned_instructors = instructor_assignment.instructor.all()
        instructor = assigned_instructors[0]
        commendation = f"commendation {generate_random_string(random.randint(5,15))}"
        recommendation = f"recommendation {generate_random_string(random.randint(5,12))}"

        ethics_grade_record= EthicsGradeRecord.objects.create(student=s, level= s.vocationalstatus.vocational_level,
                                                department=department, instructor=instructor.user,
                                                quarter=quarter, time=20, type=type,
                                                evaluation_date= evaluation_date,
                                                recommendation=recommendation, commendation=commendation,
                                                              student_discussed="2022-10-1", vc_validated="2022-10-2")



        #ethics_formative_grade = EthicsFormativeGrade.objects.create(grade_record=ethics_grade_record)

        ethics_definitions = EthicsDefinition.objects.filter(level=s.vocationalstatus.vocational_level)

        for ethic in ethics_definitions:
            score = random.randint(1, 5)
            EthicsFormativeGrade.objects.create(
                ethic=ethic,
                score=score,
                grade_record=ethics_grade_record
            )

def generate_summative_grade_records(school_abbreviation, quarter_id, type, evaluation_date):

    school = School.objects.get(abbreviation=school_abbreviation)
    quarter = Quarter.objects.get(id=quarter_id)
    studentassignment = StudentAssignment.objects.filter(department__school__id=school.id).order_by(
        '-quarter__school_year', '-quarter__name')
    student = Student.objects.filter(id__in=studentassignment.values_list('student', flat=True),
                                     user__is_active=True)

    for s in student:
        student_assignment = StudentAssignment.objects.filter(department__school__id=school.id, student=s).order_by(
            '-quarter__school_year', '-quarter__name')
        department= Department.objects.filter(id__in=student_assignment.values_list('department', flat=True)).first()

        instructor_assignment = InstructorAssignment.objects.get(department=department)
        assigned_instructors = instructor_assignment.instructor.all()
        instructor = assigned_instructors[0]
        #commendation = f"commendation {generate_random_string(random.randint(5,15))}"
        #recommendation = f"recommendation {generate_random_string(random.randint(5,12))}"

        ethics_grade_record= EthicsGradeRecord.objects.create(student=s, level= s.vocationalstatus.vocational_level,
                                                department=department, instructor=instructor.user,
                                                quarter=quarter, time=20, type=type,
                                                evaluation_date= evaluation_date,
                                                student_discussed="2022-10-1")

        #ethics_formative_grade = EthicsFormativeGrade.objects.create(grade_record=ethics_grade_record)

        ethics_definitions = EthicsDefinition.objects.filter(level=s.vocationalstatus.vocational_level)

        for ethic in ethics_definitions:
            score = random.randint(3, 5)
            comment = f"comment {generate_random_string(random.randint(5,10))}"
            EthicsSummativeGrade.objects.create(
                ethic=ethic,
                score=score,
                comment= comment,
                grade_record=ethics_grade_record
            )
        if ethics_grade_record.score() >4:
            ethics_grade_record.suggested_level= EthicsLevel.objects.filter(id=s.vocationalstatus.vocational_level.id + 1).first()
            ethics_grade_record.save()

if __name__ == "__main__":
    #generate_student_data(school_abbreviation="TS", num_students=1)
    #generate_formative_grade_records("TS", 22, "F", "2022-9-9")
    #generate_formative_grade_records("TS", 22, "F", "2022-9-30")
    generate_summative_grade_records("TS", 22, "S", "2022-10-11")