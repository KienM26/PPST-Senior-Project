from django.urls import path

from . import views

app_name = "htmx"

## if you want to go to a certain page go type in the name of that page
## Ex. http://127.0.0.1:8000/htmx/selectLanguage
## Ex. http://127.0.0.1:8000/htmx/accessibility
## Ex.

urlpatterns = [
    path("demo", views.demo, name="demo"),
    path("test", views.test, name="test"),
    path("practiceTest", views.practice_test, name="practiceTest"),
    path("practiceIntro", views.practice_test_intro, name="practiceIntro"),
    path("practiceTestNext", views.practice_test_next, name="practiceTestNext"),
    path("practiceTestPage", views.practice_test_page, name="practiceTestPage"),
    path("startPracticeTest", views.start_practice_test, name="startPracticeTest"),
    path("practiceStimulus", views.practice_stimulus, name="practiceStimulus"),
    path("doctorPortal", views.doctor_portal, name="doctorPortal"),
    path("selectLanguage", views.select_language, name="SelectLanguage"),
    path("accessibility", views.accessibility, name="Accessibility"),
    path("saveAccessibility", views.save_accessibility, name="saveAccessibility"),
    path("selectVoice", views.select_voice, name="selectVoice"),
    path("saveVoice", views.save_voice, name="saveVoice"),
    path("digitPracticeInstructions", views.digit_practice_instructions, name="digitPracticeInstructions"),
]