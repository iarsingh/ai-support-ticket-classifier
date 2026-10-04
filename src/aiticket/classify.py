import re

BILLING = {"invoice", "charge"}
ACCESS = {"login", "sso"}
OUTAGE = {"down", "timeout"}


class InputError(ValueError):
    pass


def classify(text):
    if not isinstance(text, str) or not text.strip():
        raise InputError("Text is empty.")
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    counts = {}
    counts['billing'] = sum(token in BILLING for token in tokens)
    counts['access'] = sum(token in ACCESS for token in tokens)
    counts['outage'] = sum(token in OUTAGE for token in tokens)
    label = max(counts, key=lambda name: (counts[name], name))
    if all(value == 0 for value in counts.values()):
        label = "unknown"
    return {"label": label, "counts": counts, "tokens": len(tokens)}
