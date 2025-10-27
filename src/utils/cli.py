"""Diagnostics CLI for helper tasks.

Usage examples:
  python -m src.utils.cli inspect-html --file data/debug_page.html
  python -m src.utils.cli trello-auth
  python -m src.utils.cli trello-inspect
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

import requests

import src.utils.env as env_utils
import src.utils.trello as trello_utils
from src.utils.html_utils import (
    load_html_file,
    parse_html,
    find_headers,
    find_data_at_elements,
    extract_json_ld_blocks,
    search_keywords,
)


def cmd_inspect_html(args: argparse.Namespace) -> int:
    filename = args.file
    print("=== HTML Structure Inspector ===\n")
    print(f"Loading file: {filename}")
    try:
        html_content = load_html_file(filename)
        print(f"✓ File loaded: {len(html_content)} characters\n")
    except FileNotFoundError:
        print(f"✗ Error: File not found: {filename}")
        return 1
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return 1

    print("Parsing HTML...")
    soup = parse_html(html_content, 'lxml')
    print("✓ HTML parsed\n")

    print("--- Step 1: Headers (h1, h2, h3) ---")
    try:
        headers = find_headers(soup, ("h1", "h2", "h3"), limit=10)
        print(f"Found {len(headers)} headers\n")
        for i, (name, text) in enumerate(headers):
            print(f"{i+1}. <{name}>: {text[:100]}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

    print("--- Step 2: Elements with data-at attributes ---")
    try:
        elems = find_data_at_elements(soup, limit=20)
        print(f"Found {len(elems)} elements with data-at\n")
        for data_at, text in elems:
            print(f"  data-at='{data_at}': {text[:80]}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

    print("--- Step 3: JSON-LD Structured Data ---")
    try:
        json_ld_objs = extract_json_ld_blocks(soup)
        print(f"Found {len(json_ld_objs)} JSON-LD blocks\n")
        for i, obj in enumerate(json_ld_objs, start=1):
            type_val = obj.get('@type', 'unknown')
            print(f"JSON-LD Block {i} (@type: {type_val}):")
            try:
                print(json.dumps(obj, indent=2, ensure_ascii=False)[:800])
            except Exception:
                print(str(obj)[:800])
            print("...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    if args.keywords:
        print("--- Step 4: Searching for key elements ---")
        keywords = {k: v for k, v in args.keywords}
        results = search_keywords(soup, keywords, limit_per=3)
        for key, occurrences in results.items():
            term = keywords[key]
            print(f"\nSearching for '{term}':")
            print(f"  Found in {len(occurrences)} places")
            for occ in occurrences:
                print(f"  - In <{occ['parent_tag']}> tag")
                print(f"    Classes: {occ['classes']}")
                print(f"    Text preview: {occ['preview']}")

    print("\n=== Inspection Complete ===")
    return 0


def cmd_trello_auth(_: argparse.Namespace) -> int:
    env_utils.load_env()
    auth = trello_utils.get_auth_params()
    key = auth.get('key', '')
    token = auth.get('token', '')
    print("Testing Trello API connection...")
    print(f"Key: {trello_utils.mask_secret(key, 10)}")
    print(f"Token: {trello_utils.mask_secret(token, 10)}")

    if not key or not token:
        print("✗ Missing key/token. Please set TRELLO_KEY and TRELLO_TOKEN in config/.env")
        return 1

    url = f"{trello_utils.TRELLO_API_BASE}/members/me"
    resp = requests.get(url, params=auth, timeout=20)
    print(f"\nStatus Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ Success! Logged in as: {data.get('fullName')}")
        print(f"✓ Username: {data.get('username')}")
        return 0
    else:
        print("✗ Failed!")
        print(f"Response: {resp.text}")
        return 2


def cmd_trello_inspect(_: argparse.Namespace) -> int:
    env_utils.load_env()
    auth = trello_utils.get_auth_params()
    board_id = env_utils.get_str('TRELLO_BOARD_ID')
    if not auth.get('key') or not auth.get('token'):
        print("✗ Missing Trello credentials (TRELLO_KEY/TRELLO_TOKEN)")
        return 1
    if not board_id:
        print("✗ Missing TRELLO_BOARD_ID in environment")
        return 1

    base = trello_utils.TRELLO_API_BASE
    def get(path: str, **params: Any):
        p = {**auth, **params}
        return requests.get(f"{base}/{path}", params=p, timeout=30)

    # Board info
    print("=== Trello Board Inspect ===")
    resp = get(f"boards/{board_id}")
    if resp.status_code != 200:
        print(f"✗ Failed to fetch board: {resp.status_code} {resp.text}")
        return 2
    board = resp.json()
    print(f"Board: {board.get('name')} | {board.get('url')}")

    # Lists
    lists = get(f"boards/{board_id}/lists").json()
    print(f"\nLists ({len(lists)}):")
    for lst in lists:
        print(f" - {lst.get('name')} (id={lst.get('id')})")

    # Labels
    labels = get(f"boards/{board_id}/labels").json()
    print(f"\nLabels ({len(labels)}):")
    for lab in labels:
        name = lab.get('name') or '(No name)'
        print(f" - {name} (color={lab.get('color')}, id={lab.get('id')})")

    # Custom Fields
    custom_resp = get(f"boards/{board_id}/customFields")
    if custom_resp.status_code == 200:
        fields = custom_resp.json()
        print(f"\nCustom Fields ({len(fields)}):")
        for field in fields:
            field_type = field.get('type', 'unknown')
            field_name = field.get('name', '(No name)')
            print(f" - {field_name} (type={field_type}, id={field.get('id')})")
            if field_type == 'list' and 'options' in field:
                opts = [opt['value']['text'] for opt in field.get('options', [])]
                print(f"   Options: {', '.join(opts)}")
    else:
        print(f"\nCustom Fields: Could not retrieve (status {custom_resp.status_code})")

    print("\n=== Done ===")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="helper-cli", description="Diagnostics CLI for helper tasks")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_html = sub.add_parser("inspect-html", help="Inspect an HTML file for structure and JSON-LD")
    p_html.add_argument("--file", default="data/debug_page.html", help="Path to HTML file")
    p_html.add_argument("--keywords", nargs=2, action="append", metavar=("KEY", "VALUE"), help="Keyword pair to search (repeatable)")
    p_html.set_defaults(func=cmd_inspect_html)

    p_auth = sub.add_parser("trello-auth", help="Probe Trello auth and print user profile")
    p_auth.set_defaults(func=cmd_trello_auth)

    p_inspect = sub.add_parser("trello-inspect", help="Inspect Trello board lists and labels")
    p_inspect.set_defaults(func=cmd_trello_inspect)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
