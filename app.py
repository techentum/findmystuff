from __future__ import annotations

import re
from typing import Any, Dict, List

from flask import Flask, jsonify, request

app = Flask(__name__)

BIN_ID_PATTERN = re.compile(r"^\d{4}$")

bins: Dict[str, Dict[str, Any]] = {}
items: Dict[str, Dict[str, Any]] = {}


def _parse_tags(payload: Dict[str, Any]) -> List[str]:
    tags = payload.get("tags", [])
    if tags is None:
        return []
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("tags must be a list of strings")
    return tags


def _ensure_bin_id(bin_id: str) -> None:
    if not BIN_ID_PATTERN.match(bin_id):
        raise ValueError("bin_id must be a 4 digit string")


def _filter_by_tags(collection: Dict[str, Dict[str, Any]], tag: str | None) -> List[Dict[str, Any]]:
    if not tag:
        return list(collection.values())
    return [value for value in collection.values() if tag in value.get("tags", [])]


@app.errorhandler(ValueError)
def handle_value_error(error: ValueError):
    return jsonify({"error": str(error)}), 400


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


@app.route("/bins", methods=["GET"])
def list_bins() -> Any:
    tag = request.args.get("tag")
    return jsonify(_filter_by_tags(bins, tag))


@app.route("/bins", methods=["POST"])
def create_bin() -> Any:
    payload = request.get_json(force=True, silent=True) or {}
    bin_id = payload.get("id")
    if not bin_id:
        raise ValueError("id is required")
    _ensure_bin_id(bin_id)
    if bin_id in bins:
        raise ValueError("bin already exists")
    location = payload.get("location")
    if not location:
        raise ValueError("location is required")
    tags = _parse_tags(payload)
    bin_record = {"id": bin_id, "location": location, "tags": tags}
    bins[bin_id] = bin_record
    return jsonify(bin_record), 201


@app.route("/bins/<bin_id>", methods=["GET"])
def get_bin(bin_id: str) -> Any:
    bin_record = bins.get(bin_id)
    if not bin_record:
        return jsonify({"error": "bin not found"}), 404
    return jsonify(bin_record)


@app.route("/bins/<bin_id>", methods=["PUT"])
def update_bin(bin_id: str) -> Any:
    _ensure_bin_id(bin_id)
    if bin_id not in bins:
        return jsonify({"error": "bin not found"}), 404
    payload = request.get_json(force=True, silent=True) or {}
    location = payload.get("location", bins[bin_id]["location"])
    tags = _parse_tags(payload)
    if not tags:
        tags = bins[bin_id].get("tags", [])
    bins[bin_id] = {"id": bin_id, "location": location, "tags": tags}
    return jsonify(bins[bin_id])


@app.route("/bins/<bin_id>", methods=["DELETE"])
def delete_bin(bin_id: str) -> Any:
    if bin_id not in bins:
        return jsonify({"error": "bin not found"}), 404
    if any(item.get("bin_id") == bin_id for item in items.values()):
        return jsonify({"error": "bin has items; move or delete them first"}), 400
    del bins[bin_id]
    return jsonify({"status": "deleted"})


@app.route("/bins/<bin_id>/items", methods=["GET"])
def list_bin_items(bin_id: str) -> Any:
    if bin_id not in bins:
        return jsonify({"error": "bin not found"}), 404
    tag = request.args.get("tag")
    bin_items = {item_id: item for item_id, item in items.items() if item.get("bin_id") == bin_id}
    return jsonify(_filter_by_tags(bin_items, tag))


@app.route("/items", methods=["GET"])
def list_items() -> Any:
    tag = request.args.get("tag")
    return jsonify(_filter_by_tags(items, tag))


@app.route("/items", methods=["POST"])
def create_item() -> Any:
    payload = request.get_json(force=True, silent=True) or {}
    item_id = payload.get("id")
    if not item_id:
        raise ValueError("id is required")
    if item_id in items:
        raise ValueError("item already exists")
    name = payload.get("name")
    if not name:
        raise ValueError("name is required")
    bin_id = payload.get("bin_id")
    if not bin_id:
        raise ValueError("bin_id is required")
    _ensure_bin_id(bin_id)
    if bin_id not in bins:
        raise ValueError("bin does not exist")
    tags = _parse_tags(payload)
    item_record = {"id": item_id, "name": name, "bin_id": bin_id, "tags": tags}
    items[item_id] = item_record
    return jsonify(item_record), 201


@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id: str) -> Any:
    item_record = items.get(item_id)
    if not item_record:
        return jsonify({"error": "item not found"}), 404
    return jsonify(item_record)


@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id: str) -> Any:
    if item_id not in items:
        return jsonify({"error": "item not found"}), 404
    payload = request.get_json(force=True, silent=True) or {}
    name = payload.get("name", items[item_id]["name"])
    bin_id = payload.get("bin_id", items[item_id]["bin_id"])
    _ensure_bin_id(bin_id)
    if bin_id not in bins:
        raise ValueError("bin does not exist")
    tags = _parse_tags(payload)
    if not tags:
        tags = items[item_id].get("tags", [])
    items[item_id] = {"id": item_id, "name": name, "bin_id": bin_id, "tags": tags}
    return jsonify(items[item_id])


@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id: str) -> Any:
    if item_id not in items:
        return jsonify({"error": "item not found"}), 404
    del items[item_id]
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
