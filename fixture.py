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
    email="john.smith@example.com",
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
    ("48973", "34789", "digit", 5),
    ("14982", "12489", "digit", 5),
    # four span mixed
    ("A2H6", "26AH", "mixed", 4),
    ("7DF5", "57DF", "mixed", 4),
    ("F82I", "28FI", "mixed", 4),
    # five span mixed
    ("GC86F", "68CFG", "mixed", 5),
    ("5BI76", "567BI", "mixed", 5),
    ("2A48C", "248AC", "mixed", 5),
]


#completed tests creator
def create_completed_test_with_full_data(doctor, age, is_independent, answer_map, total_time, response_time, base_latency=600):
    test = Test.objects.create(doctor=doctor, status="completed", expiration_date=timezone.now() - timezone.timedelta(days=1), test_taker_age=age, is_independent=is_independent); num_correct = 0; num_incorrect = 0
    for i, (stimulus_string, correct_answer, stimulus_type, span_length) in enumerate(stimuli_data):
        stimulus = Stimulus.objects.create(test=test, stimulus_string=stimulus_string, correct_answer=correct_answer, stimulus_type=stimulus_type, span_length=span_length); response = Response.objects.create(test=test, stimulus=stimulus, response_string=answer_map[i]); response.set_correctness(); num_correct += 1 if response.is_correct else 0; num_incorrect += 0 if response.is_correct else 1
        for j, char in enumerate(response.response_string):
            Latency.objects.create(response=response, input_order=j + 1, input_value=char, time=base_latency + (j * 120) + (i * 30))
    Results.objects.create(test=test, total_time=total_time, response_time=response_time, num_of_correct=num_correct, num_of_incorrect=num_incorrect); return test




# doctor1 completed test 1 - correct(12/12)
answers_test1 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "34789",
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
    age=21,
    is_independent=False,
    answer_map=answers_test1,
    total_time=310000,
    response_time=5200,
    base_latency=520
)




# doctor1 completed test 2 - I mean he did alright(9/12)
answers_test2 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "83497",   # wrong
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
    age=38,
    is_independent=True,
    answer_map=answers_test2,
    total_time=340000,
    response_time=4720,
    base_latency=700
)




# doctor1 completed test 3 - bro did not cook(2/12)
answers_test3 = [
    "1748",    # wrong
    "3569",
    "2793",    # wrong
    "35468",   # wrong
    "34789",
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
    age=60,
    is_independent=True,
    answer_map=answers_test3,
    total_time=590000,
    response_time=6400,
    base_latency=980
)

# doctor1 completed test 4 - near perfect (11/12)
answers_test4 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "34789",
    "12489",
    "26AL",
    "57LU",
    "28FI",
    "68CFU",
    "567KI",   # wrong
    "248KL",
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=23,
    is_independent=True,
    answer_map=answers_test4,
    total_time=320000,
    response_time=4380,
    base_latency=640
)


# doctor1 completed test 5 - average (8/12)
answers_test5 = [
    "1478",
    "3596",    # wrong
    "2379",
    "34586",   # wrong
    "34789",
    "12849",   # wrong
    "26AL",
    "57LU",
    "28FI",
    "68CFU",
    "567IK",
    "284KL",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=28,
    is_independent=False,
    answer_map=answers_test5,
    total_time=460000,
    response_time=5750,
    base_latency=920
)


# doctor1 completed test 6 - perfect
answers_test6 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "34789",
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
    age=21,
    is_independent=True,
    answer_map=answers_test6,
    total_time=300000,
    response_time=4100,
    base_latency=560
)


# doctor1 completed test 7 - below average (6/12)
answers_test7 = [
    "1748",    # wrong
    "3569",
    "2793",    # wrong
    "35468",   # wrong
    "34789",
    "12489",
    "2A6L",    # wrong
    "57UL",    # wrong
    "28FI",
    "68UCF",   # wrong
    "567IK",
    "248KL",
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=50,
    is_independent=False,
    answer_map=answers_test7,
    total_time=520000,
    response_time=6100,
    base_latency=1040
)


# doctor1 completed test 8 - good (9/12)
answers_test8 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "83497",   # wrong
    "12489",
    "26LA",    # wrong
    "57LU",
    "28FI",
    "68CFU",
    "567IK",
    "248LK",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=31,
    is_independent=False,
    answer_map=answers_test8,
    total_time=380000,
    response_time=5000,
    base_latency=820
)


# doctor1 completed test 9 - strong (10/12)
answers_test9 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "34789",
    "12489",
    "26AL",
    "57LU",
    "82FI",    # wrong
    "68CFU",
    "567IK",
    "284KL",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=30,
    is_independent=True,
    answer_map=answers_test9,
    total_time=345000,
    response_time=4250,
    base_latency=610
)


# doctor1 completed test 10 - decent (6/12)
answers_test10 = [
    "1478",
    "3569",
    "2739",    # wrong
    "34568",
    "83497",   # wrong
    "12489",
    "26AL",
    "75LU",    # wrong
    "28IF",    # wrong
    "68CFU",
    "576IK",   # wrong
    "248LK",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=35,
    is_independent=True,
    answer_map=answers_test10,
    total_time=430000,
    response_time=4400,
    base_latency=680
)

# doctor1 completed test 11 - average (9/12)
answers_test11 = [
    "1478",
    "3596",    # wrong
    "2379",
    "34568",
    "34789",
    "12849",   # wrong
    "26AL",
    "57LU",
    "82FI",    # wrong
    "68CFU",
    "567IK",
    "248KL",
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=42,
    is_independent=False,
    answer_map=answers_test11,
    total_time=450000,
    response_time=4900,
    base_latency=860
)


# doctor1 completed test 12 - rough (4/12)
answers_test12 = [
    "1748",    # wrong
    "3569",
    "2793",    # wrong
    "35468",   # wrong
    "34789",
    "14289",   # wrong
    "2A6L",    # wrong
    "57UL",    # wrong
    "28FI",
    "68UCF",   # wrong
    "567KI",   # wrong
    "248KL",
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=50,
    is_independent=False,
    answer_map=answers_test12,
    total_time=560000,
    response_time=5480,
    base_latency=960
)


# doctor1 completed test 13 - good (9/12)
answers_test13 = [
    "1478",
    "3569",
    "2379",
    "34568",
    "83497",   # wrong
    "12489",
    "26AL",
    "57LU",
    "28FI",
    "68UFC",   # wrong
    "567IK",
    "248LK",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=55,
    is_independent=False,
    answer_map=answers_test13,
    total_time=390000,
    response_time=5250,
    base_latency=910
)


# doctor1 completed test 14 - below average (6/12)
answers_test14 = [
    "1748",    # wrong
    "3569",
    "2379",
    "35468",   # wrong
    "34789",
    "12489",
    "2A6L",    # wrong
    "57UL",    # wrong
    "82FI",    # wrong
    "68CFU",
    "567IK",
    "248LK",   # wrong
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=61,
    is_independent=False,
    answer_map=answers_test14,
    total_time=500000,
    response_time=5820,
    base_latency=1020
)


# doctor1 completed test 15 - very rough (1/12)
answers_test15 = [
    "1748",    # wrong
    "3659",    # wrong
    "2793",    # wrong
    "35468",   # wrong
    "84379",   # wrong
    "12849",   # wrong
    "2A6L",    # wrong
    "57UL",    # wrong
    "82FI",    # wrong
    "68UCF",   # wrong
    "567KI",   # wrong
    "248KL",
]

create_completed_test_with_full_data(
    doctor=doctor1,
    age=67,
    is_independent=False,
    answer_map=answers_test15,
    total_time=600000,
    response_time=6400,
    base_latency=1120
)




# graph/stat data
graph_data = [
    {"age": 8,  "is_independent": False, "total_time": 540000, "response_time": 6800, "correct": 5,  "incorrect": 7},
    {"age": 10, "is_independent": False, "total_time": 500000, "response_time": 6500, "correct": 6,  "incorrect": 6},
    {"age": 14, "is_independent": False, "total_time": 420000, "response_time": 6000, "correct": 7,  "incorrect": 5},
    {"age": 18, "is_independent": True,  "total_time": 340000, "response_time": 4800, "correct": 9,  "incorrect": 3},
    {"age": 21, "is_independent": True,  "total_time": 310000, "response_time": 4400, "correct": 10, "incorrect": 2},
    {"age": 30, "is_independent": True,  "total_time": 330000, "response_time": 4600, "correct": 9,  "incorrect": 3},
    {"age": 42, "is_independent": False, "total_time": 400000, "response_time": 5500, "correct": 8,  "incorrect": 4},
    {"age": 55, "is_independent": False, "total_time": 460000, "response_time": 6000, "correct": 7,  "incorrect": 5},
    {"age": 67, "is_independent": False, "total_time": 580000, "response_time": 7000, "correct": 5,  "incorrect": 7},
]


for row in graph_data:
    test = Test.objects.create(\
        doctor=None, status="completed", \
        expiration_date=timezone.now() - timezone.timedelta(days=1), \
        test_taker_age=row["age"], is_independent=row["is_independent"])
    Results.objects.create(\
        test=test, total_time=row["total_time"], response_time=row["response_time"], \
        num_of_correct=row["correct"], num_of_incorrect=row["incorrect"])



