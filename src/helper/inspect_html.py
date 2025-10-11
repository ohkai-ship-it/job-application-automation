import json

from src.utils.html import (
    load_html_file,
    parse_html,
    find_headers,
    find_data_at_elements,
    extract_json_ld_blocks,
    search_keywords,
)

def inspect_html_structure(filename='data/debug_page.html'):
    """
    Inspects the HTML structure to find where data is located
    """
    
    print("=== HTML Structure Inspector ===\n")
    print(f"Loading file: {filename}")
    
    try:
        html_content = load_html_file(filename)
        print(f"✓ File loaded: {len(html_content)} characters\n")
    except FileNotFoundError:
        print(f"✗ Error: File not found: {filename}")
        return
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return
    
    print("Parsing HTML...")
    soup = parse_html(html_content, 'lxml')
    print("✓ HTML parsed\n")
    
    # 1. Find all headers
    print("--- Step 1: Headers (h1, h2, h3) ---")
    try:
        headers = find_headers(soup, ("h1", "h2", "h3"), limit=10)
        print(f"Found {len(headers)} headers\n")
        for i, (name, text) in enumerate(headers):
            print(f"{i+1}. <{name}>: {text[:100]}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 2. Look for data-at attributes (Stepstone specific)
    print("--- Step 2: Elements with data-at attributes ---")
    try:
        elems = find_data_at_elements(soup, limit=20)
        print(f"Found {len(elems)} elements with data-at\n")
        for data_at, text in elems:
            print(f"  data-at='{data_at}': {text[:80]}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 3. Find JSON-LD (structured data)
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
    
    # 4. Search for specific keywords
    print("--- Step 4: Searching for key elements ---")
    keywords = {
        'company': 'Toll Collect',
        'location': 'Berlin',
        'description_header': 'Ihre Aufgaben'
    }
    
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


if __name__ == "__main__":
    inspect_html_structure()