import re
import sys
import os

# Configuration
INPUT_FILE = "zsa_oryx_source/keymap.c"
OUTPUT_FILE = "olkb_firmware/keymap.c"

def split_keycodes(content):
    """
    Splits a string of comma-separated keycodes while respecting nested parentheses.
    """
    keys = []
    current_key = []
    depth = 0
    
    for char in content:
        if char == '(':
            depth += 1
            current_key.append(char)
        elif char == ')':
            depth -= 1
            current_key.append(char)
        elif char == ',' and depth == 0:
            key_str = "".join(current_key).strip()
            if key_str:
                keys.append(key_str)
            current_key = []
        else:
            current_key.append(char)
            
    key_str = "".join(current_key).strip()
    if key_str:
        keys.append(key_str)
        
    return keys

def extract_layer_content(full_text, start_index):
    """
    Starting from the character AFTER 'LAYOUT_xxx(', walk forward 
    counting parentheses to extract the full layer definition 
    handling nested macros correctly.
    """
    content = []
    depth = 1 # We started after the first '('
    i = start_index
    
    while i < len(full_text) and depth > 0:
        char = full_text[i]
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        
        if depth > 0:
            content.append(char)
        i += 1
    
    return "".join(content)

def parse_zsa_layers(content: str):
    """Parse the ZSA keymaps array and extract per-layer 4x12 key lists."""
    
    # Locate the main keymaps array block
    match = re.search(
        r"keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]\s*=\s*\{",
        content,
    )
    if not match:
        print("Error: Could not find keymaps array start in input file.")
        return []

    # Start searching for layers AFTER the keymaps array starts
    search_start = match.end()
    
    # Regex to find the START of a layer definition: [NAME] = LAYOUT_xxx(
    # We purposefully do NOT try to capture the end here.
    layer_start_pattern = re.compile(r"\[([^\]]+)\]\s*=\s*LAYOUT_\w+\(")
    
    layers = []
    
    # Iterate over all layer starts found in the file
    for match in layer_start_pattern.finditer(content, search_start):
        layer_name = match.group(1)
        content_start_index = match.end()
        
        # Use robust parser to get the full content until matching ')'
        raw_layer_content = extract_layer_content(content, content_start_index)
        
        # Clean up
        clean_content = re.sub(r"//.*", "", raw_layer_content)  # Strip comments
        clean_content = clean_content.replace("\n", " ").replace("\r", "")
        
        keys = split_keycodes(clean_content)
        
        # Validation
        if len(keys) < 47:
             print(f"Warning: Layer {layer_name} has only {len(keys)} keys. Check parsing logic.")

        layers.append((layer_name, keys))

    return layers


def transpose_to_olkb_matrix(keys):
    """Convert a 48-key 4x12 visual layout into an 8x6 OLKB Planck Rev 6 matrix."""
    current_keys = list(keys)

    # Handle MIT layout (47 keys with 2u spacebar)
    if len(current_keys) == 47:
        current_keys.insert(41, current_keys[41])
    elif len(current_keys) < 47:
        while len(current_keys) < 48:
            current_keys.append("KC_NO")

    matrix = [["KC_NO" for _ in range(6)] for _ in range(8)]

    for i in range(48):
        if i >= len(current_keys):
            break
        keycode = current_keys[i]

        visual_row = i // 12
        visual_col = i % 12

        if visual_col < 6:
            target_row = visual_row
            target_col = visual_col
        else:
            target_row = visual_row + 4
            target_col = visual_col - 6

        matrix[target_row][target_col] = keycode

    return matrix


def generate_keymaps_block(layers):
    """Generate the full const keymaps block for the OLKB matrix."""
    output = []
    output.append("const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {")

    for layer_name, keys in layers:
        matrix = transpose_to_olkb_matrix(keys)

        output.append(f"    [{layer_name}] = {{ // Converted from {layer_name}")

        for r_idx, row in enumerate(matrix):
            row_str = ", ".join(f"{k:<7}" for k in row)
            label = f"// L{r_idx}" if r_idx < 4 else f"// R{r_idx-4}"
            output.append(f"        {{ {row_str} }}, {label}")

        output.append("    },")

    output.append("};")
    return "\n".join(output)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        print("Place your ZSA 'keymap.c' in the 'zsa_oryx_source' folder.")
        sys.exit(1)

    print(f"Reading from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    layers = parse_zsa_layers(content)
    if not layers:
        print("No layers found or parse error.")
        sys.exit(1)

    print(f"Found {len(layers)} layers. Converting keymaps...")

    new_keymaps_block = generate_keymaps_block(layers)

    full_pattern = (
        r"const\s+uint16_t\s+PROGMEM\s+keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]"
        r"\s*=\s*\{[\s\S]*?\};"
    )
    if not re.search(full_pattern, content):
        print("Error: Could not replace keymaps array in input file.")
        sys.exit(1)

    new_content = re.sub(full_pattern, new_keymaps_block, content, count=1)

    # FIX: Comment out ZSA-specific headers
    new_content = re.sub(r'(#include "version.h")', r'// \1', new_content)
    new_content = re.sub(r'(#include "zsa.h")', r'// \1', new_content)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"// Converted by oryx_to_olkb.py\n// Retains Vial/OLKB Matrix Compatibility\n{new_content}")

    print(f"Success! Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
