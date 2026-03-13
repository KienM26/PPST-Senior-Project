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
    path("digit_stimuli_1", views.digit_stimuli_1, name="digitStimuli1"),
    path("digit_stimuli_1_response", views.digit_stimuli_1_response, name="digitStimuli1Response"),
    path("digit_stimuli_2", views.digit_stimuli_2, name="digitStimuli2"),
    path("digit_stimuli_2_response", views.digit_stimuli_2_response, name="digitStimuli2Response"),
    path("digit_stimuli_3", views.digit_stimuli_3, name="digitStimuli3"),
    path("digit_stimuli_3_response", views.digit_stimuli_3_response, name="digitStimuli3Response"),
    path("digit_stimuli_4", views.digit_stimuli_4, name="digitStimuli4"),
    path("digit_stimuli_4_response", views.digit_stimuli_4_response, name="digitStimuli4Response"),
    path("digit_stimuli_5", views.digit_stimuli_5, name="digitStimuli5"),
    path("digit_stimuli_5_response", views.digit_stimuli_5_response, name="digitStimuli5Response"),
    path("digit_stimuli_6", views.digit_stimuli_6, name="digitStimuli6"),
    path("digit_stimuli_6_response", views.digit_stimuli_6_response, name="digitStimuli6Response"),
    path("practice_digit_stimuli_1_response", views.practice_digit_stimuli_1_response, name="practiceDigitStimuli1Response"),
    path("practice_digit_stimuli_1", views.practice_digit_stimuli_1, name="practiceDigitStimuli1"),
    path("practice_digit_stimuli_2_response", views.practice_digit_stimuli_2_response, name="practiceDigitStimuli2Response"),
    path("practice_digit_stimuli_2", views.practice_digit_stimuli_2, name="practiceDigitStimuli2")


]