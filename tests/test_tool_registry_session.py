"""Contratto P2 (ToDo 2026-10-28): registry tool session-scoped append-only.

Le dichiarazioni caricate vanno trasportate invariate nelle richieste successive
(carry-forward): il registry per sessione e' derivato da session_id e non
ricomposto per-request. Tra turni consecutivi il set resta stabile e cresce
solo per append; nessuna rimozione o riordino puo' destabilizzare il prefix.
"""

from __future__ import annotations

import unittest

from gateway_core import ToolSessionRegistry, derive_session_id


class TestToolSessionRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolSessionRegistry()
        self.session = derive_session_id("key", "/proj", "chat_1")

    def test_stesso_set_tra_turni_consecutivi(self) -> None:
        self.registry.register(self.session, [{"name": "fetch"}, {"name": "search"}])
        first = self.registry.get(self.session)
        # turno successivo: il client ripresenta le stesse dichiarazioni
        self.registry.register(self.session, [{"name": "fetch"}, {"name": "search"}])
        self.assertEqual(first, self.registry.get(self.session))

    def test_append_only_con_nuova_dichiarazione(self) -> None:
        self.registry.register(self.session, [{"name": "fetch"}])
        base = self.registry.get(self.session)
        self.registry.register(self.session, [{"name": "skill_extra"}])
        after = self.registry.get(self.session)
        self.assertEqual(after[: len(base)], base)
        self.assertEqual(len(after), len(base) + 1)

    def test_nessuna_rimozione_ne_riordino(self) -> None:
        self.registry.register(self.session, [{"name": "beta"}, {"name": "alpha"}])
        first = self.registry.get(self.session)
        # ripresentazione in ordine diverso: identita' gia' nota, nessuna variazione
        self.registry.register(self.session, [{"name": "alpha"}, {"name": "beta"}])
        self.assertEqual(first, self.registry.get(self.session))

    def test_sessioni_isolate(self) -> None:
        other = derive_session_id("key", "/proj", "chat_2")
        self.registry.register(self.session, [{"name": "fetch"}])
        self.assertEqual(self.registry.get(other), [])

    def test_dichiarazioni_stringhe_supportate(self) -> None:
        self.registry.register(self.session, ["skill:a"])
        self.registry.register(self.session, ["skill:a", "skill:b"])
        self.assertEqual(self.registry.get(self.session), ["skill:a", "skill:b"])


if __name__ == "__main__":
    unittest.main()
