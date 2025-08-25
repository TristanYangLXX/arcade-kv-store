# store.py
class Store:
    """In-memory KV store with nested transactions (overlay stack)."""

    _TOMBSTONE = object()  # marks a deletion in overlays

    def __init__(self):
        self._base = {}        # committed state
        self._tx_stack = []    # list[dict] of overlay deltas (outermost at end)

    # ---------- internal helpers ----------
    def _has_tx(self) -> bool:
        return bool(self._tx_stack)

    def _top(self) -> dict:
        return self._tx_stack[-1]

    def _resolve(self, key):
        print(f"Resolving key: {key}, tx_stack: {self._tx_stack}, base: {self._base}")
        for layer in reversed(self._tx_stack):
            if key in layer:
                val = layer[key]
                if val is self._TOMBSTONE:
                    raise KeyError(key)
                return val
        if key in self._base:
            return self._base[key]
        raise KeyError(key)

    # ---------- public API ----------
    def get(self, key):
        return self._resolve(key)

    def set(self, key, value):
        if self._has_tx():
            self._top()[key] = value
        else:
            self._base[key] = value

    def delete(self, key):
        if self._has_tx():
            self._top()[key] = self._TOMBSTONE
        else:
            print(f"Before pop: {self._base}")
            self._base.pop(key, None)
            print(f"After pop: {self._base}")

    # ---------- transactions ----------
    def begin(self):
        self._tx_stack.append({})

    def commit(self):
        if not self._has_tx():
            raise RuntimeError("No transaction to commit")
        changes = self._tx_stack.pop()
        if self._has_tx():
            # merge into parent overlay
            self._top().update(changes)
        else:
            # apply to base
            for k, v in changes.items():
                if v is self._TOMBSTONE:
                    self._base.pop(k, None)
                else:
                    self._base[k] = v

    def rollback(self):
        if not self._has_tx():
            raise RuntimeError("No transaction to rollback")
        self._tx_stack.pop()

    # ---------- helpers for REST ----------
    def exists(self, key) -> bool:
        try:
            self._resolve(key)
            return True
        except KeyError:
            return False

    def list_keys(self):
        keys = set(self._base.keys())
        for layer in self._tx_stack:
            for k, v in layer.items():
                if v is self._TOMBSTONE:
                    keys.discard(k)
                else:
                    keys.add(k)
        return sorted(keys)

    def clear(self):
        self._base.clear()
        self._tx_stack.clear()