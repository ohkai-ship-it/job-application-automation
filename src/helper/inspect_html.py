from bs4 import BeautifulSoup
import json

def inspect_html_structure(filename='data/debug_page.html'):
    """
    Inspects the HTML structure to find where data is located
    """
    
    print("=== HTML Structure Inspector ===\n")
    print(f"Loading file: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"✓ File loaded: {len(html_content)} characters\n")
    except FileNotFoundError:
        print(f"✗ Error: File not found: {filename}")
        return
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return
    
    print("Parsing HTML...")
    soup = BeautifulSoup(html_content, 'lxml')
    print("✓ HTML parsed\n")
    
    # 1. Find all headers
    print("--- Step 1: Headers (h1, h2, h3) ---")
    try:
        headers = soup.find_all(['h1', 'h2', 'h3'])
        print(f"Found {len(headers)} headers\n")
        for i, header in enumerate(headers[:10]):
            text = header.get_text(strip=True)[:100]
            print(f"{i+1}. <{header.name}>: {text}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 2. Look for data-at attributes (Stepstone specific)
    print("--- Step 2: Elements with data-at attributes ---")
    try:
        data_at_elements = soup.find_all(attrs={'data-at': True})
        print(f"Found {len(data_at_elements)} elements with data-at\n")
        for elem in data_at_elements[:20]:
            data_at = elem.get('data-at')
            text = elem.get_text(strip=True)[:80]
            print(f"  data-at='{data_at}': {text}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 3. Find JSON-LD (structured data)
    print("--- Step 3: JSON-LD Structured Data ---")
    try:
        json_ld = soup.find_all('script', type='application/ld+json')
        print(f"Found {len(json_ld)} JSON-LD blocks\n")
        for i, script in enumerate(json_ld):
            if script.string:
                try:
                    data = json.loads(script.string)
                    print(f"JSON-LD Block {i+1} (@type: {data.get('@type', 'unknown')}):")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:800])
                    print("...\n")
                except Exception as e:
                    print(f"Could not parse JSON-LD block {i+1}: {e}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 4. Search for specific keywords
    print("--- Step 4: Searching for key elements ---")
    keywords = {
        'company': 'Toll Collect',
        'location': 'Berlin',
        'description_header': 'Ihre Aufgaben'
    }
    
    for key, search_term in keywords.items():
        print(f"\nSearching for '{search_term}':")
        elements = soup.find_all(string=lambda text: text and search_term in text)
        print(f"  Found in {len(elements)} places")
        for elem in elements[:3]:
            parent = elem.parent
            print(f"  - In <{parent.name}> tag")
            print(f"    Classes: {parent.get('class')}")
            print(f"    Text preview: {elem.strip()[:60]}...")
    
    print("\n=== Inspection Complete ===")


if __name__ == "__main__":
    inspect_html_structure()