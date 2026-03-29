from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "htmx"

## if you want to go to a certain page go type in the name of that page
## Ex. http://127.0.0.1:8000/htmx/selectLanguage
## Ex. http://127.0.0.1:8000/htmx/accessibility
## Ex.

urlpatterns = [
    path("practiceTest", views.practice_test, name="practiceTest"),
    path("practiceIntro", views.practice_test_intro, name="practiceIntro"),
    path("practiceTestNext", views.practice_test_next, name="practiceTestNext"),
    path("practiceTestPage", views.practice_test_page, name="practiceTestPage"),
    path("startPracticeTest", views.start_practice_test, name="startPracticeTest"),
    path("practiceStimulus", views.practice_stimulus, name="practiceStimulus"),

    ##practice exam select language and accessibility
    path("selectLanguage", views.select_language, name="SelectLanguage"),
    path("accessibility", views.accessibility, name="Accessibility"),
    path("saveAccessibility", views.save_accessibility, name="saveAccessibility"),
    
    path("home", views.home, name="home"),

    ##select voice M/F
    path("selectVoice", views.select_voice, name="selectVoice"),
    path("digitPracticeInstructions", views.digit_practice_instructions, name="digitPracticeInstructions"),
    path("saveVoice", views.save_voice, name="saveVoice"),
    
    ##digit stimuli exam
    path("practice_digit_stimuli_1_response", views.practice_digit_stimuli_1_response, name="practiceDigitStimuli1Response"),
    path("practice_digit_stimuli_1", views.practice_digit_stimuli_1, name="practiceDigitStimuli1"),
    path("practice_digit_stimuli_2_response", views.practice_digit_stimuli_2_response, name="practiceDigitStimuli2Response"),
    path("practice_digit_stimuli_2", views.practice_digit_stimuli_2, name="practiceDigitStimuli2"),
    
    path("digitActualInstructions", views.digit_actual_instructions, name="digitActualInstructions"),

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

    ##mixed stimuli exam
    path("mixedPracticeInstructions", views.mixed_practice_instructions, name="mixedPracticeInstructions"),
    
    path("practice_mixed_stimuli_1", views.practice_mixed_stimuli_1, name="practiceMixedStimuli1"),
    path("practice_mixed_stimuli_1_response", views.practice_mixed_stimuli_1_response, name="practiceMixedStimuli1Response"),
    path("practice_mixed_stimuli_2", views.practice_mixed_stimuli_2, name="practiceMixedStimuli2"),
    path("practice_mixed_stimuli_2_response", views.practice_mixed_stimuli_2_response, name="practiceMixedStimuli2Response"),
    
    path("mixedActualInstructions", views.mixed_actual_instructions, name="mixedActualInstructions"),

    path("mixed_stimuli_1", views.mixed_stimuli_1, name="mixedStimuli1"),
    path("mixed_stimuli_1_response", views.mixed_stimuli_1_response, name="mixedStimuli1Response"),
    path("mixed_stimuli_2", views.mixed_stimuli_2,  name="mixedStimuli2"),
    path("mixed_stimuli_2_response", views.mixed_stimuli_2_response, name="mixedStimuli2Response"),
    path("mixed_stimuli_3", views.mixed_stimuli_3, name="mixedStimuli3"),
    path("mixed_stimuli_3_response", views.mixed_stimuli_3_response, name="mixedStimuli3Response"),
    path("mixed_stimuli_4", views.mixed_stimuli_4, name="mixedStimuli4"),
    path("mixed_stimuli_4_response", views.mixed_stimuli_4_response, name="mixedStimuli4Response"),
    path("mixed_stimuli_5", views.mixed_stimuli_5, name="mixedStimuli5"),
    path("mixed_stimuli_5_response", views.mixed_stimuli_5_response, name="mixedStimuli5Response"),
    path("mixed_stimuli_6", views.mixed_stimuli_6, name="mixedStimuli6"),
    path("mixed_stimuli_6_response", views.mixed_stimuli_6_response, name="mixedStimuli6Response"),
    path("exit", views.exit, name="exit"),

    ## doctor portal
    path("home", views.home, name="home"),
    path("doctor_about", views.doctor_about, name="doctor_about"),
    path("doctor_login", views.doctor_login, name="doctor_login"),
    path("doctor_create_account", views.doctor_create_account, name="doctor_create_account"),
    path("doctor_dashboard", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor_create_test", views.doctor_create_test, name="doctor_create_test"),
    path("doctor_test_results", views.doctor_test_results, name="doctor_test_results"),
    path("doctor_test_result/<int:test_id>", views.doctor_test_result, name="doctor_test_result"),
    path("doctor_settings", views.doctor_settings, name="doctor_settings"),
    path("doctor_support", views.doctor_support, name="doctor_support"),
    path("doctor_logout", views.doctor_logout, name="doctor_logout"),
    path("doctor_forgot_password", views.doctor_forgot_password, name="doctor_forgot_password"),
]