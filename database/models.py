from django.db import models
from django.contrib.auth.models import AbstractUser


class Doctor(AbstractUser):
    middle_initial = models.CharField(max_length=1, blank=True)
    organization_name = models.CharField(max_length=200)
    office_name = models.CharField(max_length=200)
    medical_license_number = models.CharField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=True)
   
    def approve(self):
        self.is_approved = True
        self.save()


    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_initial} {self.last_name}".strip()




class Test(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('active', 'Active'),
    ]


    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tests'
    )
   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expiration_date = models.DateTimeField(null=True, blank=True)
    test_taker_age = models.PositiveIntegerField()
    is_independent = models.BooleanField(default=True)


    def __str__(self):
        return f"Test {self.id} - {self.status}"




class Stimulus(models.Model):
    STIMULUS_TYPE_CHOICES = [
        ('digit', 'Digit'),
        ('mixed', 'Mixed'),
    ]


    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='stimuli'
    )
   
    stimulus_string = models.TextField()
    correct_answer = models.TextField()
    stimulus_type = models.CharField(
        max_length=20,
        choices=STIMULUS_TYPE_CHOICES,
        default='digit'
    )
    span_length = models.PositiveIntegerField()


    def __str__(self):
        return f"stimulus {self.id} has string {self.stimulus_string}"




class Response(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    stimulus = models.ForeignKey(
        Stimulus,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    response_string = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)


    def set_correctness(self):
        self.is_correct = self.response_string == self.stimulus.correct_answer
        self.save()


    def __str__(self):
        return f"response {self.id} to stimulus {self.stimulus.id} has string {self.response_string} and is_correct {self.is_correct}"




class Latency(models.Model):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='latencies'
    )
    input_order = models.PositiveIntegerField()
    input_value = models.CharField(max_length=1)
    time = models.PositiveIntegerField()


    class Meta:
        ordering = ['input_order']
        unique_together = ('response', 'input_order')




class Results(models.Model):
    test = models.OneToOneField(
        Test,
        on_delete=models.CASCADE,
        related_name='results'
    )
   
    total_time = models.PositiveIntegerField()
    response_time = models.PositiveIntegerField()
    num_of_correct = models.IntegerField(default=0)
    num_of_incorrect = models.IntegerField(default=0)


    @property
    def accuracy(self):
        total_answered = self.num_of_correct + self.num_of_incorrect
        if total_answered == 0:
            return 0.0
        return (self.num_of_correct / total_answered) * 100
