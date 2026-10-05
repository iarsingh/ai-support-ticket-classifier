# ai-support-ticket-classifier — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

The same ticket labels as the ML classifier, kept as a separate NLP-facing service.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/aiticket/__init__.py"]
    M1["src/aiticket/classify.py"]
    M2["src/aiticket/main.py"]
    M2 -->|imports| M1
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/aiticket/main.py`](src/aiticket/main.py) | HTTP handlers: `GET /healthz`, `POST /classify` |
| [`src/aiticket/classify.py`](src/aiticket/classify.py) | Functions: `classify` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/aiticket/__init__.py`](src/aiticket/__init__.py) | Implementation or supporting configuration |
| [`tests/test_classify.py`](tests/test_classify.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/aiticket/main.py`](src/aiticket/main.py#L8) |
| `POST /classify` | `post_classify` | [`src/aiticket/main.py`](src/aiticket/main.py#L13) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `classify(text)`

Source: [`src/aiticket/classify.py`](src/aiticket/classify.py#L12).

Calls visible in this function: `InputError`, `all`, `counts.values`, `isinstance`, `len`, `max`, `re.findall`, `sum`, `text.lower`, `text.strip`.

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

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `InputError('Text is empty.')` | [`src/aiticket/classify.py`](src/aiticket/classify.py#L14) |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/aiticket/main.py`](src/aiticket/main.py#L17) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/aiticket/classify.py`](src/aiticket/classify.py) defines module-level containers: `BILLING`, `ACCESS`, `OUTAGE`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `classify`

In [`src/aiticket/classify.py`](src/aiticket/classify.py#L12), `classify(text)` receives the inputs. The function computes these intermediate values:

- `tokens = re.findall('[a-z0-9]+', text.lower())`
- `counts = {}`
- `counts['billing'] = sum((token in BILLING for token in tokens))`
- `counts['access'] = sum((token in ACCESS for token in tokens))`
- `counts['outage'] = sum((token in OUTAGE for token in tokens))`
- `label = max(counts, key=lambda name: (counts[name], name))`

Its result is defined by:

- `{'label': label, 'counts': counts, 'tokens': len(tokens)}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/aiticket/classify.py`](src/aiticket/classify.py#L12) branches on:

- `not isinstance(text, str) or not text.strip()`
- `all((value == 0 for value in counts.values()))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_classify.py`](tests/test_classify.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
