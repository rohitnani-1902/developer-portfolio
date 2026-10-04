"""Explicit real-provider smoke check using only authored fictional fixtures."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas_backend.core import run

fixtures = [
    {'mode': 'research', 'question': 'Compare the launch dates and explain the disagreement.', 'documents': [{'name': 'product.md', 'text': 'Product proposes launch on 15 November to 200 teams.'}, {'name': 'engineering.md', 'text': 'Engineering recommends launch on 22 November to 50 teams because load testing is incomplete.'}]},
    {'mode': 'code', 'question': 'Review this code and suggest a safer implementation. Do not execute code.', 'documents': [{'name': 'calculate.py', 'text': 'def calculate(user_expression):\n    return eval(user_expression)\n'}]},
    {'mode': 'ops', 'question': 'Draft a response following the refund policy.', 'documents': [{'name': 'request.txt', 'text': 'My invoice was charged twice. Please refund the extra payment.'}, {'name': 'policy.md', 'text': 'Verify invoice and payment references before approving a refund. Do not promise a refund or resolution date before verification.'}]}
]
results = []
for fixture in fixtures:
    try:
        result = run({**fixture, 'ai': True})
        print(f"{fixture['mode']}: engine={result['engine']}, claims={len(result['claims'])}, citations validated, {result['trace']['milliseconds']} ms", flush=True)
        results.append(result)
    except Exception as error:
        print(f"{fixture['mode']}: {type(error).__name__}: {error}", flush=True)
        cause = error.__cause__
        if cause is not None:
            print('Provider diagnostic:', type(cause).__name__, getattr(cause, 'code', ''), flush=True)
            if hasattr(cause, 'read'):
                try:
                    provider_error = json.loads(cause.read()).get('error', {})
                    print('Provider error type/code:', provider_error.get('type'), provider_error.get('code'), flush=True)
                except Exception:
                    pass
        raise SystemExit(1)
Path(__file__).with_name('smoke-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
