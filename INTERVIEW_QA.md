# ai-support-ticket-classifier — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ai-support-ticket-classifier address, and what can you demonstrate?

The same ticket labels as the ML classifier, kept as a separate NLP-facing service.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/aiticket/main.py`](src/aiticket/main.py): Implementation or supporting configuration.
- [`src/aiticket/classify.py`](src/aiticket/classify.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/aiticket/__init__.py`](src/aiticket/__init__.py): Implementation or supporting configuration.
- [`tests/test_classify.py`](tests/test_classify.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `classify` and explain the decision it makes?

The main walkthrough here is `classify(text)` in [`src/aiticket/classify.py`](src/aiticket/classify.py#L12).

```python
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
```

The implementation calls `InputError`, `all`, `counts.values`, `isinstance`, `len`, `max`, `re.findall`, `sum`, `text.lower`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `InputError('Text is empty.')` in [`src/aiticket/classify.py`](src/aiticket/classify.py#L14).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/aiticket/main.py`](src/aiticket/main.py#L17).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_classify.py`](tests/test_classify.py#L7) contains `test_labels`:

```python
def test_labels():
    assert client.post("/classify", json={"text": 'invoice charge is wrong'}).json()["label"] == "billing"
    assert client.post("/classify", json={"text": 'cluster is down'}).json()["label"] == "outage"
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/aiticket/main.py`](src/aiticket/main.py#L8).
- `POST /classify` → `post_classify` in [`src/aiticket/main.py`](src/aiticket/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `BILLING`, `ACCESS`, `OUTAGE` in [`src/aiticket/classify.py`](src/aiticket/classify.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `classify`?

In [`src/aiticket/classify.py`](src/aiticket/classify.py#L12), `classify(text)` receives the inputs. The function computes these intermediate values:

- `tokens = re.findall('[a-z0-9]+', text.lower())`
- `counts = {}`
- `counts['billing'] = sum((token in BILLING for token in tokens))`
- `counts['access'] = sum((token in ACCESS for token in tokens))`
- `counts['outage'] = sum((token in OUTAGE for token in tokens))`
- `label = max(counts, key=lambda name: (counts[name], name))`

Its result is defined by:

- `{'label': label, 'counts': counts, 'tokens': len(tokens)}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/aiticket/classify.py`](src/aiticket/classify.py#L12) branches on:

- `not isinstance(text, str) or not text.strip()`
- `all((value == 0 for value in counts.values()))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
