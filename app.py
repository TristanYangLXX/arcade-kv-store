from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from store import Store

app = Flask(__name__)
store = Store()

# Error handlers
@app.errorhandler(RuntimeError)
def handle_runtime_error(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(KeyError)
def handle_key_error(e):
    return jsonify({"error": f"key not found: {e.args[0] if e.args else ''}"}), 404

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "invalid request"}), 400

# KV routes
@app.get("/get/<key>")
def get_key(key):
    value = store.get(key)  # let this raise KeyError if missing
    return jsonify({"value": value}), 200

@app.post("/set")
def set_key():
    if not request.is_json:
        raise BadRequest()
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    value = data.get("value")
    if key is None or value is None:
        return jsonify({"error": "key and value required"}), 400
    store.set(key, value)
    return jsonify({"status": "ok"}), 200  

@app.delete("/delete/<key>")
def delete_key(key):
    store.delete(key)  # let this raise KeyError if missing
    return jsonify({"status": "ok"}), 200  

# Transactions
@app.post("/begin")
def begin_tx():
    store.begin()
    return jsonify({"status": "ok"}), 200

@app.post("/commit")
def commit_tx():
    store.commit()  
    return jsonify({"status": "ok"}), 200

@app.post("/rollback")
def rollback_tx():
    store.rollback()
    return jsonify({"status": "ok"}), 200

# Introspection
@app.get("/keys")
def list_keys():
    return jsonify({"keys": store.list_keys()}), 200

@app.get("/exists/<key>")
def exists_key(key):
    return jsonify({"exists": store.exists(key)}), 200

if __name__ == "__main__":
    # run via python app.py
    app.run(debug=True)
