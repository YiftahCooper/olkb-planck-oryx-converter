import re
import sys
import os

# Configuration
INPUT_FILE = "zsa_oryx_source/keymap.c"
OUTPUT_FILE = "olkb_firmware/keymap.c"


def parse_zsa_layers(content: str):
    """Parse the ZSA keymaps array and extract per-layer 4x12 key lists.

    This looks for:
        keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
            [_BASE] = LAYOUT_planck_grid(...),
            ...
        };
    and returns a list of (layer_name, [keys...]).
    """
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
        clean_content = re.sub(r"\s+", "", clean_content)  # Remove whitespace
        keys = clean_content.split(",")
        keys = [k for k in keys if k]  # Filter empty strings
        layers.append((layer_name, keys))

    return layers


def transpose_to_olkb_matrix(keys):
    """Convert a 48-key 4x12 visual layout into an 8x6 OLKB Planck Rev 6 matrix.

    Left half (cols 0-5)  -> rows 0-3
    Right half (cols 6-11) -> rows 4-7
    """
    # Handle MIT layout (47 keys with 2u spacebar)
    if len(keys) == 47:
        # Duplicate the spacebar position so we still have a 4x12 grid
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
    """Generate the full const keymaps block for the OLKB matrix.

    This intentionally only emits the keymaps array; all other code
    (custom keycodes, tap dances, macros, process_record_user, etc.)
    is preserved from the original file.
    """
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

    # Replace the original keymaps block in the full source, preserving
    # everything else: enums, tap dances, macros, process_record_user, etc.
    full_pattern = (
        r"const\s+uint16_t\s+PROGMEM\s+keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]"
        r"\s*=\s*\{[\s\S]*?\};"
    )
    if not re.search(full_pattern, content):
        print("Error: Could not replace keymaps array in input file.")
        sys.exit(1)

    new_content = re.sub(full_pattern, new_keymaps_block, content, count=1)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Success! Transposed keymap (with all enums/macros/functions preserved) saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
