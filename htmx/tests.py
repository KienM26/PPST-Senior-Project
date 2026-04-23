"""
Unit tests for PPST helper functions — htmx app
Place this file at: htmx/tests.py
Run with: python manage.py test htmx
"""

from django.test import TestCase, Client, RequestFactory

from htmx.views import (
    ACCESSIBILITY_THEMES,
    calculate_independent_age_group,
    generate_digit_stimulus,
    generate_mixed_stimulus,
    get_current_lang,
    get_current_theme,
)

class GenerateDigitStimulusTests(TestCase):

    def setUp(self):
        import htmx.views as v
        v.USED_STIMULI.clear()

    def test_sequence_is_5_characters(self):
        result = generate_digit_stimulus()
        self.assertEqual(len(result["sequence"]), 5)

    def test_sequence_contains_only_digits(self):
        result = generate_digit_stimulus()
        self.assertTrue(result["sequence"].isdigit())

    def test_correct_answer_is_ascending(self):
        result = generate_digit_stimulus()
        self.assertEqual(result["correct_answer"], "".join(sorted(result["sequence"])))

    def test_key_starts_with_digit(self):
        result = generate_digit_stimulus()
        self.assertTrue(result["key"].startswith("digit_"))

    def test_no_duplicate_sequences(self):
        results = [generate_digit_stimulus() for _ in range(5)]
        sequences = [r["sequence"] for r in results]
        self.assertEqual(len(sequences), len(set(sequences)))

class GenerateMixedStimulusTests(TestCase):

    def setUp(self):
        import htmx.views as v
        v.USED_STIMULI.clear()

    def test_sequence_has_3_digits_and_2_letters(self):
        result = generate_mixed_stimulus()
        seq = result["sequence"]
        self.assertEqual(len([c for c in seq if c.isdigit()]), 3)
        self.assertEqual(len([c for c in seq if c.isalpha()]), 2)

    def test_correct_answer_digits_first_then_letters(self):
        result = generate_mixed_stimulus()
        seq = result["sequence"]
        expected = "".join(sorted(c for c in seq if c.isdigit())) + \
                   "".join(sorted(c for c in seq if c.isalpha()))
        self.assertEqual(result["correct_answer"], expected)

    def test_letters_are_uppercase(self):
        result = generate_mixed_stimulus()
        letters = [c for c in result["sequence"] if c.isalpha()]
        self.assertTrue(all(c.isupper() for c in letters))

    def test_key_starts_with_mixed(self):
        result = generate_mixed_stimulus()
        self.assertTrue(result["key"].startswith("mixed_"))

    def test_no_duplicate_sequences(self):
        results = [generate_mixed_stimulus() for _ in range(5)]
        sequences = [r["sequence"] for r in results]
        self.assertEqual(len(sequences), len(set(sequences)))

class CalculateIndependentAgeGroupTests(TestCase):

    def test_90_percent_returns_20_29(self):
        group, accuracy = calculate_independent_age_group(9, 10)
        self.assertEqual(group, "20-29")
        self.assertAlmostEqual(accuracy, 90.0)

    def test_80_percent_returns_30_39(self):
        group, _ = calculate_independent_age_group(8, 10)
        self.assertEqual(group, "30-39")

    def test_70_percent_returns_40_49(self):
        group, _ = calculate_independent_age_group(7, 10)
        self.assertEqual(group, "40-49")

    def test_60_percent_returns_50_59(self):
        group, _ = calculate_independent_age_group(6, 10)
        self.assertEqual(group, "50-59")

    def test_below_60_percent_returns_60_plus(self):
        group, _ = calculate_independent_age_group(5, 10)
        self.assertEqual(group, "60+")

    def test_zero_total_returns_60_plus_and_zero_accuracy(self):
        group, accuracy = calculate_independent_age_group(0, 0)
        self.assertEqual(group, "60+")
        self.assertEqual(accuracy, 0)

    def test_100_percent_returns_20_29(self):
        group, accuracy = calculate_independent_age_group(12, 12)
        self.assertEqual(group, "20-29")
        self.assertAlmostEqual(accuracy, 100.0)

class SessionHelperTests(TestCase):

    def _request_with_session(self, session_data=None):
        client = Client()
        session = client.session
        if session_data:
            session.update(session_data)
            session.save()
        request = RequestFactory().get("/")
        request.session = session
        return request

    def test_lang_defaults_to_en(self):
        request = self._request_with_session()
        self.assertEqual(get_current_lang(request), "en")

    def test_lang_reads_from_session(self):
        request = self._request_with_session({"lang": "es"})
        self.assertEqual(get_current_lang(request), "es")

    def test_lang_falls_back_on_unknown_code(self):
        request = self._request_with_session({"lang": "fr"})
        self.assertEqual(get_current_lang(request), "en")

    def test_theme_defaults_to_teal(self):
        request = self._request_with_session()
        self.assertEqual(get_current_theme(request), ACCESSIBILITY_THEMES["teal"])

    def test_theme_reads_from_session(self):
        request = self._request_with_session({"theme": "navy"})
        self.assertEqual(get_current_theme(request), ACCESSIBILITY_THEMES["navy"])

    def test_theme_falls_back_on_unknown_key(self):
        request = self._request_with_session({"theme": "magenta"})
        self.assertEqual(get_current_theme(request), ACCESSIBILITY_THEMES["teal"])