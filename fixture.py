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
    ("3A7C", "37AC", 4),
    ("U26M", "26MU", 4),
    ("5F2A", "25AF", 4),
    ("K3I8", "38IK", 4),
    ("7C2L", "27CL", 4),
    ("3A7C1", "137AC", 5),
    ("U26M4", "246MU", 5),
    ("5F2A9", "259AF", 5),
    ("K3I18", "138IK", 5),
    ("7C2L5", "257CL", 5),
]


stimulus_objects = []


for stimulus_string, correct_answer, span_length in stimuli_data:
    stimulus_objects.append(
        Stimulus.objects.create(
            test=test1,
            stimulus_string=stimulus_string,
            correct_answer=correct_answer,
            stimulus_type="mixed",
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
