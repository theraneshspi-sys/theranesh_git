import random

random.seed(42)

FIRST_NAMES = ["Alex", "Jordan", "Priya", "Sam", "Maria", "Chen", "Liam",
               "Fatima", "Noah", "Aisha", "Carlos", "Yuki", "Emma", "Raj"]

COMPANIES = ["Northwind Logistics", "BluePeak Bank", "Cedarline Retail",
             "Apex Cloud Services", "Riverstone Insurance", "Meridian Health"]

LEGIT_SENDER_DOMAINS = ["company.com", "northwind-logistics.com",
                         "bluepeakbank.com", "apexcloud.io", "gmail.com",
                         "outlook.com"]

SPOOFED_DOMAINS = ["paypa1-secure.com", "amaz0n-account.com",
                    "bankofarnerica-verify.com", "appleid-confirm-support.com",
                    "micros0ft-support.com", "secure-login-update.net",
                    "192.168.0.14/login", "44.221.9.3/verify"]

URGENCY_PHRASES = [
    "Your account will be suspended within 24 hours",
    "Immediate action required to avoid service interruption",
    "We detected unusual sign-in activity on your account",
    "Your payment could not be processed",
    "Verify your identity now to keep your account active",
    "This is your final notice before account closure",
    "Unauthorized login attempt detected from a new device",
]

REWARD_PHRASES = [
    "Congratulations! You have been selected for a reward",
    "You have won a gift card, claim it before it expires",
    "Limited time offer just for you",
    "Act now to claim your free prize",
]

GENERIC_GREETINGS = ["Dear Customer", "Dear User", "Dear Valued Member",
                      "Dear Sir/Madam", "Dear Account Holder"]

PHISHING_CTA = ["Click here to verify your account",
                "Confirm your password immediately",
                "Update your billing information now",
                "Log in here to secure your account",
                "Download the attached invoice to review"]


def _fake_phishing_url(domain):
    paths = ["login", "verify", "secure", "update-account", "confirm"]
    if domain.count("/") > 0:
        return "http://" + domain
    return "http://" + domain + "/" + random.choice(paths)


def generate_phishing_email():
    domain = random.choice(SPOOFED_DOMAINS)
    url = _fake_phishing_url(domain)
    greeting = random.choice(GENERIC_GREETINGS)
    body_type = random.choice(["urgency", "reward"])
    hook = random.choice(URGENCY_PHRASES if body_type == "urgency" else REWARD_PHRASES)
    cta = random.choice(PHISHING_CTA)
    exclaims = "!" * random.choice([1, 2, 3])
    extra_url = ""
    if random.random() < 0.4:
        extra_url = " " + _fake_phishing_url(random.choice(SPOOFED_DOMAINS))

    subject_pool = [
        "URGENT: Account Verification Required",
        "Security Alert: Action Needed",
        "You have a pending notification",
        "Re: Your account access",
        "Final Reminder: Update Required",
    ]

    text = (
        f"Subject: {random.choice(subject_pool)}\n\n"
        f"{greeting},\n\n"
        f"{hook}{exclaims} {cta}: {url}{extra_url}\n\n"
        f"Failure to respond may result in permanent account suspension. "
        f"This message requires your immediate attention.\n\n"
        f"Customer Support Team"
    )
    return text


def generate_legitimate_email():
    name = random.choice(FIRST_NAMES)
    sender_name = random.choice(FIRST_NAMES)
    company = random.choice(COMPANIES)
    domain = random.choice(LEGIT_SENDER_DOMAINS)

    templates = [
        (
            "Project status update",
            f"Hi {name},\n\nJust a quick update on the project timeline. "
            f"We're on track to finish the draft by Friday. I'll share the "
            f"document at https://{domain}/docs/project-plan once it's ready.\n\n"
            f"Let me know if you have questions.\n\nBest,\n{sender_name}"
        ),
        (
            "Meeting reminder",
            f"Hi {name},\n\nReminder that our sync is scheduled for tomorrow "
            f"at 10am. Agenda and notes are linked here: "
            f"https://{domain}/calendar/event-2291\n\nSee you then,\n{sender_name}"
        ),
        (
            "Your monthly statement is ready",
            f"Hello {name},\n\nYour {company} statement for this month is "
            f"now available in your account dashboard at https://{domain}/account. "
            f"No action is required if everything looks correct.\n\n"
            f"Thank you,\n{company} Billing"
        ),
        (
            "Newsletter: This week at " + company,
            f"Hi {name},\n\nHere's what's new this week: we shipped two "
            f"features and onboarded three new clients. Read the full recap "
            f"at https://{domain}/blog/weekly-recap.\n\nThanks for reading,\n"
            f"{company} Team"
        ),
        (
            "Re: Lunch on Thursday?",
            f"Hey {name},\n\nAre you free for lunch on Thursday around noon? "
            f"There's a new place near the office I want to try.\n\nLet me know,\n{sender_name}"
        ),
        (
            "Invoice attached for your records",
            f"Hi {name},\n\nAttached is invoice #{random.randint(1000,9999)} for "
            f"last month's services. Let us know if you have any questions about "
            f"the line items.\n\nRegards,\n{company} Accounts"
        ),
    ]
    subject, body = random.choice(templates)
    return f"Subject: {subject}\n\n{body}"


def build_dataset(n_per_class=400):
    texts, labels = [], []
    for _ in range(n_per_class):
        texts.append(generate_phishing_email())
        labels.append(1)
        texts.append(generate_legitimate_email())
        labels.append(0)
    return texts, labels
