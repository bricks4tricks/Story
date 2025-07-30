import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import version_cache


def test_users_version_timezone():
    assert version_cache.users_version.tzinfo is datetime.timezone.utc
    version_cache.update_users_version()
    assert version_cache.users_version.tzinfo is datetime.timezone.utc
