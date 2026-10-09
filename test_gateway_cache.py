import os  # noqa: I001
import tempfile
import unittest

from gateway_core import L1RedisCacheManager

class TestGatewayCache(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_mgr = L1RedisCacheManager(backend="memory")

    def test_content_based_invalidation(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as tmp:
            tmp.write("print('v1')")
            tmp_path = tmp.name

        try:
            # 1. Write to cache with initial file content
            self.cache_mgr.set(
                session_id="sess-1",
                use_case="coding",
                messages="refactor code",
                response="cached response v1",
                relevant_files=[tmp_path],
                profile="coding"
            )

            # 2. Read cache -> should be a HIT
            res_hit, provenance = self.cache_mgr.get(
                session_id="sess-1",
                use_case="coding",
                messages="refactor code",
                relevant_files=[tmp_path]
            )
            self.assertEqual(res_hit, "cached response v1")
            self.assertEqual(provenance, "cache_hit")

            # 3. Modify file content
            with open(tmp_path, "w") as f:
                f.write("print('v2 modified')")

            # 4. Read cache -> should be a MISS due to content change
            res_miss, provenance_miss = self.cache_mgr.get(
                session_id="sess-1",
                use_case="coding",
                messages="refactor code",
                relevant_files=[tmp_path]
            )
            self.assertIsNone(res_miss)
            self.assertEqual(provenance_miss, "cache_miss")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_profile_ttl(self) -> None:
        ttl = self.cache_mgr.get_ttl_for_profile("coding")
        self.assertEqual(ttl, 3600)

        ttl_default = self.cache_mgr.get_ttl_for_profile("unknown")
        self.assertEqual(ttl_default, 1800)

    def test_tool_response_cache_boundary(self) -> None:
        # Tool responses with write side-effects or sensitive instructions should bypass cache or have specific limits
        should_cache = self.cache_mgr.validate_cacheable("coding", "run shell rm -rf /")
        self.assertFalse(should_cache)

        should_cache_ok = self.cache_mgr.validate_cacheable("coding", "explain python function")
        self.assertTrue(should_cache_ok)

if __name__ == "__main__":
    unittest.main()
