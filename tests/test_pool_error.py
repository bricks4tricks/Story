import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_utils


def test_get_pool_failure(monkeypatch):
    # ensure no pool exists before the call
    monkeypatch.setattr(db_utils, "connection_pool", None)

    def boom(*args, **kwargs):
        raise Exception("pool boom")

    monkeypatch.setattr(db_utils, "SimpleConnectionPool", boom)

    with pytest.raises(RuntimeError) as excinfo:
        db_utils._get_pool()

    assert "pool boom" in str(excinfo.value)
    assert db_utils.connection_pool is None
