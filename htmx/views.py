import csv
import random
import json

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from django.db.models import Avg

from database.models import Latency, Response, Results, Stimulus, Test

from datetime import date
import json


DIGIT_STIMULI_DATA = [
    {"key": "digit_stimuli_1", "sequence": "37K2M", "correct_answer": "237"},
    {"key": "digit_stimuli_2", "sequence": "49L1P", "correct_answer": "149"},
    {"key": "digit_stimuli_3", "sequence": "82Q5R", "correct_answer": "258"},
    {"key": "digit_stimuli_4", "sequence": "61S4T", "correct_answer": "146"},
    {"key": "digit_stimuli_5", "sequence": "93U2V", "correct_answer": "239"},
    {"key": "digit_stimuli_6", "sequence": "51W8X", "correct_answer": "158"},
]

MIXED_STIMULI_DATA = [
    {"key": "mixed_stimuli_1", "sequence": "37K2M", "correct_answer": "237KM"},
    {"key": "mixed_stimuli_2", "sequence": "37K2M", "correct_answer": "237KM"},
    {"key": "mixed_stimuli_3", "sequence": "37K2M", "correct_answer": "237KM"},
    {"key": "mixed_stimuli_4", "sequence": "37K2M", "correct_answer": "237KM"},
    {"key": "mixed_stimuli_5", "sequence": "37K2M", "correct_answer": "237KM"},
    {"key": "mixed_stimuli_6", "sequence": "37K2M", "correct_answer": "237KM"},
]


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
def start_practice_test(request):
    request.session["practice_test_started"] = True
    return redirect("htmx:practiceDigitStimuli1")


@require_POST
def start_digit_test(request):
    combined_stimuli = [
        {**stimulus, "stimulus_type": "digit"} for stimulus in DIGIT_STIMULI_DATA
    ] + [
        {**stimulus, "stimulus_type": "mixed"} for stimulus in MIXED_STIMULI_DATA
    ]

    test = Test.objects.create(
        status="active",
        test_taker_age=12,
        is_independent=True,
    )

    stimulus_ids = {}
    for stimulus in combined_stimuli:
        created = Stimulus.objects.create(
            test=test,
            stimulus_string=stimulus["sequence"],
            correct_answer=stimulus["correct_answer"],
            stimulus_type=stimulus["stimulus_type"],
            span_length=len(stimulus["sequence"]),
        )
        stimulus_ids[stimulus["key"]] = created.id

    request.session["current_test_id"] = test.id
    request.session["current_test_type"] = "full"
    request.session["current_test_stimulus_ids"] = stimulus_ids
    return redirect("htmx:digitStimuli1")


@require_POST
def start_mixed_test(request):
    if not request.session.get("current_test_id"):
        initialize_test_session(request, MIXED_STIMULI_DATA, "mixed")
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

@require_GET
def doctor_login(request):
    return render(request, 'htmx/doctorportal/doctor_login.html', {})

@require_GET
def doctor_create_account(request):
    return render(request, 'htmx/doctorportal/doctor_create_account.html', {})

@require_GET
def doctor_dashboard(request):
    return render(request, 'htmx/doctorportal/doctor_dashboard.html', {})

@require_GET
def doctor_create_test(request):
    return render(request, 'htmx/doctorportal/doctor_create_test.html', {})

@require_GET
def doctor_test_results(request):
    return render(request, 'htmx/doctorportal/doctor_test_results.html', {})

@require_GET
def doctor_test_result(request, test_id):
    return render(request, 'htmx/doctorportal/doctor_test_result.html', {'test_id': test_id})

@require_GET
def doctor_settings(request):
    return render(request, 'htmx/doctorportal/doctor_settings.html', {})

@require_GET
def doctor_support(request):
    return render(request, 'htmx/doctorportal/doctor_support.html', {})

def doctor_logout(request):
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
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_1.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_1_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_1_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_2(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_2.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_2_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_2_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_3(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_3.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_3_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_3_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_4(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_4.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_4_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_4_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_5(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_5.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_5_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_5_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_6(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_6.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_6_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_6_response.html", {
        "text": DIGIT_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def mixed_practice_instructions(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_practice_instructions.html", {
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
        "text": PRACTICE_TEXT[lang],  
    })
    
@require_GET
def practice_mixed_stimuli_1(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_1.html", {
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_mixed_stimuli_1_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_1_response.html", {
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })
    
@require_GET
def practice_mixed_stimuli_2(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_2.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def practice_mixed_stimuli_2_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_mixed_stimuli_2_response.html", {
        "text": PRACTICE_MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_actual_instructions(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_actual_instructions.html", {
        "text": PRACTICE_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_1(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_1.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })
    
@require_GET
def mixed_stimuli_1_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_1_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_2(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_2.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_2_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_2_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_3(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_3.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_3_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_3_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_4(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_4.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })
    
@require_GET
def mixed_stimuli_4_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_4_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_5(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_5.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_5_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_5_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_6(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_6.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def mixed_stimuli_6_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_6_response.html", {
        "text": MIXED_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def exit(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/exit.html", {
        "text": TEST_COMPLETION_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
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

        Results.objects.update_or_create(
            test=test,
            defaults={
                "total_time": total_time,
                "response_time": total_time,
                "num_of_correct": num_correct,
                "num_of_incorrect": num_incorrect,
            },
        )

        test.status = "completed"
        test.save(update_fields=["status"])

    for key in ("current_test_id", "current_test_type", "current_test_stimulus_ids"):
        request.session.pop(key, None)

    return JsonResponse({"ok": True})

def doctor_test_results(request):
    # Use all tests if user is anonymous
    if request.user.is_authenticated:
        tests = Test.objects.filter(doctor=request.user).select_related('results')
    else:
        tests = Test.objects.all().select_related('results')

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
    # Store chart values in SECONDS instead of ms
    # ----------------------------
    completion_chart_labels = []
    completion_chart_data = []

    for test in completed_tests.order_by('id'):
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

    context = {
        "tests": tests,
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

    # --- Summary Section ---
    writer.writerow(['Summary', 'Patient', f'Average for Age {age_label}'])
    writer.writerow(['Accuracy', result.accuracy if result else "--", avg_accuracy])
    writer.writerow(['Completion Time', result.total_time if result else "--", avg_completion])
    writer.writerow(['Avg Response', result.response_time if result else "--", "--"])
    writer.writerow(['Correct', result.num_of_correct if result else "--", "--"])
    writer.writerow(['Incorrect', result.num_of_incorrect if result else "--", "--"])
    writer.writerow(['Age', test.test_taker_age, age_label])
    writer.writerow([])

    # --- Detailed Responses Section ---
    writer.writerow(['Stimulus', 'Type', 'Span Length', 'Correct Answer', 'Patient Response', 'Correct?', 'Latency per Input (ms)'])
    responses = Response.objects.filter(test=test)
    for resp in responses:
        latencies = Latency.objects.filter(response=resp).order_by('input_order')
        latency_str = ", ".join(str(l.time) for l in latencies)
        writer.writerow([
            resp.stimulus.stimulus_string,
            resp.stimulus.stimulus_type,
            resp.stimulus.span_length,
            resp.stimulus.correct_answer,
            resp.response_string,
            "Yes" if resp.is_correct else "No",
            latency_str
        ])
    writer.writerow([])

    # --- Aggregate Stats by Stimulus Type ---
    stimulus_types = responses.values_list('stimulus__stimulus_type', flat=True).distinct()
    writer.writerow(['Aggregate by Stimulus Type', 'Average Accuracy', 'Average Completion Time (ms)', 'Average Response Time (ms)'])
    for stype in stimulus_types:
        type_responses = [r for r in responses if r.stimulus.stimulus_type == stype]
        if type_responses:
            type_results = [r for r in type_responses if hasattr(r.test, 'results')]
            if type_results:
                avg_acc = round(sum(r.test.results.accuracy for r in type_results)/len(type_results), 1)
                avg_comp = round(sum(r.test.results.total_time for r in type_results)/len(type_results), 1)
                avg_resp = round(sum(r.test.results.response_time for r in type_results)/len(type_results), 1)
            else:
                avg_acc = avg_comp = avg_resp = "--"
            writer.writerow([stype, avg_acc, avg_comp, avg_resp])
    writer.writerow([])

    # --- Stats by Span Length ---
    span_lengths = responses.values_list('stimulus__span_length', flat=True).distinct()
    writer.writerow(['Aggregate by Span Length', 'Average Correct', 'Average Incorrect'])
    for span in span_lengths:
        span_responses = [r for r in responses if r.stimulus.span_length == span]
        if span_responses:
            avg_correct = round(sum(r.is_correct for r in span_responses)/len(span_responses) * span, 1)
            avg_incorrect = span - avg_correct
            writer.writerow([span, avg_correct, avg_incorrect])

    return response