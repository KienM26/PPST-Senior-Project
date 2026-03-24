from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
import random


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
        "label": "English",
        "flag": "htmx/images/flag-usa.png",
    },
    "es": {
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
        "digit_practice_instruction_actual_test": "YOU ARE ABOUT TO BEGIN THE PPST TEST WITH DIGIT STIMULI. PLEASE CHOOSE THE START TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        "intro_button": "Next",
        "practice_heading": "Practice Test",
        "practice_body": [
            "YOU ARE ABOUT TO BEGIN THE PPST PRACTICE TEST WITH",
            "DIGIT STIMULI. YOU WILL GO THROUGH TWO PRACTICE",
            "STIMULUS AND RESPONSE PAGES. PLEASE CHOOSE THE START",
            "PRACTICE TEST BUTTON WHEN YOU ARE READY TO BEGIN.",
        ],
        "practice_button": "Start Practice Test",
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
        "digit_practice_instruction_actual_test": "ESTÁ A PUNTO DE COMENZAR LA PRUEBA PPST CON ESTÍMULOS DE DÍGITOS. POR FAVOR, ELIJA EL BOTÓN COMENZAR PRUEBA CUANDO ESTÉ LISTO PARA INICIAR.",
        "intro_button": "Siguiente",
        "practice_heading": "Prueba de Práctica",
        "practice_body": [
            "ESTÁ A PUNTO DE COMENZAR LA PRUEBA DE PRÁCTICA PPST CON",
            "ESTÍMULOS DE DÍGITOS. PASARÁ POR DOS PÁGINAS DE",
            "ESTÍMULO Y RESPUESTA DE PRÁCTICA. ELIJA EL BOTÓN",
            "COMENZAR PRÁCTICA CUANDO ESTÉ LISTO PARA INICIAR.",
        ],
        "practice_button": "Comenzar Práctica",
    }
}

PRACTICE_STIMULI_TEXT = {
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

STIMULI_TEXT = {
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


@require_GET
def practice_stimulus(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_stimulus.html", {
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_practice_instruction_actual_test(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_practice_instruction_actualTest.html", {
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

    return redirect("htmx:practiceTest")

@require_GET
def practice_test(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_test.html", {
        "text": PRACTICE_HOME_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_practice_instructions(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_practice_instructions.html", {
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
def doctor_portal(request):
    return render(request, 'htmx/doctor_portal.html', {})

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
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_1.html", {
        "text": PRACTICE_STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_digit_stimuli_1_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_1_response.html", {
        "text": PRACTICE_STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def practice_digit_stimuli_2(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_2.html", {
        "text": PRACTICE_STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def practice_digit_stimuli_2_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/practice_digit_stimuli_2_response.html", {
        "text": PRACTICE_STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_1(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_1.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_1_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_1_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_2(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_2.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_2_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_2_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_3(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_3.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_3_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_3_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_4(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_4.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_4_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_4_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_5(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_5.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })


@require_GET
def digit_stimuli_5_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_5_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_6(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_6.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

@require_GET
def digit_stimuli_6_response(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/digit_stimuli_6_response.html", {
        "text": STIMULI_TEXT[lang],
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })

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
def mixed_stimuli_practice_test(request):
    lang = get_current_lang(request)
    current_theme = get_current_theme(request)

    return render(request, "htmx/mixed_stimuli_practice_test.html", {
        "lang_info": LANGUAGE_INFO[lang],
        "current_theme": current_theme,
    })