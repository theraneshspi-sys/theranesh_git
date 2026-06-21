import re
import numpy as np

URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
IP_URL_RE = re.compile(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

URGENCY_WORDS = [
    "urgent", "immediately", "verify", "suspend", "suspended", "confirm",
    "act now", "limited time", "final notice", "unauthorized",
    "unusual activity", "click here", "update your", "password",
    "security alert", "expire", "restricted",
]

REWARD_WORDS = [
    "congratulations", "winner", "won", "free", "prize", "gift card",
    "claim your", "selected",
]

GENERIC_GREETING_RE = re.compile(
    r"dear (customer|user|valued member|sir/madam|account holder)",
    re.IGNORECASE,
)

KNOWN_BRANDS = ["paypal", "amazon", "apple", "microsoft", "bank of america",
                "google", "netflix"]


def _domain_from_url(url):
    match = re.search(r"https?://([^/]+)", url)
    return match.group(1).lower() if match else ""


def _looks_like_typosquat(domain):
    cleaned = domain.replace("0", "o").replace("1", "l").replace("-", "")
    for brand in KNOWN_BRANDS:
        brand_clean = brand.replace(" ", "")
        if brand_clean in cleaned and cleaned != brand_clean + ".com":
            return True
    return False


def extract_features(text):
    urls = URL_RE.findall(text)
    domains = [_domain_from_url(u) for u in urls]

    lower = text.lower()
    letters = [c for c in text if c.isalpha()]
    capital_ratio = (
        sum(1 for c in letters if c.isupper()) / len(letters) if letters else 0.0
    )

    features = {
        "num_urls": len(urls),
        "has_ip_url": int(bool(IP_URL_RE.search(text))),
        "has_typosquat_domain": int(any(_looks_like_typosquat(d) for d in domains)),
        "num_exclamations": text.count("!"),
        "has_generic_greeting": int(bool(GENERIC_GREETING_RE.search(text))),
        "urgency_word_count": sum(lower.count(w) for w in URGENCY_WORDS),
        "reward_word_count": sum(lower.count(w) for w in REWARD_WORDS),
        "capital_ratio": capital_ratio,
        "text_length": len(text),
    }
    return features


FEATURE_NAMES = [
    "num_urls", "has_ip_url", "has_typosquat_domain", "num_exclamations",
    "has_generic_greeting", "urgency_word_count", "reward_word_count",
    "capital_ratio", "text_length",
]


def extract_feature_matrix(texts):
    rows = []
    for t in texts:
        f = extract_features(t)
        rows.append([f[name] for name in FEATURE_NAMES])
    return np.array(rows, dtype=float)
