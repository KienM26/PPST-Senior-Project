from django.utils import timezone
from database.models import Doctor, Test, Stimulus, Response, Latency, Results


for c in [Latency, Response, Stimulus, Results, Test, Doctor]:
    c.objects.all().delete()


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


test1 = Test.objects.create(
    doctor=doctor1,
    status="active",
    expiration_date=timezone.now() + timezone.timedelta(days=7),
    test_taker_age=12,
    is_independent=True
)


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
    ("2L48k", "248KL", "mixed", 5),
    
]


stimulus_objects = []


for stimulus_string, correct_answer, stimulus_type, span_length in stimuli_data:
    stimulus_objects.append(
        Stimulus.objects.create(
            test=test1,
            stimulus_string=stimulus_string,
            correct_answer=correct_answer,
            stimulus_type=stimulus_type,
            span_length=span_length
        )
    )


responses = []


for stimulus in stimulus_objects[:5]:
    response = Response.objects.create(
        test=test1,
        stimulus=stimulus,
        response_string=stimulus.correct_answer,
        is_correct=True
    )
    responses.append(response)


for response in responses:
    resp_string = response.response_string
    for i, char in enumerate(resp_string):
        Latency.objects.create(
            response=response,
            input_order=i + 1,
            input_value=char,
            time=600 + (i * 150)
        )


Results.objects.create(
    test=test1,
    total_time=12000,
    response_time=750,
    num_of_correct=5,
    num_of_incorrect=0
)
