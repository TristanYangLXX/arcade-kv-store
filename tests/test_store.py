from store import Store
import pytest

def test_set_get():
    s = Store()
    s.set("a", 1)
    assert s.get("a") == 1

def test_delete_and_missing():
    s = Store()
    s.set("x", 42)
    s.delete("x")
    with pytest.raises(KeyError):
        s.get("x")

def test_tx_commit_and_rollback():
    s = Store()
    s.set("a", 1)
    s.begin()
    s.set("a", 2)
    assert s.get("a") == 2
    s.rollback()
    assert s.get("a") == 1

    s.begin()
    s.set("a", 3)
    s.commit()
    assert s.get("a") == 3

def test_nested_tx():
    s = Store()
    s.set("k", 0)
    s.begin()
    s.set("k", 1)
    s.begin()
    s.set("k", 2)
    assert s.get("k") == 2
    s.rollback()          # drop inner change
    assert s.get("k") == 1
    s.commit()
    assert s.get("k") == 1

def test_commit_without_tx_raises():
    s = Store()
    with pytest.raises(RuntimeError):
        s.commit()

def test_rollback_without_tx_raises():
    s = Store()
    with pytest.raises(RuntimeError):
        s.rollback()
