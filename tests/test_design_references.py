"""Design Reference Library — matcher, pack integrity, contract injection, CLI.

The library ships design-reference profiles (palette/type/mood/vertical) distilled
from real sites; NX matches the prompt to one by deterministic tag overlap and
injects it into the designer/frontend Engineering Contract.
"""
import argparse
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import nx_packs
from nx_providers.knowledge import design_refs as R
from nx_cli import orchestrator
from nx_knowledge.knowledge.contract import ContractBuilder
from nx_knowledge.knowledge.registry import default_registry

SEED_IDS = {"hs-motors", "espaco-ellen-souza", "luque-construcoes",
            "atelie-simone", "odara-li", "pousada-luz-do-sol"}


def catalog_refs():
    """The built-in seed references, straight from the pack catalog."""
    return R.load_references(nx_packs.pack_dir("design-references") / "references")


class _Home:
    """Temp AIES_HOME with the given packs installed."""
    def __init__(self, packs):
        self.packs = packs

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / ".ai-project-assistant"
        (root / "packs").mkdir(parents=True)
        for p in self.packs:
            nx_packs.install(p, root / "packs")
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(root)
        return root

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


class TestPackIntegrity(unittest.TestCase):
    def test_pack_is_catalogued_and_well_formed(self):
        self.assertIn("design-references", nx_packs.names())
        d = nx_packs.pack_dir("design-references")
        for req in nx_packs.REQUIRED:
            self.assertTrue((d / req).is_file(), f"missing {req}")
        self.assertTrue((d / "matcher.md").is_file())
        m = nx_packs.manifest("design-references")
        self.assertEqual(m["category"], "design")
        # designer + frontend + responsive + mobile (tokens are platform-agnostic)
        self.assertEqual(sorted(m["applies_to"]),
                         ["designer", "frontend", "mobile", "responsive"])

    def test_every_seed_reference_conforms_to_schema(self):
        refs = catalog_refs()
        ids = {e["id"] for e in refs}
        self.assertTrue(SEED_IDS <= ids, f"missing seeds: {SEED_IDS - ids}")
        for e in refs:
            for f in R.REQUIRED_FIELDS:
                self.assertIn(f, e, f"{e.get('id')} missing '{f}'")
            for theme in ("light", "dark"):
                t = e["palette"][theme]
                for role in ("bg", "surface", "primary", "accent", "fg", "muted"):
                    self.assertIn(role, t, f"{e['id']} palette.{theme} missing {role}")
            for slot in ("display", "body"):
                self.assertIn("family", e["typography"][slot])

    def test_seed_files_are_valid_json(self):
        d = nx_packs.pack_dir("design-references") / "references"
        for p in d.glob("*.json"):
            json.loads(p.read_text(encoding="utf-8"))  # raises on malformed


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.refs = catalog_refs()

    def test_prompt_selects_expected_reference(self):
        cases = {
            "quero um site para uma loja de carros seminovos": "hs-motors",
            "salão de beleza elegante e feminino": "espaco-ellen-souza",
            "salão de beleza de luxo sofisticado": "odara-li",
            "empresa de obras e reformas / construtora": "luque-construcoes",
            "papelaria personalizada para festas e convites": "atelie-simone",
            "pousada à beira-mar em Aracati": "pousada-luz-do-sol",
        }
        for prompt, expected in cases.items():
            top = R.match(prompt, self.refs, k=1)
            self.assertTrue(top, f"no match for {prompt!r}")
            self.assertEqual(top[0][0]["id"], expected, f"{prompt!r} → {top[0][0]['id']}")

    def test_mood_disambiguates_same_vertical(self):
        # both are beauty-salon; mood terms must break the tie the right way
        elegant = R.match("salão de beleza elegante", self.refs, k=2)
        luxury = R.match("salão de beleza de luxo", self.refs, k=2)
        self.assertEqual(elegant[0][0]["id"], "espaco-ellen-souza")
        self.assertEqual(luxury[0][0]["id"], "odara-li")

    def test_accents_are_normalized(self):
        with_accents = R.match("construção e reformas", self.refs, k=1)
        without = R.match("construcao e reformas", self.refs, k=1)
        self.assertEqual(with_accents[0][0]["id"], "luque-construcoes")
        self.assertEqual(without[0][0]["id"], "luque-construcoes")

    def test_unrelated_prompt_matches_nothing(self):
        self.assertEqual(R.match("a vegan recipe blog about quantum physics", self.refs), [])

    def test_ranking_is_deterministic(self):
        a = [e["id"] for e, _ in R.match("salão de beleza", self.refs, k=6)]
        b = [e["id"] for e, _ in R.match("salão de beleza", self.refs, k=6)]
        self.assertEqual(a, b)

    def test_expanded_library_covers_new_verticals(self):
        # the second extraction batch (2.7.0) added these ids + verticals
        ids = {e["id"] for e in self.refs}
        for new in ("sweetags", "myfots", "petala-beauty", "vicshop",
                    "fwr-agencia", "liloca", "tapetes-sao-jose", "lp-max-suzuki"):
            self.assertIn(new, ids, f"missing new reference {new}")
        cases = {
            "site para uma agência de design de ecommerce": "sweetags",
            "loja de cosméticos e maquiagem feminina": "petala-beauty",
            "agência digital de seo e conversão": "fwr-agencia",
            "tapetes sob medida para decoração da casa": "tapetes-sao-jose",
        }
        for prompt, expected in cases.items():
            top = R.match(prompt, self.refs, k=1)
            self.assertTrue(top, f"no match for {prompt!r}")
            self.assertEqual(top[0][0]["id"], expected, f"{prompt!r} → {top[0][0]['id']}")


class TestContractInjection(unittest.TestCase):
    def test_designer_contract_gets_matched_reference(self):
        with _Home(["design", "design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("Landing page para salão de beleza de luxo", "designer")
            self.assertIn("design-references", c.packs())
            self.assertIsNotNone(c.design_reference)
            self.assertEqual(c.design_reference["id"], "odara-li")
            self.assertIn("design_reference:", c.to_text())
            self.assertIn("odara-li", c.to_text())
            self.assertEqual(c.as_dict()["design_reference"]["id"], "odara-li")

    def test_frontend_agent_also_receives_reference(self):
        with _Home(["design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("Construir a home de uma pousada à beira-mar", "frontend")
            self.assertIsNotNone(c.design_reference)
            self.assertEqual(c.design_reference["id"], "pousada-luz-do-sol")

    def test_non_design_agent_never_gets_reference(self):
        with _Home(["design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("site para salão de beleza", "backend")
            self.assertIsNone(c.design_reference)

    def test_no_matching_reference_leaves_it_none(self):
        with _Home(["design-references"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("Implement a Kafka consumer for quantum telemetry", "designer")
            self.assertIsNone(c.design_reference)

    def test_pack_absent_means_no_reference(self):
        with _Home(["design"]):
            cb = ContractBuilder(config={}, registry=default_registry())
            c = cb.build("site para salão de beleza de luxo", "designer")
            self.assertIsNone(c.design_reference)


class TestDesignCLI(unittest.TestCase):
    def setUp(self):
        self.parser = orchestrator.build_parser()

    def test_parser_routes_design_ref(self):
        args = self.parser.parse_args(["design", "ref", "match", "salão de beleza", "--top", "2"])
        self.assertEqual(args.fn.__name__, "cmd_design")
        self.assertEqual(args.ref_action, "match")
        self.assertEqual(args.query, "salão de beleza")
        self.assertEqual(args.top, 2)

    def _run(self, argv):
        args = self.parser.parse_args(argv)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.fn(args)
        return rc, buf.getvalue()

    def test_list_show_match_smoke(self):
        with _Home([]):  # falls back to the built-in catalog
            rc, out = self._run(["design", "ref", "list"])
            self.assertEqual(rc, 0)
            self.assertIn("odara-li", out)
            rc, out = self._run(["design", "ref", "show", "hs-motors"])
            self.assertEqual(rc, 0)
            self.assertIn("Clash Display", out)
            rc, out = self._run(["design", "ref", "match", "obras e reformas"])
            self.assertEqual(rc, 0)
            self.assertIn("luque-construcoes", out)

    def test_show_unknown_id_errors(self):
        with _Home([]):
            args = self.parser.parse_args(["design", "ref", "show", "nope"])
            self.assertEqual(args.fn(args), 2)


if __name__ == "__main__":
    unittest.main()
