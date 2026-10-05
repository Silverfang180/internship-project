TARGETS_MINUTES = {
    'chat': 15,
    'voice': 120,
    'social': 240,
    'email': 480
}

CREDIT_PER_BREACH_INR = 350

SHIFTS = [
    ('Morning', 6, 14),
    ('Day', 14, 22),
    ('Night', 22, 6) # Night spans across midnight (22 to 6)
]

NIGHT_FINDING_MIN_BREACH_PCT = 0.50
NIGHT_FINDING_RATE_MULTIPLIER = 2.0
