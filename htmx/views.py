import csv
import random
import json

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.utils import timezone

from django.db.models import Avg

from database.models import Latency, Response, Results, Stimulus, Test

from datetime import date, timedelta
import json

from django.contrib.auth import authenticate, login, logout
from database.models import Doctor
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

import random
import string

USED_STIMULI = set()


def generate_digit_stimulus():
    while True:
        digits = random.sample("123456789", 5)
        sequence = "".join(digits)

        if sequence in USED_STIMULI:
            continue

        USED_STIMULI.add(sequence)

        correct_answer = "".join(sorted(digits))  # ascending digits

        return {
            "key": f"digit_{sequence}",
            "sequence": sequence,
            "correct_answer": correct_answer,
        }


def generate_mixed_stimulus():
    while True:
        digits = random.sample("123456789", 3)
        letters = random.sample(string.ascii_uppercase, 2)

        combined = digits + letters
        random.shuffle(combined)
        sequence = "".join(combined)

        if sequence in USED_STIMULI:
            continue

        USED_STIMULI.add(sequence)

        correct_answer = "".join(sorted(digits)) + "".join(sorted(letters))

        return {
            "key": f"mixed_{sequence}",
            "sequence": sequence,
            "correct_answer": correct_answer,
        }




ACCESSIBILITY_THEMES = {
    "teal": {
        "name": "Teal",
        "swatch": "#0f9db7",
        "header": "#0f9db7",
        "button": "#0f9db7",
    },
    "orange": {
        "name": "Orange",
        "swatch": "#f7924a",
        "header": "#f7924a",
        "button": "#f7924a",
    },
    "navy": {
        "name": "Navy",
        "swatch": "#075787",
        "header": "#075787",
        "button": "#075787",
    },
    "purple": {
        "name": "Purple",
        "swatch": "#9b69de",
        "header": "#9b69de",
        "button": "#9b69de",
    },
}

ACCESSIBILITY_TEXT = {
    "en": {
        "title": "Accessibility",
        "prompt": "Choose the Colors You can see the Best",
        "change": "Change",
        "continue": "Continue",
    },
    "es": {
        "title": "Accesibilidad",
        "prompt": "Elige los colores que puedas ver mejor",
        "change": "Cambiar",
        "continue": "Continuar",
    }
}

LANGUAGE_INFO = {
    "en": {
        "code": "en",
        "label": "English",
        "flag": "htmx/images/flag-usa.png",
    },
    "es": {
        "code": "es",
        "label": "Español",
        "flag": "htmx/images/flag-spain.png",
    }
}

PRACTICE_HOME_TEXT = {
    "en": {
        "title": "The Philadelphia Pointing Span Proctored Test",
        "btn": "Start Test Now",
    },
    "es": {
        "title": "La Prueba Supervisada de Span de Apuntado de Filadelfia",
        "btn": "Comenzar Prueba Ahora",
    }
}

SELECT_VOICE_TEXT = {
    "en": {
        "title": "Select Your Voice",
        "btn": "Next",
        "female": "Female",
        "male": "Male",
    },
    "es": {
        "title": "Seleccione Su Voz",
        "btn": "Siguiente",
        "female": "Femenino",
        "male": "Masculino",
    }
}

PRACTICE_TEXT = {
    "en": {
        "title": "Test Instructions",
        "intro_heading": "Before You Begin",
        "intro_body": [
            "THIS TEST MEASURES ATTENTION AND MEMORY",
            "YOU WILL SEE OR HEAR DIFFERENT PROMPTS",
            "FOLLOW THE ON-SCREEN INSTRUCTIONS CAREFULLY",
            "ANSWER EACH PROMPT TO THE BEST OF YOUR ABILITY",
            "YOUR RESPONSES REMAIN ANONYMOUS",
        ],
        "digit_test": "Digit Stimuli Test",
        "mixed_test": "Mixed Stimuli Test",
        "mixed_practice_test": "Mixed Stimuli Practice Test",
        "digit_actual_instructions": "YOU ARE ABOUT TO BEGIN THE PPST TEST WITH DIGIT STIMULI. PLEASE CHOOSE THE START TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        "mixed_actual_instructions": "YOU ARE ABOUT TO BEGIN THE PPST TEST WITH MIXED STIMULI. PLEASE CHOOSE THE START TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        "mixed_practice_instructions": "YOU ARE ABOUT TO BEGIN THE PPST PRACTICE TEST WITH MIXED (ALPHABET-DIGIT) STIMULI. YOU WILL GO THROUGH TWO PRACTICE STIMULUS AND RESPONSE PAGES. PLEASE CHOOSE THE START PRACTICE TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        "intro_button": "Next",
        "practice_heading": "Practice Test",
        "practice_body": [
            "YOU ARE ABOUT TO BEGIN THE PPST PRACTICE TEST WITH",
            "DIGIT STIMULI. YOU WILL GO THROUGH TWO PRACTICE",
            "STIMULUS AND RESPONSE PAGES. PLEASE CHOOSE THE START",
            "PRACTICE TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        ],
        "practice_button": "Start Practice Test",
        "actual_test_button": "Start Test",
    },
    "es": {
        "title": "Instrucciones de la Prueba",
        "intro_heading": "Antes de Comenzar",
        "intro_body": [
            "ESTA PRUEBA MIDE LA ATENCIÓN Y LA MEMORIA",
            "VERÁ O ESCUCHARÁ DIFERENTES INDICACIONES",
            "SIGA CUIDADOSAMENTE LAS INSTRUCCIONES EN PANTALLA",
            "RESPONDA CADA INDICACIÓN LO MEJOR POSIBLE",
            "SUS RESPUESTAS PERMANECEN ANÓNIMAS",
        ],
        "digit_test": "Prueba de Estímulos de Dígitos",
        "mixed_test": "Prueba de Estímulos Mixtos",
        "mixed_practice_test": "Prueba de Práctica de Estímulos Mixtos",
        "digit_actual_instructions": "ESTÁ A PUNTO DE COMENZAR LA PRUEBA PPST CON ESTÍMULOS DE DÍGITOS. POR FAVOR, ELIJA EL BOTÓN COMENZAR PRUEBA CUANDO ESTÉ LISTO PARA INICIAR.",
        "mixed_actual_instructions": "ESTÁ A PUNTO DE COMENZAR LA PRUEBA PPST CON ESTÍMULOS MIXTOS. POR FAVOR, ELIJA EL BOTÓN COMENZAR PRUEBA CUANDO ESTÉ LISTO PARA INICIAR.",
        "mixed_practice_instructions": "ESTÁ A PUNTO DE COMENZAR LA PRUEBA DE PRÁCTICA PPST CON ESTÍMULOS MIXTOS (ALFABETO-DÍGITO). PASARÁ POR DOS PÁGINAS DE ESTÍMULO Y RESPUESTA DE PRÁCTICA. POR FAVOR, ELIJA EL BOTÓN COMENZAR PRUEBA CUANDO ESTÉ LISTO PARA INICIAR.",
        "intro_button": "Siguiente",
        "practice_heading": "Prueba de Práctica",
        "practice_body": [
            "ESTÁ A PUNTO DE COMENZAR LA PRUEBA DE PRÁCTICA PPST CON",
            "ESTÍMULOS DE DÍGITOS. PASARÁ POR DOS PÁGINAS DE",
            "ESTÍMULO Y RESPUESTA DE PRÁCTICA. ELIJA EL BOTÓN",
            "COMENZAR PRÁCTICA CUANDO ESTÉ LISTO PARA INICIAR.",
        ],
        "practice_button": "Comenzar Práctica",
        "actual_test_button": "Comenzar Prueba",
    }
}

PRACTICE_DIGIT_TEXT = {
    "en": {
        "title": "Practice Test Digit Stimuli",
        "title_response": "Practice Test Digit Stimuli Response",
        "title_mixed": "Practice Test Mixed Stimuli",
        "title_mixed_response": "Practice Test Mixed Stimuli Response",
        "sequence": "Sequence shown here",
        "prompt": "Please Enter Digits in Ascending Order",
        "submit": "Submit",
        "next": "Next",
    },
    "es": {
        "title": "Prueba de Práctica de Dígitos",
        "title_response": "Respuesta de Prueba de Práctica de Dígitos",
        "title_mixed": "Prueba de práctica con estímulos mixtos",
        "title_mixed_response": "Prueba de práctica con estímulos mixtos y respuesta",
        "sequence": "Secuencia mostrada aquí",
        "prompt": "Por favor, ingrese los dígitos en orden ascendente",
        "submit": "Enviar",
        "next": "Siguiente",
    }
}

DIGIT_TEXT = {
    "en": {
        "title": "Digit Stimuli",
        "title_response": "Digit Stimuli Response",
        "title_mixed": "Mixed Stimuli",
        "title_mixed_response": "Mixed Stimuli Response",
        "sequence": "Sequence shown here",
        "prompt": "Please Enter Digits in Ascending Order",
        "submit": "Submit",
        "next": "Next",
    },
    "es": {
        "title": "Estímulos de Dígitos",
        "title_response": "Respuesta de Estímulos de Dígitos",
        "title_mixed": "Estímulos Mixtos",
        "title_mixed_response": "Respuesta de Estímulos Mixtos",
        "sequence": "Secuencia mostrada aquí",
        "prompt": "Por favor, ingrese los dígitos en orden ascendente",
        "submit": "Enviar",
        "next": "Siguiente",
    }
}

PRACTICE_MIXED_TEXT = {
    "en": {
        "title": "Practice Test Mixed Stimuli",
        "title_response": "Practice Test Mixed Stimuli Response",
        "sequence": "Sequence shown here",
        "prompt": "Please Enter Digits in Ascending Order and Letters Alphabetically",
        "submit": "Submit",
        "next": "Next",
    },
    "es": {
        "title": "Prueba de práctica con estímulos mixtos",
        "title_response": "Prueba de práctica con estímulos mixtos y respuesta",
        "sequence": "Secuencia mostrada aquí",
        "prompt": "Por favor, ingrese dígitos en orden ascendente y letras alfabéticamente",
        "submit": "Enviar",
        "next": "Siguiente",
    }
}

MIXED_TEXT = {
    "en": {
        "title": "Mixed Stimuli",
        "title_response": "Mixed Stimuli Response",
        "sequence": "Sequence shown here",
        "prompt": "Please Enter Digits in Ascending Order and Letters Alphabetically",
        "submit": "Submit",
        "next": "Next",
    },
    "es": {
        "title": "Estímulos Mixtos",
        "title_response": "Respuesta de Estímulos Mixtos",
        "sequence": "Secuencia mostrada aquí",
        "prompt": "Por favor, ingrese dígitos en orden ascendente y letras alfabéticamente",
        "submit": "Enviar",
        "next": "Siguiente",
    }
}

TEST_COMPLETION_TEXT = {
    "en": {
        "title": "Test Complete",
        "message": "Thank you for completing the test. Your responses have been recorded.",
        "exit": "Exit",
    },
    "es": {
        "title": "Prueba Completa",
        "message": "Gracias por completar la prueba. Sus respuestas han sido registradas.",
        "exit": "Salir",
    }
}

def get_current_lang(request):
    lang = request.session.get("lang", "en")
    if lang not in PRACTICE_TEXT:
        lang = "en"
    return lang

def get_current_theme(request):
    theme_key = request.session.get("theme", "teal")
    if theme_key not in ACCESSIBILITY_THEMES:
        theme_key = "teal"
    return ACCESSIBILITY_THEMES[theme_key]


def initialize_test_session(request, stimuli_data, stimulus_type):
    test = Test.objects.create(
    doctor=request.user if request.user.is_authenticated else None,
    status="active",
    test_taker_age=12,
    is_independent=True,
    )

    stimulus_ids = {}
    for stimulus in stimuli_data:
        created = Stimulus.objects.create(
            test=test,
            stimulus_string=stimulus["sequence"],
            correct_answer=stimulus["correct_answer"],
            stimulus_type=stimulus_type,
            span_length=len(stimulus["sequence"]),
        )
        stimulus_ids[stimulus["key"]] = created.id

    request.session["current_test_id"] = test.id
    request.session["current_test_type"] = stimulus_type
    request.session["current_test_stimulus_ids"] = stimulus_ids

@require_GET
def demo(request):
    return render(request, 'htmx/demo.html', randomimg())


@require_GET
def test(request):
    return render(request, 'htmx/test.html', {})

@require_GET
def practice_test_intro(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_test_intro.html", {
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_POST
def practice_test_next(request):
    request.session["practice_intro_seen"] = True
    return redirect("htmx:practiceTestPage")


@require_GET
def practice_test_page(request):
    if not request.session.get("practice_intro_seen"):
        return redirect("htmx:practiceTest")

    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_test_ready.html", {
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_POST
def start_independent_test(request):
    for key in (
        "independent_test",
        "independent_stimuli",
        "independent_results",
        "used_stimuli_keys",
        "test_started_at",
    ):
        request.session.pop(key, None)

    request.session["independent_test"] = True
    request.session["test_started_at"] = timezone.now().isoformat()

    # Pull stimuli from database fixture instead of generating random ones
    baseline_test = Test.objects.filter(status="completed").first()
    
    if baseline_test and baseline_test.stimuli.exists():
        baseline_stimuli = baseline_test.stimuli.all()
        
        # Get all digit stimuli by span
        digit_4_span = list(baseline_stimuli.filter(stimulus_type="digit", span_length=4))
        digit_5_span = list(baseline_stimuli.filter(stimulus_type="digit", span_length=5))
        
        # Get all mixed stimuli by span
        mixed_4_span = list(baseline_stimuli.filter(stimulus_type="mixed", span_length=4))
        mixed_5_span = list(baseline_stimuli.filter(stimulus_type="mixed", span_length=5))
        
        # Shuffle each group
        random.shuffle(digit_4_span)
        random.shuffle(digit_5_span)
        random.shuffle(mixed_4_span)
        random.shuffle(mixed_5_span)
        
        # Create stimuli arrays with proper key format for independent test
        digit_stimuli = []
        for stim in (digit_4_span + digit_5_span):
            digit_stimuli.append({
                "key": f"digit_{stim.stimulus_string}",
                "sequence": stim.stimulus_string,
                "correct_answer": stim.correct_answer,
            })
        
        mixed_stimuli = []
        for stim in (mixed_4_span + mixed_5_span):
            mixed_stimuli.append({
                "key": f"mixed_{stim.stimulus_string}",
                "sequence": stim.stimulus_string,
                "correct_answer": stim.correct_answer,
            })
    else:
        # Fallback: use fixture data directly
        digit_4_span_data = [
            ("1478", "1478"),
            ("9356", "3569"),
            ("9732", "2379"),
        ]
        digit_5_span_data = [
            ("35486", "34568"),
            ("48973", "34789"),
            ("14982", "12489"),
        ]
        mixed_4_span_data = [
            ("A2L6", "26AL"),
            ("7LU5", "57LU"),
            ("F82I", "28FI"),
        ]
        mixed_5_span_data = [
            ("UC86F", "68CFU"),
            ("5KI76", "567IK"),
            ("2L48K", "248KL"),
        ]
        
        # Shuffle each group
        random.shuffle(digit_4_span_data)
        random.shuffle(digit_5_span_data)
        random.shuffle(mixed_4_span_data)
        random.shuffle(mixed_5_span_data)
        
        digit_stimuli = []
        for seq, ans in (digit_4_span_data + digit_5_span_data):
            digit_stimuli.append({
                "key": f"digit_{seq}",
                "sequence": seq,
                "correct_answer": ans,
            })
        
        mixed_stimuli = []
        for seq, ans in (mixed_4_span_data + mixed_5_span_data):
            mixed_stimuli.append({
                "key": f"mixed_{seq}",
                "sequence": seq,
                "correct_answer": ans,
            })

    request.session["digit_stimuli"] = digit_stimuli
    request.session["mixed_stimuli"] = mixed_stimuli
    request.session["used_stimuli_keys"] = []

    return redirect("htmx:SelectLanguage")

@require_POST
def start_practice_test(request):
    request.session["practice_test_started"] = True
    return redirect("htmx:practiceDigitStimuli1")


@require_POST
def start_digit_test(request):
    request.session["test_started_at"] = timezone.now().isoformat()
    request.session["current_stimulus_index"] = 0
    request.session["current_test_section"] = "digit"

    # ensure clean tracking
    request.session.setdefault("used_stimuli_keys", [])

    return redirect("htmx:digitStimuli1")


@require_POST
def start_mixed_test(request):
    request.session["current_stimulus_index"] = 2  # After 2 digit stimuli
    request.session["current_test_section"] = "mixed"
    return redirect("htmx:mixedStimuli1")


@require_GET
def practice_stimulus(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_stimulus.html", {
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_actual_instructions(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_actual_instructions.html", {
        "lang": lang,
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def select_language(request):
    return render(request, 'htmx/select_language.html', {})


@require_GET
def accessibility(request):
    lang = request.GET.get("lang") or request.session.get("lang", "en")
    if lang not in ACCESSIBILITY_TEXT:
        lang = "en"

    request.session["lang"] = lang

    selected_theme = request.session.get("theme", "teal")
    if selected_theme not in ACCESSIBILITY_THEMES:
        selected_theme = "teal"

    return render(request, "htmx/accessibility.html", {
        "lang": lang,
        "text": ACCESSIBILITY_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "themes": ACCESSIBILITY_THEMES,
        "selected_theme": selected_theme,
        "current_theme": ACCESSIBILITY_THEMES[selected_theme],
    })

@require_POST
def save_accessibility(request):
    lang = request.POST.get("lang", "en")
    if lang not in ACCESSIBILITY_TEXT:
        lang = "en"

    selected_theme = request.POST.get("theme", "teal")
    if selected_theme not in ACCESSIBILITY_THEMES:
        selected_theme = "teal"

    request.session["lang"] = lang
    request.session["theme"] = selected_theme

    print("SAVE_ACCESSIBILITY POST lang =", lang)
    print("SAVE_ACCESSIBILITY session lang =", request.session.get("lang"))

    return redirect(f"/htmx/practiceTest?lang={lang}")

@require_GET
def practice_test(request):
    lang = request.GET.get("lang") or request.session.get("lang") or "en"

    print("PRACTICE_TEST GET lang =", request.GET.get("lang"))
    print("PRACTICE_TEST session lang =", request.session.get("lang"))
    print("PRACTICE_TEST final lang =", lang)

    if lang not in PRACTICE_HOME_TEXT:
        lang = "en"

    request.session["lang"] = lang
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_test.html", {
        "lang": lang,
        "text": PRACTICE_HOME_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_practice_instructions(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_practice_instructions.html", {
        "lang": lang,
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def select_voice(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)
    selected_voice = request.session.get("voice", "")
    current_theme = get_current_theme(request)

    return render(request, 'htmx/select_voice.html', {
        "text": SELECT_VOICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "selected_voice": selected_voice,
    })

@require_POST
def save_voice(request):
    selected_voice = request.POST.get("voice", "")
    if selected_voice not in ["female", "male"]:
        selected_voice = "female"

    request.session["voice"] = selected_voice

    return redirect("htmx:digitPracticeInstructions")

@require_GET
def doctor_about(request):
    return render(request, 'htmx/doctorportal/doctor_about.html', {})

@require_GET
def home(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/doctorportal/home.html", {
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "text": PRACTICE_HOME_TEXT[lang],  
    })

@require_GET
def doctor_portal(request):
    return render(request, 'htmx/doctorportal/doctor_portal.html', {})

@require_http_methods(["GET", "POST"])
def doctor_login(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_approved:
                return render(request, 'htmx/doctorportal/doctor_login.html', {
                    "error": "Account not approved yet"
                })

            # Capture the prior login timestamp before Django updates last_login.
            request.session["previous_login_at"] = (
                user.last_login.isoformat() if user.last_login else ""
            )

            login(request, user)
            return redirect("htmx:doctor_dashboard")

        return render(request, 'htmx/doctorportal/doctor_login.html', {
            "error": "Invalid username or password"
        })

    return render(request, 'htmx/doctorportal/doctor_login.html')

def doctor_create_account(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        hospital = request.POST.get("hospital")
        practice = request.POST.get("practice")
        license_number = request.POST.get("license")

        errors = []
        if not first_name or not last_name:
            errors.append("First and last name are required.")

        if not email:
            errors.append("Email is required.")
        else:
            try:
                validate_email(email)
            except:
                errors.append("Enter a valid email address.")

        if not username:
            errors.append("Username is required.")

        if not password:
            errors.append("Password is required.")

        if password != password_confirm:
            errors.append("Passwords do not match.")
        try:
            validate_password(password)
        except ValidationError as e:
            errors.extend(e.messages)
        #----
        if not re.search(r"[A-Z]", password or ""):
            errors.append("Password must include at least one uppercase letter.")

        if not re.search(r"[a-z]", password or ""):
            errors.append("Password must include at least one lowercase letter.")

        if not re.search(r"[0-9]", password or ""):
            errors.append("Password must include at least one number.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password or ""):
            errors.append("Password must include at least one special character.")
        #----
        if Doctor.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if Doctor.objects.filter(medical_license_number=license_number).exists():
            errors.append("License already registered.")
        if errors:
            return render(request, 'htmx/doctorportal/doctor_create_account.html', {
                "errors": errors,
                "form_data": request.POST
            })
        user = Doctor.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            middle_initial=middle_name[:1] if middle_name else "",
            organization_name=hospital,
            office_name=practice,
            medical_license_number=license_number,
            is_approved=True
        )

        login(request, user)
        return redirect("htmx:doctor_dashboard")

    return render(request, 'htmx/doctorportal/doctor_create_account.html')

@login_required
@require_GET
def doctor_dashboard(request):
    now = timezone.now()
    previous_login_raw = request.session.get("previous_login_at", "")
    previous_login_at = parse_datetime(previous_login_raw) if previous_login_raw else None

    tests = Test.objects.filter(doctor=request.user).select_related("results")

    completed_tests = tests.filter(status="completed", results__isnull=False)
    if previous_login_at:
        completed_tests = completed_tests.filter(results__created_at__gte=previous_login_at)
    else:
        completed_tests = completed_tests.none()

    in_progress_tests = tests.filter(status="active")

    expiring_soon = tests.filter(
        expiration_date__isnull=False,
        expiration_date__gte=now,
        expiration_date__lte=now + timedelta(hours=48),
    ).exclude(status="completed").exclude(status="expired")

    return render(request, 'htmx/doctorportal/doctor_dashboard.html', {
        "user": request.user,
        "completed_tests": completed_tests.order_by("-results__created_at"),
        "in_progress_tests": in_progress_tests.order_by("expiration_date", "id"),
        "expiring_soon": expiring_soon.order_by("expiration_date", "id"),
        "previous_login_at": previous_login_at,
    })

@login_required
@require_GET
def doctor_create_test(request):
    recent_tests = Test.objects.filter(
        doctor=request.user,
        token__isnull=False
    ).order_by('-created_at')[:10]
    return render(request, 'htmx/doctorportal/doctor_create_test.html', {
        "user": request.user,
        "recent_tests": recent_tests,
    })


@login_required
@require_POST
def generate_test_link(request):
    import uuid as uuid_module
    from datetime import datetime, timedelta, timezone as dt_timezone

    patient_age      = request.POST.get("patient_age", "").strip()
    device_email     = request.POST.get("device_email", "").strip()
    expiration_hours = request.POST.get("expiration_hours", "48").strip()

    errors = {}
    if not patient_age or not patient_age.isdigit() or not (1 <= int(patient_age) <= 120):
        errors["patient_age"] = "A valid patient age (1–120) is required."
    if not device_email:
        errors["device_email"] = "A device email is required."
    try:
        exp_hours = int(expiration_hours)
        if exp_hours < 1 or exp_hours > 720:
            raise ValueError
    except ValueError:
        exp_hours = 48

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    expiration_dt = datetime.now(dt_timezone.utc) + timedelta(hours=exp_hours)
    token = uuid_module.uuid4()

    test = Test.objects.create(
        doctor=request.user,
        status="pending",
        test_taker_age=int(patient_age),
        is_independent=False,
        token=token,
        patient_email=device_email,
        expiration_date=expiration_dt,
    )

    test_url = request.build_absolute_uri(f"/htmx/take_test/{token}/")

    return JsonResponse({
        "success": True,
        "test_id": test.id,
        "token": str(token),
        "link": test_url,
        "sent_to": device_email,
        "expires": timezone.localtime(expiration_dt).strftime("%m/%d/%Y at %I:%M %p"),
        "created_at": timezone.localtime(test.created_at).strftime("%m/%d/%Y at %I:%M %p") if test.created_at else "",
    })


@require_GET
def take_test(request, token):
    from datetime import datetime, timezone as dt_timezone

    test = get_object_or_404(Test, token=token)

    if test.expiration_date and datetime.now(dt_timezone.utc) > test.expiration_date:
        test.status = "expired"
        test.save(update_fields=["status"])
        return render(request, "htmx/test_expired.html", {"test": test})

    if test.status == "completed":
        return render(request, "htmx/test_already_completed.html", {"test": test})

    if test.status == "pending":
        test.status = "active"
        test.save(update_fields=["status"])

    # Only create stimuli if they don't exist for this test
    if not test.stimuli.exists():
        # Get baseline stimuli from any completed test (they're the same for all tests)
        baseline_test = Test.objects.filter(status="completed").first()
        
        if baseline_test and baseline_test.stimuli.exists():
            # Use existing stimuli from completed test as template
            baseline_stimuli = baseline_test.stimuli.all()
            
            # Get all digit stimuli (4-span and 5-span)
            digit_4_span = list(baseline_stimuli.filter(stimulus_type="digit", span_length=4))
            digit_5_span = list(baseline_stimuli.filter(stimulus_type="digit", span_length=5))
            
            # Get all mixed stimuli (4-span and 5-span)
            mixed_4_span = list(baseline_stimuli.filter(stimulus_type="mixed", span_length=4))
            mixed_5_span = list(baseline_stimuli.filter(stimulus_type="mixed", span_length=5))
            
            # Shuffle each group to randomize order
            random.shuffle(digit_4_span)
            random.shuffle(digit_5_span)
            random.shuffle(mixed_4_span)
            random.shuffle(mixed_5_span)
            
            # Combine: all 3 from 4-span + all 3 from 5-span for each type
            digit_stimuli = digit_4_span + digit_5_span  # 6 total
            mixed_stimuli = mixed_4_span + mixed_5_span  # 6 total
            
            # Create digit stimuli for this test (in randomized order)
            for stim in digit_stimuli:
                Stimulus.objects.create(
                    test=test,
                    stimulus_string=stim.stimulus_string,
                    correct_answer=stim.correct_answer,
                    stimulus_type=stim.stimulus_type,
                    span_length=stim.span_length,
                )
            
            # Create mixed stimuli for this test (in randomized order)
            for stim in mixed_stimuli:
                Stimulus.objects.create(
                    test=test,
                    stimulus_string=stim.stimulus_string,
                    correct_answer=stim.correct_answer,
                    stimulus_type=stim.stimulus_type,
                    span_length=stim.span_length,
                )
        else:
            # Fallback: manually create from fixture data if no completed tests exist
            # Use EXACT fixture data - do not modify
            digit_4_span_data = [
                ("1478", "1478", "digit", 4),
                ("9356", "3569", "digit", 4),
                ("9732", "2379", "digit", 4),
            ]
            digit_5_span_data = [
                ("35486", "34568", "digit", 5),
                ("48973", "34789", "digit", 5),
                ("14982", "12489", "digit", 5),
            ]
            mixed_4_span_data = [
                ("A2L6", "26AL", "mixed", 4),
                ("7LU5", "57LU", "mixed", 4),
                ("F82I", "28FI", "mixed", 4),
            ]
            mixed_5_span_data = [
                ("UC86F", "68CFU", "mixed", 5),
                ("5KI76", "567IK", "mixed", 5),
                ("2L48K", "248KL", "mixed", 5),
            ]
            
            # Shuffle each group to randomize order
            random.shuffle(digit_4_span_data)
            random.shuffle(digit_5_span_data)
            random.shuffle(mixed_4_span_data)
            random.shuffle(mixed_5_span_data)
            
            # Combine in order: digit (4-span then 5-span), then mixed (4-span then 5-span)
            all_stimuli = digit_4_span_data + digit_5_span_data + mixed_4_span_data + mixed_5_span_data
            
            for stimulus_string, correct_answer, stimulus_type, span_length in all_stimuli:
                Stimulus.objects.create(
                    test=test,
                    stimulus_string=stimulus_string,
                    correct_answer=correct_answer,
                    stimulus_type=stimulus_type,
                    span_length=span_length,
                )

    # Get all stimuli for this test in the order they were created (already randomized)
    all_stimuli = list(test.stimuli.all())
    
    # Separate by type (maintains creation order which is already randomized)
    digit_stimuli = [s for s in all_stimuli if s.stimulus_type == "digit"]
    mixed_stimuli = [s for s in all_stimuli if s.stimulus_type == "mixed"]
    
    # Create mapping for templates
    stimulus_ids_keyed = {}
    
    # Map digit stimuli (should be 6)
    for i, stim in enumerate(digit_stimuli, 1):
        stimulus_ids_keyed[f"digit_stimuli_{i}"] = stim.id
    
    # Map mixed stimuli (should be 6)
    for i, stim in enumerate(mixed_stimuli, 1):
        stimulus_ids_keyed[f"mixed_stimuli_{i}"] = stim.id

    request.session["current_test_id"]           = test.id
    request.session["current_test_type"]          = "full"
    request.session["current_test_stimulus_ids"]  = stimulus_ids_keyed
    request.session["current_stimulus_index"]     = 0
    request.session["lang"]                       = "en"

    return redirect("htmx:SelectLanguage")

@login_required
@require_GET
def doctor_test_results(request):
    return render(request, 'htmx/doctorportal/doctor_test_results.html', {
        "user": request.user
    })
@login_required
@require_GET
def doctor_test_result(request, test_id):
    return render(request, 'htmx/doctorportal/doctor_test_result.html', {'test_id': test_id})
@login_required
@require_http_methods(["GET", "POST"])
def doctor_settings(request):
    profile_errors = []

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        middle_initial = request.POST.get("middle_initial", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        organization_name = request.POST.get("organization_name", "").strip()
        office_name = request.POST.get("office_name", "").strip()

        if not first_name:
            profile_errors.append("First name is required.")
        if not last_name:
            profile_errors.append("Last name is required.")
        if not email:
            profile_errors.append("Email is required.")
        if not organization_name:
            profile_errors.append("Hospital/Organization is required.")
        if not office_name:
            profile_errors.append("Doctor's Office/Practice Name is required.")

        if middle_initial and len(middle_initial) > 1:
            profile_errors.append("Middle initial must be one character.")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                profile_errors.append("Enter a valid email address.")

        if not profile_errors:
            request.user.first_name = first_name
            request.user.middle_initial = middle_initial.upper()
            request.user.last_name = last_name
            request.user.email = email
            request.user.organization_name = organization_name
            request.user.office_name = office_name
            request.user.save(update_fields=[
                "first_name",
                "middle_initial",
                "last_name",
                "email",
                "organization_name",
                "office_name",
            ])
            return redirect("htmx:doctor_settings")

    return render(request, 'htmx/doctorportal/doctor_settings.html', {
        "user": request.user,
        "show_edit_form": request.method == "POST" or request.GET.get("edit") == "1",
        "profile_errors": profile_errors,
    })

@require_GET
def doctor_support(request):
    return render(request, 'htmx/doctorportal/doctor_support.html', {})

def doctor_logout(request):
    logout(request)
    return redirect('htmx:doctor_login')

@require_GET
def doctor_forgot_password(request):
    return render(request, 'htmx/doctorportal/doctor_forgot_password.html', {})

@require_GET
def demo_bootstrap(request):
    return render(request, 'htmx/demo_bootstrap.html', {})


# POST request example
@require_POST
def answer(request):
    try:
        value = int(request.POST['value'])
        func = request.POST['function']
        if func == "square":
            return render(request, "htmx/partials/answer.html", {'answer': value*value })
        else:
            return render(request, "htmx/partials/answer.html", {'answer': value*value*value })
    except:
        return render(request, "htmx/partials/answer.html",{'answer': "Invalid"})
    

@require_POST
def answer1(request):
    try:
        value = int(request.POST['value1'])
        func = request.POST['function1']
        if func == "square":
            return render(request, "htmx/partials/answer.html", {'answer': value*value })
        else:
            return render(request, "htmx/partials/answer.html", {'answer': value*value*value })
    except:
        return render(request, "htmx/partials/answer.html",{'answer': "Invalid"})

@require_GET
def oneimage(request):
    return render(request, 'htmx/partials/image.html', randomimg())

@require_GET
def example1(request):
    return render(request, 'htmx/example1.html', {})

@require_GET
def example2(request):
    return render(request, 'htmx/example2.html', {})

@require_GET
def example3(request):
    return render(request, 'htmx/example3.html', randomimg())

@require_GET
def example4(request):
    return render(request, 'htmx/example4.html', {
        'projects': Project.objects.all()
    })

@require_POST
def tasks4project(request):
    try:
        id = int(request.POST['id'])
        tasks = Task.objects.filter(project__id=id)
        return render(request, "htmx/partials/tasks.html", {
            'tasks': tasks            
        })
    except:
        return render(request, "htmx/partials/tasks.html", {
            'tasks': []             
        })
    
@require_GET
def member4task(request, id):
    try:
        # name = int(request.POST['name'])
        task = Task.objects.get(id=id)
        return render(request, "htmx/partials/member.html", {
            'member': task.assignee          
        })
    except:
        return render(request, "htmx/partials/member.html", {
            'member': []             
        })


@require_GET
def jsdemo(request):
    return render(request, "htmx/jsdemo.html", {})


@require_POST
def jsresponse(request):
    times = request.POST['response']
    responses = times.split(" ")
    previous = int(responses[0])
    responses.pop(0)
    answer = "Server received: "
    for response in responses:
        values = response.split(':')
        button = values[0]
        latency = (int(values[1]) - previous)/1000
        previous = int(values[1])
        answer = f"{answer} Button {button} after a latency of {latency} seconds. "
    return render(request, "htmx/partials/times.html",{
        'answer': answer
    }) 

@require_GET
def practice_digit_stimuli_1(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_1.html", {
        "lang": lang,
        "text": PRACTICE_DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_digit_stimuli_1_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_1_response.html", {
        "lang": lang,
        "text": PRACTICE_DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def practice_digit_stimuli_2(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_2.html", {
        "lang": lang,
        "text": PRACTICE_DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_digit_stimuli_2_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_2_response.html", {
        "lang": lang,
        "text": PRACTICE_DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_1(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 1:
            sequence = list(digit_stimuli[0]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_1")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_1.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 1,
        "next_url": "htmx:digitStimuli1Response",
    })


@require_GET
def digit_stimuli_1_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_1_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_2(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 2:
            sequence = list(digit_stimuli[1]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_2")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_2.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 2,
        "next_url": "htmx:digitStimuli2Response",
    })
@require_GET
def digit_stimuli_2_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_2_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_3(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 3:
            sequence = list(digit_stimuli[2]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_3")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_3.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 3,
        "next_url": "htmx:digitStimuli3Response",
    })
@require_GET
def digit_stimuli_3_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_3_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_4(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 4:
            sequence = list(digit_stimuli[3]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_4")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_4.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 4,
        "next_url": "htmx:digitStimuli4Response",
    })
@require_GET
def digit_stimuli_4_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_4_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_5(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 5:
            sequence = list(digit_stimuli[4]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_5")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_5.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 5,
        "next_url": "htmx:digitStimuli5Response",
    })
@require_GET
def digit_stimuli_5_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_5_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_6(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        digit_stimuli = request.session.get("digit_stimuli", [])
        if len(digit_stimuli) >= 6:
            sequence = list(digit_stimuli[5]["sequence"])
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("digit_stimuli_6")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["1", "4", "7", "8"]  # Fallback

    return render(request, "htmx/digit_stimuli_6.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 6,
        "next_url": "htmx:digitStimuli6Response",
    })
@require_GET
def digit_stimuli_6_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_6_response.html", {
        "lang": lang,
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_practice_instructions(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_practice_instructions.html", {
        "lang": lang,
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })
    
@require_GET
def practice_mixed_stimuli_1(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_1.html", {
        "lang": lang,
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_mixed_stimuli_1_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_1_response.html", {
        "lang": lang,
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })
    
@require_GET
def practice_mixed_stimuli_2(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_2.html", {
        "lang": lang,
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def practice_mixed_stimuli_2_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_2_response.html", {
        "lang": lang,
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_actual_instructions(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_actual_instructions.html", {
        "lang": lang,
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_1(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 1:
            sequence = list(mixed_stimuli[0]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_1")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_1.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 1,
        "next_url": "htmx:mixedStimuli1Response",
    })
@require_GET
def mixed_stimuli_1_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_1_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_stimuli_2(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 2:
            sequence = list(mixed_stimuli[1]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_2")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_2.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 2,
        "next_url": "htmx:mixedStimuli2Response",
    })
@require_GET
def mixed_stimuli_2_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_2_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_stimuli_3(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 3:
            sequence = list(mixed_stimuli[2]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_3")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_3.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 3,
        "next_url": "htmx:mixedStimuli3Response",
    })
@require_GET
def mixed_stimuli_3_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_3_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_stimuli_4(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 4:
            sequence = list(mixed_stimuli[3]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_4")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_4.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 4,
        "next_url": "htmx:mixedStimuli4Response",
    })
@require_GET
def mixed_stimuli_4_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_4_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_stimuli_5(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 5:
            sequence = list(mixed_stimuli[4]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_5")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_5.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 5,
        "next_url": "htmx:mixedStimuli5Response",
    })
@require_GET
def mixed_stimuli_5_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_5_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_stimuli_6(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    # Check if this is an independent test
    if request.session.get("independent_test"):
        # Get from session array
        mixed_stimuli = request.session.get("mixed_stimuli", [])
        if len(mixed_stimuli) >= 6:
            sequence = list(mixed_stimuli[5]["sequence"])
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback
    else:
        # Get from database (doctor-created test)
        stimulus_ids = request.session.get("current_test_stimulus_ids", {})
        stimulus_id = stimulus_ids.get("mixed_stimuli_6")
        
        if stimulus_id:
            stimulus = get_object_or_404(Stimulus, id=stimulus_id)
            sequence = list(stimulus.stimulus_string)
        else:
            sequence = ["A", "2", "L", "6"]  # Fallback

    return render(request, "htmx/mixed_stimuli_6.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "sequence": json.dumps(sequence),
        "stimulus_number": 6,
        "next_url": "htmx:mixedStimuli6Response",
    })
@require_GET
def mixed_stimuli_6_response(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_6_response.html", {
        "lang": lang,
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def exit(request):
    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/exit.html", {
        "lang": lang,
        "text": TEST_COMPLETION_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

# independent test calculate age group
def calculate_independent_age_group(num_correct, total_answered):
    if total_answered <= 0:
        return "60+", 0

    accuracy = round((num_correct / total_answered) * 100, 1)

    if accuracy >= 90:
        age_group = "20-29"
    elif accuracy >= 80:
        age_group = "30-39"
    elif accuracy >= 70:
        age_group = "40-49"
    elif accuracy >= 60:
        age_group = "50-59"
    else:
        age_group = "60+"

    return age_group, accuracy

#independent test responses
@require_POST
def submit_independent_test_responses(request):
    if not request.session.get("independent_test"):
        return JsonResponse({"error": "No active independent test session found."}, status=400)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    submitted_responses = payload.get("responses", [])
    if not isinstance(submitted_responses, list):
        return JsonResponse({"error": "Responses payload must be a list."}, status=400)

    # Get stimuli from session
    digit_stimuli = request.session.get("digit_stimuli", [])
    mixed_stimuli = request.session.get("mixed_stimuli", [])
    
    combined_stimuli = (
        [{**stimulus, "stimulus_type": "digit"} for stimulus in digit_stimuli] +
        [{**stimulus, "stimulus_type": "mixed"} for stimulus in mixed_stimuli]
    )

    stimuli_map = {}
    for stimulus in combined_stimuli:
        stimuli_map[stimulus["key"]] = stimulus

    num_correct = 0
    num_incorrect = 0
    total_time = 0
    saved_responses = []

    for item in submitted_responses:
        stimulus_key = item.get("stimulus_key")
        stimulus = stimuli_map.get(stimulus_key)

        if not stimulus:
            continue

        response_string = str(item.get("response_string", ""))
        is_correct = response_string == stimulus["correct_answer"]

        if is_correct:
            num_correct += 1
        else:
            num_incorrect += 1

        started_at = item.get("started_at")
        submitted_at = item.get("submitted_at")

        response_time = 0
        if isinstance(started_at, int) and isinstance(submitted_at, int) and submitted_at >= started_at:
            response_time = submitted_at - started_at
            total_time += response_time

        saved_responses.append({
            "stimulus_key": stimulus_key,
            "stimulus_type": stimulus["stimulus_type"],
            "sequence": stimulus["sequence"],
            "correct_answer": stimulus["correct_answer"],
            "response_string": response_string,
            "is_correct": is_correct,
            "response_time": response_time,
        })

    from datetime import datetime
    started_at_iso = request.session.get("test_started_at")
    if started_at_iso:
        started_at_dt = datetime.fromisoformat(started_at_iso)
        wall_total_time = int((timezone.now() - started_at_dt).total_seconds() * 1000)
    else:
        wall_total_time = total_time

    total_answered = num_correct + num_incorrect
    age_group, accuracy = calculate_independent_age_group(num_correct, total_answered)

    request.session["independent_results"] = {
        "num_correct": num_correct,
        "num_incorrect": num_incorrect,
        "response_time": total_time,
        "total_time": wall_total_time,
        "accuracy": accuracy,
        "age_group": age_group,
        "responses": saved_responses,
    }

    return JsonResponse({
        "ok": True,
        "redirect_url": "/htmx/independentTestResults"
    })

#independent results
@require_GET
def independent_test_results(request):
    if not request.session.get("independent_test"):
        return redirect("htmx:home")

    results = request.session.get("independent_results")
    if not results:
        return redirect("htmx:home")

    lang = request.session.get("lang", "en")
    current_theme = get_current_theme(request)

    return render(request, "htmx/independent_test_results.html", {
        "lang": lang,
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "results": results,
    })

@require_POST
def submit_test_responses(request):
    current_test_id = request.session.get("current_test_id")
    stimulus_ids = request.session.get("current_test_stimulus_ids", {})

    if not current_test_id or not stimulus_ids:
        return JsonResponse({"error": "No active test session found."}, status=400)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    submitted_responses = payload.get("responses", [])
    if not isinstance(submitted_responses, list):
        return JsonResponse({"error": "Responses payload must be a list."}, status=400)

    test = get_object_or_404(Test, id=current_test_id)

    with transaction.atomic():
        Response.objects.filter(test=test).delete()

        num_correct = 0
        num_incorrect = 0
        total_time = 0

        for item in submitted_responses:
            stimulus_key = item.get("stimulus_key")
            stimulus_id = stimulus_ids.get(stimulus_key)
            if not stimulus_id:
                continue

            stimulus = get_object_or_404(Stimulus, id=stimulus_id, test=test)
            response_string = str(item.get("response_string", ""))
            response = Response.objects.create(
                test=test,
                stimulus=stimulus,
                response_string=response_string,
                is_correct=response_string == stimulus.correct_answer,
            )

            if response.is_correct:
                num_correct += 1
            else:
                num_incorrect += 1

            started_at = item.get("started_at")
            if isinstance(started_at, int):
                submitted_at = item.get("submitted_at", started_at)
                if isinstance(submitted_at, int) and submitted_at >= started_at:
                    total_time += submitted_at - started_at

            previous_timestamp = started_at
            for index, click in enumerate(item.get("clicks", []), start=1):
                click_value = str(click.get("value", ""))[:1]
                click_timestamp = click.get("timestamp")
                if not click_value or not isinstance(click_timestamp, int):
                    continue

                latency_time = 0
                if isinstance(previous_timestamp, int) and click_timestamp >= previous_timestamp:
                    latency_time = click_timestamp - previous_timestamp
                previous_timestamp = click_timestamp

                Latency.objects.create(
                    response=response,
                    input_order=index,
                    input_value=click_value,
                    time=latency_time,
                )

        from datetime import datetime
        started_at_iso = request.session.get("test_started_at")
        if started_at_iso:
            started_at_dt = datetime.fromisoformat(started_at_iso)
            wall_total_time = int((timezone.now() - started_at_dt).total_seconds() * 1000)
        else:
            wall_total_time = total_time

        Results.objects.update_or_create(
            test=test,
            defaults={
                "total_time": wall_total_time,
                "response_time": total_time,
                "num_of_correct": num_correct,
                "num_of_incorrect": num_incorrect,
            },
        )

        test.status = "completed"
        test.save(update_fields=["status"])

    for key in ("current_test_id", "current_test_type", "current_test_stimulus_ids", "test_started_at"):
        request.session.pop(key, None)

    return JsonResponse({"ok": True})

@login_required
def doctor_test_results(request):
    tests = Test.objects.filter(doctor=request.user).select_related('results')

    completed_tests = tests.filter(status='completed', results__isnull=False)

    # ----------------------------
    # SUMMARY
    # ----------------------------
    completed_tests_count = completed_tests.count()

    avg_completion_time = completed_tests.aggregate(
        avg_time=Avg('results__total_time')
    )['avg_time']

    avg_response_time = completed_tests.aggregate(
        avg_time=Avg('results__response_time')
    )['avg_time']

    # ----------------------------
    # AGE GROUP CHART
    # ----------------------------
    age_groups = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "60+": 0
    }

    for test in completed_tests:
        age = test.test_taker_age

        if age <= 20:
            age_groups["0-20"] += 1
        elif age <= 40:
            age_groups["21-40"] += 1
        elif age <= 60:
            age_groups["41-60"] += 1
        else:
            age_groups["60+"] += 1

    age_chart_labels = list(age_groups.keys())
    age_chart_data = list(age_groups.values())

    # ----------------------------
    # ACCURACY OVER TESTS
    # ----------------------------
    accuracy_chart_labels = []
    accuracy_chart_data = []

    for test in completed_tests.order_by('id'):
        try:
            result = test.results
            accuracy_chart_labels.append(f"Test {test.id}")
            accuracy_chart_data.append(round(result.accuracy, 2))
        except:
            pass

    # ----------------------------
    # COMPLETION TIME CHART
    # Only the 10 most recent completed tests, store in SECONDS instead of ms
    # ----------------------------
    completion_chart_labels = []
    completion_chart_data = []

    recent_completed = list(completed_tests.order_by('-created_at')[:10])
    recent_completed.reverse()  # oldest → newest left to right on chart
    for test in recent_completed:
        try:
            result = test.results
            completion_chart_labels.append(f"Test {test.id}")
            completion_chart_data.append(round(result.total_time / 1000, 2))
        except:
            pass

    # ----------------------------
    # DISPLAY FRIENDLY TABLE VALUES
    # ----------------------------
    for test in tests:
        try:
            test.formatted_total_time = format_ms(test.results.total_time)
        except:
            test.formatted_total_time = "--"

    # ----------------------------
    # SORT: active (in progress) + pending (not started) by id first,
    # then completed (newest first), then expired
    # Uses Python sort so we never touch the DB ordering
    # ----------------------------
    STATUS_ORDER = {'active': 0, 'pending': 1, 'completed': 2, 'expired': 3}

    def sort_key(t):
        status_rank = STATUS_ORDER.get(t.status, 4)
        if t.status == 'completed':
            ts = t.created_at.timestamp() if t.created_at else 0
            return (status_rank, -ts, t.id)
        return (status_rank, 0, t.id)

    sorted_tests = sorted(list(tests), key=sort_key)

    context = {
        "tests": sorted_tests,
        "completed_tests_count": completed_tests_count,

        # raw values if ever needed
        "avg_completion_time": round(avg_completion_time, 2) if avg_completion_time else "--",
        "avg_response_time": round(avg_response_time, 2) if avg_response_time else "--",

        # display values
        "avg_completion_time_display": format_ms(avg_completion_time) if avg_completion_time else "--",
        "avg_response_time_display": format_ms(avg_response_time) if avg_response_time else "--",

        "age_chart_labels": json.dumps(age_chart_labels),
        "age_chart_data": json.dumps(age_chart_data),

        "accuracy_chart_labels": json.dumps(accuracy_chart_labels),
        "accuracy_chart_data": json.dumps(accuracy_chart_data),

        "completion_chart_labels": json.dumps(completion_chart_labels),
        "completion_chart_data": json.dumps(completion_chart_data),
    }

    return render(request, "htmx/doctorportal/doctor_test_results.html", context)

def get_age_group(age):
    """Map a test taker’s age to a readable age group."""
    if 12 <= age <= 17:
        return "12-17"
    elif 18 <= age <= 25:
        return "18-25"
    elif 26 <= age <= 40:
        return "26-40"
    elif 41 <= age <= 60:
        return "41-60"
    else:
        return "60+"
    
def format_ms(ms):
    """Convert milliseconds to a readable time string."""
    if ms is None:
        return "--"

    total_seconds = int(round(ms / 1000))

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    if minutes > 0:
        return f"{minutes} min {seconds} sec"
    return f"{seconds} sec"


@login_required
def doctor_test_result(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    # Fetch the related Results object safely
    result = getattr(test, 'results', None)

    # Compute age group
    age_group_label = get_age_group(test.test_taker_age)

    # Handle "60+" safely
    if "+" in age_group_label:
        age_min = int(age_group_label.replace("+", ""))
        age_group_tests = Test.objects.filter(
            test_taker_age__gte=age_min,
            status='completed'
        )
    else:
        age_min, age_max = map(int, age_group_label.split('-'))
        age_group_tests = Test.objects.filter(
            test_taker_age__gte=age_min,
            test_taker_age__lte=age_max,
            status='completed'
        )

    # Pull completed results only
    completed_results = [t.results for t in age_group_tests if hasattr(t, 'results')]

    if completed_results:
        avg_accuracy = round(sum(r.accuracy for r in completed_results) / len(completed_results), 1)
        avg_completion = round(sum(r.total_time for r in completed_results) / len(completed_results), 1)
        avg_response = round(sum(r.response_time for r in completed_results) / len(completed_results), 1)
        avg_correct = round(sum(r.num_of_correct for r in completed_results) / len(completed_results), 1)
        avg_incorrect = round(sum(r.num_of_incorrect for r in completed_results) / len(completed_results), 1)
    else:
        avg_accuracy = "--"
        avg_completion = None
        avg_response = None
        avg_correct = "--"
        avg_incorrect = "--"

    context = {
        "test": test,
        "result": result,
        "age_group_label": age_group_label,

        "avg_accuracy": avg_accuracy,
        "avg_completion": avg_completion,
        "avg_response": avg_response,
        "avg_correct": avg_correct,
        "avg_incorrect": avg_incorrect,

        # Display-friendly formatted values
        "patient_completion_display": format_ms(result.total_time) if result else "--",
        "avg_completion_display": format_ms(avg_completion) if avg_completion is not None else "--",

        "patient_response_display": format_ms(result.response_time) if result else "--",
        "avg_response_display": format_ms(avg_response) if avg_response is not None else "--",
    }

    return render(request, "htmx/doctorportal/doctor_test_result.html", context)

@login_required
def doctor_test_result_csv(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    result = getattr(test, "results", None)  # link to Results

    # Determine age group dynamically
    def get_age_group(age):
        if 12 <= age <= 17:
            return "12-17", 12, 17
        elif 18 <= age <= 25:
            return "18-25", 18, 25
        elif 26 <= age <= 40:
            return "26-40", 26, 40
        elif 41 <= age <= 60:
            return "41-60", 41, 60
        else:
            return "60+", 61, 200

    age_label, age_min, age_max = get_age_group(test.test_taker_age)

    # Filter completed tests in the same age group
    age_group_tests = Test.objects.filter(
        test_taker_age__gte=age_min,
        test_taker_age__lte=age_max,
        status='completed'
    )
    completed_results = [t.results for t in age_group_tests if hasattr(t, 'results')]

    if completed_results:
        avg_accuracy = round(sum(r.accuracy for r in completed_results) / len(completed_results), 1)
        avg_completion = round(sum(r.total_time for r in completed_results) / len(completed_results), 1)
    else:
        avg_accuracy = "--"
        avg_completion = "--"

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="test_{test.id}_results.csv"'
    writer = csv.writer(response)

    # --- Test Info Section ---
    writer.writerow(['Test Information'])
    writer.writerow(['Test ID', test.id])
    writer.writerow(['Status', test.get_status_display()])
    writer.writerow(['Created At', timezone.localtime(test.created_at).strftime('%m/%d/%Y %I:%M %p') if test.created_at else '--'])
    writer.writerow(['Expiration Date', timezone.localtime(test.expiration_date).strftime('%m/%d/%Y %I:%M %p') if test.expiration_date else '--'])
    writer.writerow(['Test Taker Age', test.test_taker_age])
    writer.writerow(['Age Group', age_label])
    writer.writerow(['Independent', 'Yes' if test.is_independent else 'No'])
    writer.writerow([])

    # --- Summary Section ---
    writer.writerow(['Summary', 'Patient', f'Average for Age {age_label}'])
    writer.writerow(['Accuracy (%)', round(result.accuracy, 1) if result else "--", avg_accuracy])
    writer.writerow(['Completion Time (ms)', result.total_time if result else "--", avg_completion])
    writer.writerow(['Completion Time (formatted)', format_ms(result.total_time) if result else "--", format_ms(avg_completion) if isinstance(avg_completion, (int, float)) else "--"])
    writer.writerow(['Avg Response Time (ms)', result.response_time if result else "--", "--"])
    writer.writerow(['Correct Responses', result.num_of_correct if result else "--", "--"])
    writer.writerow(['Incorrect Responses', result.num_of_incorrect if result else "--", "--"])
    total_answered = (result.num_of_correct + result.num_of_incorrect) if result else 0
    writer.writerow(['Total Responses', total_answered if result else "--", "--"])
    writer.writerow([])

    # --- Detailed Responses Section ---
    responses = Response.objects.filter(test=test).select_related('stimulus').prefetch_related('latencies')
    writer.writerow(['Detailed Responses'])
    writer.writerow(['#', 'Stimulus', 'Type', 'Span Length', 'Correct Answer', 'Patient Response', 'Correct?', 'Total Latency (ms)', 'Latency per Input (ms)'])
    for i, resp in enumerate(responses, start=1):
        latencies = Latency.objects.filter(response=resp).order_by('input_order')
        latency_values = [l.time for l in latencies]
        latency_str = ", ".join(str(t) for t in latency_values)
        total_latency = sum(latency_values) if latency_values else "--"
        writer.writerow([
            i,
            resp.stimulus.stimulus_string,
            resp.stimulus.stimulus_type.capitalize(),
            resp.stimulus.span_length,
            resp.stimulus.correct_answer,
            resp.response_string,
            "Yes" if resp.is_correct else "No",
            total_latency,
            latency_str
        ])
    writer.writerow([])

    # --- Aggregate Stats by Stimulus Type ---
    stimulus_types = responses.values_list('stimulus__stimulus_type', flat=True).distinct()
    writer.writerow(['Aggregate by Stimulus Type'])
    writer.writerow(['Type', 'Total Responses', 'Correct', 'Incorrect', 'Accuracy (%)', 'Avg Completion Time (ms)', 'Avg Response Time (ms)'])
    for stype in stimulus_types:
        type_responses = [r for r in responses if r.stimulus.stimulus_type == stype]
        if type_responses:
            correct_count = sum(1 for r in type_responses if r.is_correct)
            incorrect_count = len(type_responses) - correct_count
            type_accuracy = round(correct_count / len(type_responses) * 100, 1) if type_responses else "--"
            type_results = [r for r in type_responses if hasattr(r.test, 'results')]
            if type_results:
                avg_comp = round(sum(r.test.results.total_time for r in type_results)/len(type_results), 1)
                avg_resp = round(sum(r.test.results.response_time for r in type_results)/len(type_results), 1)
            else:
                avg_comp = avg_resp = "--"
            writer.writerow([stype.capitalize(), len(type_responses), correct_count, incorrect_count, type_accuracy, avg_comp, avg_resp])
    writer.writerow([])

    # --- Stats by Span Length ---
    span_lengths = sorted(responses.values_list('stimulus__span_length', flat=True).distinct())
    writer.writerow(['Aggregate by Span Length'])
    writer.writerow(['Span Length', 'Total Trials', 'Correct Trials', 'Incorrect Trials', 'Accuracy (%)'])
    for span in span_lengths:
        span_responses = [r for r in responses if r.stimulus.span_length == span]
        if span_responses:
            correct_count = sum(1 for r in span_responses if r.is_correct)
            incorrect_count = len(span_responses) - correct_count
            span_accuracy = round(correct_count / len(span_responses) * 100, 1)
            writer.writerow([span, len(span_responses), correct_count, incorrect_count, span_accuracy])
    writer.writerow([])

    # --- Latency Analysis ---
    writer.writerow(['Latency Analysis'])
    writer.writerow(['Stimulus', 'Type', 'Span Length', 'Input #', 'Input Value', 'Latency (ms)'])
    for resp in responses:
        latencies = Latency.objects.filter(response=resp).order_by('input_order')
        for lat in latencies:
            writer.writerow([
                resp.stimulus.stimulus_string,
                resp.stimulus.stimulus_type.capitalize(),
                resp.stimulus.span_length,
                lat.input_order,
                lat.input_value,
                lat.time
            ])
    writer.writerow([])

    # --- Age Group Comparison ---
    writer.writerow(['Age Group Comparison'])
    writer.writerow(['Metric', f'This Patient (Age {test.test_taker_age})', f'Age Group Average ({age_label})'])
    writer.writerow(['Accuracy (%)', round(result.accuracy, 1) if result else "--", avg_accuracy])
    writer.writerow(['Completion Time (ms)', result.total_time if result else "--", avg_completion])

    return response