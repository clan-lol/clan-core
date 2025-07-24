from clan_lib.flake.flake import FlakeCache, parse_selector


class TestFlakeAccessTracking:
    """Test the leaf-only access tracking feature for FlakeCache"""

    def test_leaf_access_tracking_simple(self) -> None:
        """Test that only leaf nodes have their access count incremented"""
        cache = FlakeCache()

        # Insert some data
        data = {"level1": {"level2": {"leaf": "value"}}}
        cache.insert(data, "")

        # Initially, the leaf should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("level1.level2.leaf"))

        # Mark the path as accessed
        cache.mark_path_accessed(parse_selector("level1.level2.leaf"))

        # Now the leaf should be accessed
        assert not cache.is_path_unaccessed(parse_selector("level1.level2.leaf"))

        # But intermediate nodes should still have _num_accessed == 0
        # We'll need to check this directly on the cache entries
        entry = cache.cache
        assert isinstance(entry.value, dict)
        assert entry._num_accessed == 0  # Root should not be incremented

        level1_entry = entry.value["level1"]
        assert level1_entry._num_accessed == 0  # level1 should not be incremented

        level2_entry = level1_entry.value["level2"]
        assert level2_entry._num_accessed == 0  # level2 should not be incremented

        leaf_entry = level2_entry.value["leaf"]
        assert leaf_entry._num_accessed == 1  # Only leaf should be incremented

    def test_leaf_access_tracking_multiple_paths(self) -> None:
        """Test access tracking with multiple paths"""
        cache = FlakeCache()

        # Insert data with multiple branches
        data = {"branch1": {"leaf1": "value1"}, "branch2": {"leaf2": "value2"}}
        cache.insert(data, "")

        # Initially both leaves should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("branch1.leaf1"))
        assert cache.is_path_unaccessed(parse_selector("branch2.leaf2"))

        # Access first leaf
        cache.mark_path_accessed(parse_selector("branch1.leaf1"))

        # First leaf should be accessed, second should not
        assert not cache.is_path_unaccessed(parse_selector("branch1.leaf1"))
        assert cache.is_path_unaccessed(parse_selector("branch2.leaf2"))

        # Access second leaf
        cache.mark_path_accessed(parse_selector("branch2.leaf2"))

        # Both should now be accessed
        assert not cache.is_path_unaccessed(parse_selector("branch1.leaf1"))
        assert not cache.is_path_unaccessed(parse_selector("branch2.leaf2"))

    def test_leaf_access_tracking_with_lists(self) -> None:
        """Test access tracking with list entries"""
        cache = FlakeCache()

        # Insert data with a list
        data = {"items": ["item0", "item1", "item2"]}
        cache.insert(data, "")

        # Check initial state
        assert cache.is_path_unaccessed(parse_selector("items.0"))
        assert cache.is_path_unaccessed(parse_selector("items.1"))
        assert cache.is_path_unaccessed(parse_selector("items.2"))

        # Access one item
        cache.mark_path_accessed(parse_selector("items.1"))

        # Only that item should be marked as accessed
        assert cache.is_path_unaccessed(parse_selector("items.0"))
        assert not cache.is_path_unaccessed(parse_selector("items.1"))
        assert cache.is_path_unaccessed(parse_selector("items.2"))

    def test_leaf_access_tracking_nonexistent_path(self) -> None:
        """Test that non-existent paths are considered unaccessed"""
        cache = FlakeCache()

        # Insert minimal data
        data = {"exists": "value"}
        cache.insert(data, "")

        # Non-existent path should be considered unaccessed
        assert cache.is_path_unaccessed(parse_selector("does.not.exist"))

        # Marking non-existent path should not crash
        cache.mark_path_accessed(parse_selector("does.not.exist"))

        # It should still be considered unaccessed since it doesn't exist
        assert cache.is_path_unaccessed(parse_selector("does.not.exist"))

    def test_leaf_access_tracking_integration_with_select(self) -> None:
        """Test that the access tracking works correctly with the select operation"""
        cache = FlakeCache()

        # Insert nested data
        data = {
            "config": {
                "database": {"host": "localhost", "port": 5432},
                "cache": {"enabled": True},
            }
        }
        cache.insert(data, "")

        # Verify all paths are initially unaccessed
        assert cache.is_path_unaccessed(parse_selector("config.database.host"))
        assert cache.is_path_unaccessed(parse_selector("config.database.port"))
        assert cache.is_path_unaccessed(parse_selector("config.cache.enabled"))

        # Select a value (this would happen in Flake.select)
        value = cache.select("config.database.host")
        assert value == "localhost"

        # Mark the path as accessed (simulating what Flake.select does)
        cache.mark_path_accessed(parse_selector("config.database.host"))

        # Only the accessed path should be marked
        assert not cache.is_path_unaccessed(parse_selector("config.database.host"))
        assert cache.is_path_unaccessed(parse_selector("config.database.port"))
        assert cache.is_path_unaccessed(parse_selector("config.cache.enabled"))

    def test_leaf_access_multiple_accesses(self) -> None:
        """Test that multiple accesses increment the counter"""
        cache = FlakeCache()

        data = {"key": "value"}
        cache.insert(data, "")

        # Initially unaccessed
        assert cache.is_path_unaccessed(parse_selector("key"))

        # Access once
        cache.mark_path_accessed(parse_selector("key"))
        assert not cache.is_path_unaccessed(parse_selector("key"))

        # Access again
        cache.mark_path_accessed(parse_selector("key"))
        assert not cache.is_path_unaccessed(parse_selector("key"))

        # Check the actual count
        assert isinstance(cache.cache.value, dict)
        entry = cache.cache.value["key"]
        assert entry._num_accessed == 2

    def test_leaf_access_tracking_with_set_selectors(self) -> None:
        """Test access tracking with SET selectors (subselectors)"""
        cache = FlakeCache()

        # Insert data with multiple keys at the same level
        data = {"apps": {"web": "web-app", "api": "api-service", "db": "database"}}
        cache.insert(data, "")

        # Initially all should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("apps.web"))
        assert cache.is_path_unaccessed(parse_selector("apps.api"))
        assert cache.is_path_unaccessed(parse_selector("apps.db"))

        # Use SET selector to access multiple keys at once
        cache.mark_path_accessed(parse_selector("apps.{web,api}"))

        # Only the keys in the set should be marked as accessed
        assert not cache.is_path_unaccessed(parse_selector("apps.web"))
        assert not cache.is_path_unaccessed(parse_selector("apps.api"))
        assert cache.is_path_unaccessed(parse_selector("apps.db"))  # Not in set

        # Verify the intermediate node is not marked as accessed
        assert isinstance(cache.cache.value, dict)
        apps_entry = cache.cache.value["apps"]
        assert (
            apps_entry._num_accessed == 0
        )  # Intermediate node should not be incremented

    def test_leaf_access_tracking_set_selectors_nested(self) -> None:
        """Test SET selectors with nested paths"""
        cache = FlakeCache()

        # Insert nested data
        data = {
            "services": {
                "frontend": {"port": 3000, "host": "localhost"},
                "backend": {"port": 8080, "host": "0.0.0.0"},
            }
        }
        cache.insert(data, "")

        # Use SET selector at different nesting levels
        cache.mark_path_accessed(parse_selector("services.{frontend,backend}.port"))

        # Both port leaves should be accessed
        assert not cache.is_path_unaccessed(parse_selector("services.frontend.port"))
        assert not cache.is_path_unaccessed(parse_selector("services.backend.port"))

        # Host leaves should not be accessed
        assert cache.is_path_unaccessed(parse_selector("services.frontend.host"))
        assert cache.is_path_unaccessed(parse_selector("services.backend.host"))

    def test_leaf_access_tracking_set_selectors_partial_match(self) -> None:
        """Test SET selectors when some keys don't exist"""
        cache = FlakeCache()

        # Insert data with only some of the keys that will be requested
        data = {
            "config": {
                "database": "postgres",
                "cache": "redis",
                # Note: 'queue' key is missing
            }
        }
        cache.insert(data, "")

        # Use SET selector that includes non-existent key
        cache.mark_path_accessed(parse_selector("config.{database,cache,queue}"))

        # Existing keys should be marked as accessed
        assert not cache.is_path_unaccessed(parse_selector("config.database"))
        assert not cache.is_path_unaccessed(parse_selector("config.cache"))

        # Non-existent key should still be considered unaccessed
        assert cache.is_path_unaccessed(parse_selector("config.queue"))

    def test_leaf_access_tracking_set_selectors_is_path_unaccessed(self) -> None:
        """Test is_path_unaccessed with SET selectors"""
        cache = FlakeCache()

        # Insert data
        data = {"metrics": {"cpu": 50, "memory": 80, "disk": 30}}
        cache.insert(data, "")

        # Initially, SET selector path should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("metrics.{cpu,memory}"))

        # Access one of the keys in the set
        cache.mark_path_accessed(parse_selector("metrics.cpu"))

        # Now the SET selector should be considered accessed (since at least one key is accessed)
        assert not cache.is_path_unaccessed(parse_selector("metrics.{cpu,memory}"))

        # But a different SET selector should still be unaccessed
        assert cache.is_path_unaccessed(parse_selector("metrics.{memory,disk}"))

    def test_leaf_access_tracking_set_selectors_mixed_access(self) -> None:
        """Test SET selectors with mixed individual and set access patterns"""
        cache = FlakeCache()

        # Insert data
        data = {
            "endpoints": {
                "users": "/api/users",
                "posts": "/api/posts",
                "comments": "/api/comments",
                "auth": "/api/auth",
            }
        }
        cache.insert(data, "")

        # Access individual key first
        cache.mark_path_accessed(parse_selector("endpoints.users"))

        # Then access using SET selector
        cache.mark_path_accessed(parse_selector("endpoints.{posts,comments}"))

        # Check individual access states
        assert not cache.is_path_unaccessed(
            parse_selector("endpoints.users")
        )  # Individual access
        assert not cache.is_path_unaccessed(
            parse_selector("endpoints.posts")
        )  # SET access
        assert not cache.is_path_unaccessed(
            parse_selector("endpoints.comments")
        )  # SET access
        assert cache.is_path_unaccessed(
            parse_selector("endpoints.auth")
        )  # Not accessed

        # Verify access counts
        assert isinstance(cache.cache.value, dict)
        endpoints_entry = cache.cache.value["endpoints"]
        assert isinstance(endpoints_entry.value, dict)

        # Each accessed leaf should have _num_accessed == 1
        assert endpoints_entry.value["users"]._num_accessed == 1
        assert endpoints_entry.value["posts"]._num_accessed == 1
        assert endpoints_entry.value["comments"]._num_accessed == 1
        assert endpoints_entry.value["auth"]._num_accessed == 0

    def test_leaf_access_tracking_with_all_selectors(self) -> None:
        """Test access tracking with ALL selectors (*)"""
        cache = FlakeCache()

        # Insert data with multiple keys at the same level
        data = {
            "packages": {
                "python": "3.11",
                "nodejs": "18.0",
                "java": "17.0",
                "rust": "1.70",
            }
        }
        cache.insert(data, "")

        # Initially all should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("packages.python"))
        assert cache.is_path_unaccessed(parse_selector("packages.nodejs"))
        assert cache.is_path_unaccessed(parse_selector("packages.java"))
        assert cache.is_path_unaccessed(parse_selector("packages.rust"))

        # Use ALL selector to access all keys at once
        cache.mark_path_accessed(parse_selector("packages.*"))

        # All keys should now be marked as accessed
        assert not cache.is_path_unaccessed(parse_selector("packages.python"))
        assert not cache.is_path_unaccessed(parse_selector("packages.nodejs"))
        assert not cache.is_path_unaccessed(parse_selector("packages.java"))
        assert not cache.is_path_unaccessed(parse_selector("packages.rust"))

        # Verify the intermediate node is not marked as accessed
        assert isinstance(cache.cache.value, dict)
        packages_entry = cache.cache.value["packages"]
        assert (
            packages_entry._num_accessed == 0
        )  # Intermediate node should not be incremented

        # Verify each leaf has been accessed exactly once
        assert isinstance(packages_entry.value, dict)
        assert packages_entry.value["python"]._num_accessed == 1
        assert packages_entry.value["nodejs"]._num_accessed == 1
        assert packages_entry.value["java"]._num_accessed == 1
        assert packages_entry.value["rust"]._num_accessed == 1

    def test_leaf_access_tracking_all_selectors_nested(self) -> None:
        """Test ALL selectors with nested paths"""
        cache = FlakeCache()

        # Insert nested data
        data = {
            "environments": {
                "dev": {"database": "dev-db", "cache": "dev-cache"},
                "prod": {"database": "prod-db", "cache": "prod-cache"},
                "test": {"database": "test-db", "cache": "test-cache"},
            }
        }
        cache.insert(data, "")

        # Use ALL selector at different nesting levels
        cache.mark_path_accessed(parse_selector("environments.*.database"))

        # All database leaves should be accessed
        assert not cache.is_path_unaccessed(parse_selector("environments.dev.database"))
        assert not cache.is_path_unaccessed(
            parse_selector("environments.prod.database")
        )
        assert not cache.is_path_unaccessed(
            parse_selector("environments.test.database")
        )

        # Cache leaves should not be accessed
        assert cache.is_path_unaccessed(parse_selector("environments.dev.cache"))
        assert cache.is_path_unaccessed(parse_selector("environments.prod.cache"))
        assert cache.is_path_unaccessed(parse_selector("environments.test.cache"))

    def test_leaf_access_tracking_all_selectors_is_path_unaccessed(self) -> None:
        """Test is_path_unaccessed with ALL selectors"""
        cache = FlakeCache()

        # Insert data
        data = {"services": {"web": "nginx", "api": "fastapi", "worker": "celery"}}
        cache.insert(data, "")

        # Initially, ALL selector path should be unaccessed
        assert cache.is_path_unaccessed(parse_selector("services.*"))

        # Access one of the keys individually
        cache.mark_path_accessed(parse_selector("services.web"))

        # Now the ALL selector should be considered accessed (since at least one key is accessed)
        assert not cache.is_path_unaccessed(parse_selector("services.*"))

    def test_leaf_access_tracking_comprehensive_mixed_selectors(self) -> None:
        """Comprehensive test combining ALL, SET, individual, and list selectors"""
        cache = FlakeCache()

        # Insert complex nested data structure
        data = {
            "cluster": {
                "nodes": {
                    "master": {"cpu": 4, "memory": "8GB", "disk": "100GB"},
                    "worker1": {"cpu": 2, "memory": "4GB", "disk": "50GB"},
                    "worker2": {"cpu": 2, "memory": "4GB", "disk": "50GB"},
                },
                "config": {
                    "network": "10.0.0.0/8",
                    "storage": "nfs",
                    "monitoring": "prometheus",
                },
                "services": ["api", "web", "database", "cache"],
                "metadata": {"version": "1.0", "created": "2023-01-01"},
            }
        }
        cache.insert(data, "")

        # Phase 1: Use individual selector
        cache.mark_path_accessed(parse_selector("cluster.config.network"))
        assert not cache.is_path_unaccessed(parse_selector("cluster.config.network"))
        assert cache.is_path_unaccessed(parse_selector("cluster.config.storage"))

        # Phase 2: Use SET selector
        cache.mark_path_accessed(parse_selector("cluster.nodes.{master,worker1}.cpu"))
        assert not cache.is_path_unaccessed(parse_selector("cluster.nodes.master.cpu"))
        assert not cache.is_path_unaccessed(parse_selector("cluster.nodes.worker1.cpu"))
        assert cache.is_path_unaccessed(parse_selector("cluster.nodes.worker2.cpu"))

        # Phase 3: Use ALL selector
        cache.mark_path_accessed(parse_selector("cluster.metadata.*"))
        assert not cache.is_path_unaccessed(parse_selector("cluster.metadata.version"))
        assert not cache.is_path_unaccessed(parse_selector("cluster.metadata.created"))

        # Phase 4: Use list selector
        cache.mark_path_accessed(parse_selector("cluster.services.1"))  # "web"
        assert not cache.is_path_unaccessed(parse_selector("cluster.services.1"))
        assert cache.is_path_unaccessed(parse_selector("cluster.services.0"))  # "api"

        # Phase 5: Complex combination - ALL selector followed by SET selector
        cache.mark_path_accessed(parse_selector("cluster.nodes.*.{memory,disk}"))

        # All memory and disk leaves should be accessed
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.master.memory")
        )
        assert not cache.is_path_unaccessed(parse_selector("cluster.nodes.master.disk"))
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.worker1.memory")
        )
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.worker1.disk")
        )
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.worker2.memory")
        )
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.worker2.disk")
        )

        # Verify intermediate nodes are not accessed
        assert isinstance(cache.cache.value, dict)
        cluster_entry = cache.cache.value["cluster"]
        assert cluster_entry._num_accessed == 0

        assert isinstance(cluster_entry.value, dict)
        nodes_entry = cluster_entry.value["nodes"]
        assert nodes_entry._num_accessed == 0

        config_entry = cluster_entry.value["config"]
        assert config_entry._num_accessed == 0

        # Verify specific leaf access counts
        assert isinstance(nodes_entry.value, dict)
        master_entry = nodes_entry.value["master"]
        assert master_entry._num_accessed == 0  # Intermediate node

        assert isinstance(master_entry.value, dict)
        # CPU was accessed once via SET selector
        assert master_entry.value["cpu"]._num_accessed == 1
        # Memory and disk were accessed once via ALL+SET combination
        assert master_entry.value["memory"]._num_accessed == 1
        assert master_entry.value["disk"]._num_accessed == 1

        # Verify that mixed selector patterns work correctly
        # Test a complex query that should be unaccessed
        assert cache.is_path_unaccessed(
            parse_selector("cluster.config.{storage,monitoring}")
        )

        # Test a complex query that should be accessed
        assert not cache.is_path_unaccessed(
            parse_selector("cluster.nodes.{master,worker2}.memory")
        )
