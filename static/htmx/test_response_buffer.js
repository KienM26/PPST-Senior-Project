(function () {
    const STORAGE_KEY = "ppstTestResponses";
    let currentAnswer = [];
    let currentClicks = [];
    let currentStartedAt = null;

    function readResponses() {
        try {
            return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
        } catch (error) {
            return [];
        }
    }

    function writeResponses(responses) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(responses));
    }

    function updateHiddenInput(inputId) {
        const input = document.getElementById(inputId);
        if (input) {
            input.value = currentAnswer.join("");
        }
    }

    window.ppstTestBuffer = {
        clear() {
            sessionStorage.removeItem(STORAGE_KEY);
            currentAnswer = [];
            currentClicks = [];
            currentStartedAt = null;
        },

        startCapture(inputId = "response") {
            currentAnswer = [];
            currentClicks = [];
            currentStartedAt = Date.now();
            updateHiddenInput(inputId);
        },

        press(value, inputId = "response") {
            const normalizedValue = String(value);
            currentAnswer.push(normalizedValue);
            currentClicks.push({
                value: normalizedValue,
                timestamp: Date.now(),
            });
            updateHiddenInput(inputId);
        },

        saveCurrentResponse(stimulusKey, stimulusType) {
            const responses = readResponses().filter((item) => item.stimulus_key !== stimulusKey);
            responses.push({
                stimulus_key: stimulusKey,
                stimulus_type: stimulusType,
                response_string: currentAnswer.join(""),
                started_at: currentStartedAt,
                submitted_at: Date.now(),
                clicks: currentClicks,
            });
            writeResponses(responses);
        },

        async submitAll(url, csrfToken) {
            const responses = readResponses();
            if (!responses.length) {
                return { ok: true, skipped: true };
            }

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ responses }),
            });

            if (!response.ok) {
                throw new Error("Failed to submit test responses.");
            }

            this.clear();
            return response.json();
        },
    };
})();
