import copy
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas_backend.core import InputError, documents, generate, passages, retrieve, run, triage

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.docs = [{'name': 'engineering.md', 'text': 'Search latency target is 300 ms. Launch on 22 November after load testing.'},
                     {'name': 'support.md', 'text': 'Customer support coverage on weekends is unresolved. Pilot teams require citations.'}]

    def test_retrieval_and_abstention(self):
        chunks = passages(documents(self.docs))
        self.assertEqual(retrieve('latency', chunks)[0]['source'], 'engineering.md')
        self.assertEqual(retrieve('weekends support', chunks)[0]['source'], 'support.md')
        for q in ('zzzzunmatched', 'the and of'):
            self.assertEqual(retrieve(q, chunks), [])
        self.assertEqual(retrieve('café', passages(documents([{'name': 'cafe', 'text': 'CAFÉ menu'}])))[0]['source'], 'cafe')

    def test_duplicate_names_have_distinct_provenance(self):
        docs = documents([{'name': 'same', 'text': 'first evidence'}, {'name': 'same', 'text': 'second evidence'}])
        self.assertNotEqual(passages(docs)[0]['id'], passages(docs)[1]['id'])

    def test_source_coverage_preserves_missing_and_duplicate_sources(self):
        result = run({'mode': 'research', 'question': 'launch', 'documents': [
            {'name': 'same.md', 'text': 'Launch on 15 November with 200 teams.'},
            {'name': 'same.md', 'text': 'Launch on 22 November with 50 teams.'},
            {'name': 'interviews.md', 'text': 'People requested exportable briefs.'}]})
        rows = result['source_coverage']
        self.assertEqual([r['document_id'] for r in rows], ['1', '2', '3'])
        self.assertEqual([r['status'] for r in rows], ['Selected evidence', 'Selected evidence', 'No lexical match'])
        self.assertIn('15 November', rows[0]['excerpt'])
        self.assertIn('22 November', rows[1]['excerpt'])
        self.assertNotEqual(rows[0]['citations'], rows[1]['citations'])
        self.assertEqual(rows[2]['excerpt'], '')

    def test_source_coverage_distinguishes_retrieval_limit_from_no_match(self):
        docs = [{'name': str(i), 'text': 'Launch proposal.'} for i in range(7)]
        result = run({'mode': 'research', 'question': 'launch', 'documents': docs})
        self.assertEqual(len(result['evidence']), 6)
        self.assertEqual(result['source_coverage'][-1]['status'], 'Outside retrieval limit')
        self.assertEqual(result['source_coverage'][-1]['matched_terms'], ['launch'])

    def test_source_coverage_with_no_evidence_abstains(self):
        result = run({'mode': 'research', 'question': 'unmatchedzz', 'documents': self.docs})
        self.assertEqual(result['claims'], [])
        self.assertTrue(all(r['status'] == 'No lexical match' for r in result['source_coverage']))
        self.assertEqual(run({'mode': 'ops', 'question': 'draft', 'documents': self.docs})['source_coverage'], [])

    def test_chunk_tail_and_limits(self):
        chunks = passages(documents([{'name': 'long', 'text': 'a' * 4000 + ' final-tail'}]))
        self.assertIn('final-tail', chunks[-1]['text'])
        with self.assertRaises(InputError):
            documents([{'name': 'too-long', 'text': 'x' * 50001}])
        with self.assertRaises(InputError):
            documents([{'name': 'source', 'text': 'x'}] * 13)
        with self.assertRaises(InputError):
            passages(documents([{'name': str(i), 'text': '\n'.join('x' for _ in range(1000))} for i in range(4)]))

    def test_invalid_input(self):
        for payload in (None, {}, {'mode': 'other'}, {'mode': 'research', 'question': '', 'documents': []}, {'mode': 'code', 'question': 'review', 'documents': [{'name': 'a', 'text': ''}]}):
            with self.assertRaises(InputError):
                run(payload)

    def test_no_evidence_does_not_call_model(self):
        def forbidden(_):
            self.fail('Model must not run without evidence')
        result = run({'mode': 'research', 'question': 'zzzzz', 'documents': self.docs, 'ai': True}, call=forbidden)
        self.assertEqual(result['claims'], [])
        self.assertEqual(result['engine'], 'local')

    def test_code_analysis_is_static(self):
        text = 'import subprocess\nvalue = eval(user_input)\nsubprocess.run(user_command, shell=True)\n'
        result = run({'mode': 'code', 'question': 'review', 'documents': [{'name': 'unsafe.py', 'text': text}]})
        self.assertEqual(len(result['findings']), 2)
        self.assertEqual(result['findings'][0]['line'], 2)
        bad = run({'mode': 'code', 'question': 'review', 'documents': [{'name': 'broken.py', 'text': 'def broken('}]})
        self.assertEqual(bad['findings'][0]['title'], 'Python syntax error')

    def test_ops_review_boundary(self):
        result = run({'mode': 'ops', 'question': 'draft', 'documents': [{'name': 'request', 'text': 'Urgent duplicate invoice payment; refund requested.'}]})
        self.assertEqual(result['triage']['category'], 'Billing')
        self.assertEqual(result['triage']['priority'], 'High')
        self.assertEqual(result['triage']['status'], 'Needs review')
        self.assertTrue(result['draft'])
        self.assertNotIn('sent', result)

    def test_structured_generation_and_prompt_boundary(self):
        evidence = passages(documents(self.docs))
        expected = {'summary': 'Summary', 'claims': [{'text': 'Latency target is 300 ms.', 'citations': [evidence[0]['id']]}], 'next_steps': ['Review'], 'draft': ''}
        def fake(payload):
            self.assertIn('untrusted data', payload['messages'][0]['content'])
            self.assertEqual(payload['response_format']['json_schema']['strict'], True)
            return copy.deepcopy(expected)
        self.assertEqual(generate('research', 'latency', evidence, [], fake), expected)
        invalid = copy.deepcopy(expected)
        invalid['claims'][0]['citations'] = ['invented-source']
        with self.assertRaises(RuntimeError):
            generate('research', 'latency', evidence, [], lambda _: invalid)
        invalid['claims'][0]['citations'] = []
        with self.assertRaises(RuntimeError):
            generate('research', 'latency', evidence, [], lambda _: invalid)
        with self.assertRaises(RuntimeError):
            generate('research', 'latency', evidence, [], lambda _: {'summary': 'malformed'})

    def test_unconfigured_model_reports_failure(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(InputError):
                run({'mode': 'research', 'question': 'latency', 'documents': self.docs, 'ai': True})

    def test_trace_and_input_immutable(self):
        payload = {'mode': 'research', 'question': 'latency', 'documents': self.docs}
        before = json.dumps(payload)
        result = run(payload)
        self.assertEqual(json.dumps(payload), before)
        self.assertEqual(result['trace']['sources'], 2)
        self.assertEqual(result['trace']['retrieved'], 1)
        self.assertEqual(len(result['trace']['input_hash']), 12)

if __name__ == '__main__':
    unittest.main()
