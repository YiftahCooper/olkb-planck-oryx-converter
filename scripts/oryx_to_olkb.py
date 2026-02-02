import re
import sys
import os

# Configuration
INPUT_FILE = "zsa_oryx_source/keymap.c"
OUTPUT_FILE = "olkb_firmware/keymap.c"

def parse_zsa_layers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return []

    # Extract keymaps array using regex
    match = re.search(r'keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]\s*=\s*\{([\s\S]*?)\};', content)
    if not match:
        print("Error: Could not find keymaps array in input file.")
        return []
    
    raw_layers_content = match.group(1)

    # Find individual layers (handles named layers like [_BASE])
    layer_matches = re.findall(r'\[([^\]]+)\]\s*=\s*LAYOUT_\w+\(([\s\S]*?)\)', raw_layers_content)

    layers = []
    for layer_name, layer_content in layer_matches:
        # Clean up the content
        clean_content = re.sub(r'//.*', '', layer_content) # Strip comments
        clean_content = re.sub(r'\s+', '', clean_content)  # Remove whitespace
        keys = clean_content.split(',')
        keys = [k for k in keys if k] # Filter empty strings
        layers.append((layer_name, keys))
    
    return layers

def transpose_to_olkb_matrix(keys):
    # Handle MIT layout (47 keys with 2u spacebar)
    if len(keys) == 47:
        keys.insert(41, keys[41]) 

    # Initialize 8x6 matrix with KC_NO
    matrix = [['KC_NO' for _ in range(6)] for _ in range(8)]

    for i in range(48):
        if i >= len(keys): break
        keycode = keys[i]

        # Calculate visual position (4x12 grid)
        visual_row = i // 12
        visual_col = i % 12

        # Transpose Logic: Split keyboard in half
        # Left half (cols 0-5) -> Rows 0-3
        # Right half (cols 6-11) -> Rows 4-7
        if visual_col < 6:
            target_row = visual_row
            target_col = visual_col
        else:
            target_row = visual_row + 4
            target_col = visual_col - 6
            
        matrix[target_row][target_col] = keycode

    return matrix

def generate_keymap_c(layers):
    output = []
    output.append('#include QMK_KEYBOARD_H')
    output.append('')
    output.append('const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {')

    for index, (layer_name, keys) in enumerate(layers):
        matrix = transpose_to_olkb_matrix(keys)
        
        output.append(f'    [{layer_name}] = {{ // Converted from {layer_name}')
        
        for r_idx, row in enumerate(matrix):
            row_str = ", ".join(f"{k:<7}" for k in row)
            label = f"// L{r_idx}" if r_idx < 4 else f"// R{r_idx-4}"
            output.append(f'        {{ {row_str} }}, {label}')
        
        output.append('    },')

    output.append('};')
    return "\n".join(output)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        print("Place your ZSA 'keymap.c' in the 'zsa_oryx_source' folder.")
        sys.exit(1)

    print(f"Reading from {INPUT_FILE}...")
    layers = parse_zsa_layers(INPUT_FILE)
    
    if not layers:
        print("No layers found or parse error.")
        sys.exit(1)

    print(f"Found {len(layers)} layers. Converting...")
    c_code = generate_keymap_c(layers)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(c_code)
        
    print(f"Success! Transposed keymap saved to {OUTPUT_FILE}")
    print("NOTE: Manually copy Tap Dance definitions, custom keycodes, and macros from the ZSA file.")

if __name__ == "__main__":
    main()
