#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


def validate_contract(contract: dict) -> list[str]:
    errors: list[str] = []
    required = contract.get("required")
    if not isinstance(required, list):
        return ["contract missing required list: required"]
    for idx, item in enumerate(required):
        if not isinstance(item, dict):
            errors.append(f"required[{idx}] must be an object")
            continue
        key = item.get("key")
        pattern = item.get("pattern")
        if not isinstance(key, str) or not key:
            errors.append(f"required[{idx}].key must be a non-empty string")
        if not isinstance(pattern, str) or not pattern:
            errors.append(f"required[{idx}].pattern must be a non-empty string")
    return errors


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    seen: set[str] = set()
    errors: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            errors.append("malformed env line with empty key")
            continue
        if key in seen:
            errors.append(f"duplicate key: {key}")
            continue
        seen.add(key)
        values[key] = value
    if errors:
        raise ValueError("; ".join(errors))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .env.example against contract")
    parser.add_argument("--contract", default="config/env-contract.json")
    parser.add_argument("--env-file", default=".env.example")
    args = parser.parse_args()

    contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
    contract_errors = validate_contract(contract)
    if contract_errors:
        print("env contract parse failed")
        for error in contract_errors:
            print(f" - {error}")
        return 1
    try:
        values = parse_env(Path(args.env_file))
    except ValueError as exc:
        print("env template parse failed")
        print(f" - {exc}")
        return 1

    errors: list[str] = []
    for item in contract.get("required", []):
        key = item["key"]
        pattern = item["pattern"]
        value = values.get(key)
        if value is None:
            errors.append(f"missing key: {key}")
            continue
        if re.match(pattern, value) is None:
            errors.append(f"invalid value for {key}: {value!r} does not match {pattern}")

    if errors:
        print("env template contract validation failed")
        for error in errors:
            print(f" - {error}")
        return 1

    print("env template contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
