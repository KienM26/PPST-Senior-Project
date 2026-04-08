from django.utils import timezone
from database.models import Doctor, Test, Stimulus, Response, Latency, Results




for c in [Latency, Response, Stimulus, Results, Test, Doctor]:
    c.objects.all().delete()




# doctor data
doctor1 = Doctor.objects.create_user(
    username="doctor1",
    password="testpass",
    first_name="John",
    last_name="Smith",
    middle_initial="A",
    organization_name="PPST Clinic",
    office_name="Main Office",
    medical_license_number="LIC1001",
    is_approved=True
)




# stimulus template
stimuli_data = [
    # four span digits
    ("1478", "1478", "digit", 4),
    ("9356", "3569", "digit", 4),
    ("9732", "2379", "digit", 4),
    # five span digits
    ("35486", "34568", "digit", 5),
    ("40973", "03479", "digit", 5),
    ("14982", "12489", "digit", 5),
    # four span mixed
    ("A2L6", "26AL", "mixed", 4),
    ("7LU5", "57LU", "mixed", 4),
    ("F82I", "28FI", "mixed", 4),
    # five span mixed
    ("UC86F", "68CFU", "mixed", 5),
    ("5KI76", "567IK", "mixed", 5),
    ("2L48K", "248KL", "mixed", 5),
]


#completed tests creator
def create_completed_test_with_full_data(doctor, age, is_independent, answer_map, total_time, response_time, base_latency=600):
    test = Test.objects.create(doctor=doctor, status="completed", expiration_date=timezone.now() - timezone.timedelta(days=1), test_taker_age=age, is_independent=is_independent); num_correct = 0; num_incorrect = 0
    for i, (stimulus_string, correct_answer, stimulus_type, span_length) in enumerate(stimuli_data):
        stimulus = Stimulus.objects.create(test=test, stimulus_string=stimulus_string, correct_answer=correct_answer, stimulus_type=stimulus_type, span_length=span_length); response = Response.objects.create(test=test, stimulus=stimulus, response_string=answer_map[i]); response.set_correctness(); num_correct += 1 if response.is_correct else 0; num_incorrect += 0 if response.is_correct else 1
        for j, char in enumerate(response.response_string):
            Latency.objects.create(response=response, input_order=j + 1, input_value=char, time=base_latency + (j * 120) + (i * 30))
    Results.objects.create(test=test, total_time=total_time, response_time=response_time, num_of_correct=num_correct, num_of_incorrect=num_incorrect); return test




# doctor1 completed test 1 - correct
answers_test1 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "03479",
    "12489",
    "26AL",
    "57LU",
    "28FI",
    "68CFU",
    "567IK",
    "248KL",
]


create_completed_test_with_full_data(
    doctor=doctor1,
    age=12,
    is_independent=False,
    answer_map=answers_test1,
    total_time=10800,
    response_time=690,
    base_latency=520
)




# doctor1 completed test 2 - I mean he did alright
answers_test2 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "03497",   # wrong
    "12489",
    "26AL",
    "75LU",    # wrong
    "28FI",
    "68CFU",
    "576IK",   # wrong
    "248KL",
]


create_completed_test_with_full_data(
    doctor=doctor1,
    age=16,
    is_independent=True,
    answer_map=answers_test2,
    total_time=12600,
    response_time=820,
    base_latency=700
)




# doctor1 completed test 3 - bro did not cook
answers_test3 = [
    "1748",    # wrong
    "3569",
    "2793",    # wrong
    "35468",   # wrong
    "03479",
    "12849",   # wrong
    "2A6L",    # wrong
    "57UL",    # wrong
    "82FI",    # wrong
    "68UCF",   # wrong
    "567KI",   # wrong
    "284KL",   # wrong
]


create_completed_test_with_full_data(
    doctor=doctor1,
    age=25,
    is_independent=True,
    answer_map=answers_test3,
    total_time=16800,
    response_time=1080,
    base_latency=980
)




# graph/stat data
graph_data = [
    {"age": 8,  "is_independent": False, "total_time": 15600, "response_time": 980, "correct": 5,  "incorrect": 7},
    {"age": 10, "is_independent": False, "total_time": 14800, "response_time": 920, "correct": 6,  "incorrect": 6},
    {"age": 14, "is_independent": False, "total_time": 13900, "response_time": 860, "correct": 7,  "incorrect": 5},
    {"age": 18, "is_independent": True,  "total_time": 11600, "response_time": 730, "correct": 9,  "incorrect": 3},
    {"age": 21, "is_independent": True,  "total_time": 10400, "response_time": 660, "correct": 10, "incorrect": 2},
    {"age": 30, "is_independent": True,  "total_time": 11100, "response_time": 700, "correct": 9,  "incorrect": 3},
    {"age": 42, "is_independent": False, "total_time": 12900, "response_time": 810, "correct": 8,  "incorrect": 4},
    {"age": 55, "is_independent": False, "total_time": 14100, "response_time": 890, "correct": 7,  "incorrect": 5},
    {"age": 67, "is_independent": False, "total_time": 15900, "response_time": 1010, "correct": 5,  "incorrect": 7},
]


for row in graph_data:
    test = Test.objects.create(\
        doctor=None, status="completed", \
        expiration_date=timezone.now() - timezone.timedelta(days=1), \
        test_taker_age=row["age"], is_independent=row["is_independent"])
    Results.objects.create(\
        test=test, total_time=row["total_time"], response_time=row["response_time"], \
        num_of_correct=row["correct"], num_of_incorrect=row["incorrect"])



