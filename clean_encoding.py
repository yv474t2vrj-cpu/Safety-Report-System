import re

def clean_file(input_file, output_file=None):
    if output_file is None:
        output_file = input_file
    
    # Read with multiple encoding attempts
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        # Last resort: binary read
        with open(input_file, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        print("Read with error replacement")
    
    # Fix common problematic characters
    replacements = {
        'â€¢': '•',
        'âœ“': '[OK]',
        'âš€': '',
        'â€"': '-',
        'â€™': "'",
        'â€œ': '"',
        'â€': '"',
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã¢': 'â',
        'Ã': 'í',
        '©': 'é',
        '®': '®',
        '™': '™',
        '°': '°',
    }
    
    for bad, good in replacements.items():
        content = content.replace(bad, good)
    
    # Remove any remaining non-ASCII except basic punctuation
    content = re.sub(r'[^\x00-\x7F]', '*', content)
    
    # Write with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"File cleaned and saved as {output_file}")

if __name__ == '__main__':
    print("Cleaning app.py encoding issues...")
    clean_file('app.py', 'app_cleaned.py')
    print("Done! Try running: python app_cleaned.py")