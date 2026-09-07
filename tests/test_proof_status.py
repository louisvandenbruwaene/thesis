"""Regression checks for missing, commented and incorrectly associated proofs."""

from pathlib import Path
import re
import unittest

from check_proof_status import check_proof_status, strip_comments

ROOT = Path(__file__).resolve().parents[1]
APP = 'chapters/app_proofs.tex'
CH1 = 'chapters/ch1_basecases.tex'
STATEMENT = r'\begin{conjecture}[Example, with proof,\conditional]\label{test:a}Claim.\end{conjecture}'
PROOF = r'\begin{proof}[Conditional proof]An argument.\end{proof}'


class ProofStatus(unittest.TestCase):
    def check(self, text):
        return check_proof_status({APP: text})

    def test_inline_and_named_proofs_are_accepted(self):
        self.assertEqual(self.check(STATEMENT + PROOF), [])
        named = PROOF.replace('[Conditional proof]', r'[Conditional proof of \Cref{test:a}]')
        self.assertEqual(check_proof_status({CH1: STATEMENT, APP: named}), [])

    def test_another_statements_named_proof_cannot_be_borrowed(self):
        wrong = PROOF.replace('[Conditional proof]', r'[Conditional proof of \Cref{test:b}]')
        self.assertIn('CONJECTURE WITHOUT PROOF: test:a', self.check(STATEMENT + wrong))

    def test_commented_proof_does_not_count(self):
        for text in [STATEMENT + '\n%' + PROOF, STATEMENT + '% hidden\n%' + PROOF]:
            self.assertIn('CONJECTURE WITHOUT PROOF: test:a', self.check(text))

    def test_empty_or_unclosed_proofs_are_rejected(self):
        for proof in [PROOF.replace('An argument.', ''), PROOF.replace(r'\end{proof}', '')]:
            self.assertIn('CONJECTURE WITHOUT PROOF: test:a', self.check(STATEMENT + proof))

    def test_proof_status_still_has_to_match(self):
        self.assertTrue(any('PROOF STATUS DESYNC' in e for e in
                            self.check(STATEMENT + PROOF.replace('Conditional', 'Proposed'))))

    def test_escaped_percent_is_not_a_comment(self):
        self.assertEqual(strip_comments(r'50\% remains % removed'), r'50\% remains ')
        self.assertEqual(strip_comments(r'break\\% removed'), r'break\\')

    def test_live_sources_pass(self):
        sources = {f: (ROOT / f).read_text() for f in [CH1, APP]}
        self.assertEqual(check_proof_status(sources), [])

    def test_removing_each_live_conjecture_proof_is_detected(self):
        sources = {f: (ROOT / f).read_text() for f in [CH1, APP]}
        app = sources[APP]
        proofs = list(re.finditer(r'\\begin\{proof\}(?:\[([^\n]*?)\])?(.*?)\\end\{proof\}', app, re.S))
        count = 0
        for filename, source in sources.items():
            for statement in re.finditer(r'\\begin\{conjecture\}\[([^\n]*)\]\\label\{([^}]+)\}(.*?)\\end\{conjecture\}', source, re.S):
                if 'with proof' not in statement.group(1):
                    continue
                label = statement.group(2)
                named = [p for p in proofs if r'\Cref{' + label + '}' in (p.group(1) or '')]
                if named:
                    proof = named[0]
                else:
                    self.assertEqual(filename, APP, label)
                    proof = next(p for p in proofs if p.start() > statement.end())
                count += 1
                with self.subTest(label=label):
                    changed = dict(sources)
                    changed[APP] = app[:proof.start()] + app[proof.end():]
                    self.assertIn('CONJECTURE WITHOUT PROOF: ' + label,
                                  check_proof_status(changed))
        self.assertGreater(count, 0)
