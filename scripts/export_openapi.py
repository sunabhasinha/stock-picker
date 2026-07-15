"""Dump the FastAPI app's OpenAPI spec to stdout - the inter-zone
contract (ADR-0007). The frontend's `npm run gen:api` pipes this through
openapi-typescript; CI regenerates and fails on drift."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.server import create_app  # noqa: E402

if __name__ == "__main__":
    print(json.dumps(create_app().openapi(), indent=2, sort_keys=True))
