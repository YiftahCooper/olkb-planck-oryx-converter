import re
import sys
import os

# Configuration
INPUT_FILE = "zsa_oryx_source/keymap.c"
OUTPUT_FILE = "olkb_firmware/keymap.c"

def split_keycodes(content):
    """
    Splits a string of comma-separated keycodes while respecting nested parentheses.
    Example: "KC_A, MT(MOD_LSFT, KC_Z), KC_B" -> ["KC_A", "MT(MOD_LSFT, KC_Z)", "KC_B"]
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
            # Split point found
            key_str = "".join(current_key).strip()
            if key_str:
                keys.append(key_str)
            current_key = []
        else:
            current_key.append(char)
            
    # Append last key
    key_str = "".join(current_key).strip()
    if key_str:
        keys.append(key_str)
        
    return keys

def parse_zsa_layers(content: str):
    """Parse the ZSA keymaps array and extract per-layer 4x12 key lists."""
    match = re.search(
        r"keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]\s*=\s*\{([\s\S]*?)\};",
        content,
    )
    if not match:
        print("Error: Could not find keymaps array in input file.")
        return []

    raw_layers_content = match.group(1)

    # Find individual layers (handles named layers like [_BASE])
    layer_matches = re.findall(
        r"\[([^\]]+)\]\s*=\s*LAYOUT_\w+\(([\s\S]*?)\)",
        raw_layers_content,
    )

    layers = []
    for layer_name, layer_content in layer_matches:
        # Clean up the content
        clean_content = re.sub(r"//.*", "", layer_content)  # Strip comments
        clean_content = re.sub(r"\s+", " ", clean_content) # Normalize whitespace to single spaces
        
        # Use robust splitter instead of simple string split
        keys = split_keycodes(clean_content)
        
        layers.append((layer_name, keys))

    return layers


def transpose_to_olkb_matrix(keys):
    """Convert a 48-key 4x12 visual layout into an 8x6 OLKB Planck Rev 6 matrix.
    
    This preserves VIAL CAPABILITY by creating the raw matrix structure 
    that matches the split-matrix hardware of the Rev 6.
    Left half (cols 0-5)  -> rows 0-3
    Right half (cols 6-11) -> rows 4-7
    """
    # Handle MIT layout (47 keys with 2u spacebar)
    if len(keys) == 47:
        keys.insert(41, keys[41])

    # Initialize 8x6 matrix with KC_NO
    matrix = [["KC_NO" for _ in range(6)] for _ in range(8)]

    for i in range(48):
        if i >= len(keys):
            break
        keycode = keys[i]

        # Calculate visual position (4x12 grid)
        visual_row = i // 12
        visual_col = i % 12

        # Transpose logic for split matrix
        if visual_col < 6:
            # Left half
            target_row = visual_row
            target_col = visual_col
        else:
            # Right half, shifted down by 4 rows
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

    # Build the new keymaps block
    new_keymaps_block = generate_keymaps_block(layers)

    # Replace the original keymaps block
    full_pattern = (
        r"const\s+uint16_t\s+PROGMEM\s+keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]"
        r"\s*=\s*\{[\s\S]*?\};"
    )
    if not re.search(full_pattern, content):
        print("Error: Could not replace keymaps array in input file.")
        sys.exit(1)

    new_content = re.sub(full_pattern, new_keymaps_block, content, count=1)

    # FIX: Comment out ZSA-specific headers that break OLKB/Vial builds
    new_content = re.sub(r'(#include "version.h")', r'// \1', new_content)
    new_content = re.sub(r'(#include "zsa.h")', r'// \1', new_content)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"// Converted by oryx_to_olkb.py\n// Retains Vial/OLKB Matrix Compatibility\n{new_content}")

    print(f"Success! Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
