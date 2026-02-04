#!/usr/bin/env python3
"""
ZSA Oryx to OLKB Planck Rev6 Vial Keymap Converter
Converts ZSA Oryx keymap exports to QMK-compatible Planck Rev6 keymaps with Vial support.
"""
import re
import os
import sys

# Configuration
INPUT_FILE = "zsa_oryx_source/keymap.c"
OUTPUT_DIR = "olkb_firmware"
OUTPUT_KEYMAP = os.path.join(OUTPUT_DIR, "keymap.c")
OUTPUT_RULES = os.path.join(OUTPUT_DIR, "rules.mk")
OUTPUT_CONFIG = os.path.join(OUTPUT_DIR, "config.h")
OUTPUT_VIAL_JSON = os.path.join(OUTPUT_DIR, "vial.json")

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
    counting parentheses to extract the full layer definition.
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

def comment_out_function(content, function_name):
    """
    Robustly comments out a function by finding its start and 
    matching braces to find the end, then wrapping in #if 0 ... #endif.
    Using C-style comments /* */ caused nesting issues.
    """
    # Find the function definition start: void function_name ... {
    pattern = re.compile(r"void\s+" + re.escape(function_name) + r"\s*\([^)]*\)\s*\{")
    match = pattern.search(content)
    
    if not match:
        return content
        
    start_idx = match.start()
    open_brace_idx = match.end() - 1
    
    # Verify the last char is indeed '{'
    if content[open_brace_idx] != '{':
        print(f"Warning: parsing error locating start of {function_name}")
        return content

    # Walk forward from open brace to find matching close brace
    depth = 1
    i = open_brace_idx + 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    
    end_idx = i
    
    # extract the full block
    full_function = content[start_idx:end_idx]
    
    # wrap in preprocessor directive instead of comments
    commented_function = "\n#if 0 // Disabled by oryx_to_olkb\n" + full_function + "\n#endif\n"
    
    # replace in content
    new_content = content[:start_idx] + commented_function + content[end_idx:]
    
    return new_content

def parse_zsa_layers(content: str):
    """Parse the ZSA keymaps array and extract per-layer 4x12 key lists."""
    
    match = re.search(
        r"keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\]\s*=\s*\{",
        content,
    )
    if not match:
        print("Error: Could not find keymaps array start in input file.")
        return []

    search_start = match.end()
    layer_start_pattern = re.compile(r"\[([^\]]+)\]\s*=\s*LAYOUT_\w+\(")
    
    layers = []
    
    for match in layer_start_pattern.finditer(content, search_start):
        layer_name = match.group(1)
        content_start_index = match.end()
        
        raw_layer_content = extract_layer_content(content, content_start_index)
        
        clean_content = re.sub(r"//.*", "", raw_layer_content)
        clean_content = clean_content.replace("\n", " ").replace("\r", "")
        
        keys = split_keycodes(clean_content)
        
        if len(keys) < 47:
             print(f"Warning: Layer {layer_name} has only {len(keys)} keys. Check parsing logic.")

        layers.append((layer_name, keys))

    return layers


def transpose_to_olkb_matrix(keys):
    """Convert a 48-key 4x12 visual layout into an 8x6 OLKB Planck Rev 6 matrix."""
    current_keys = list(keys)

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

def generate_rules_mk(output_path):
    """
    Generate rules.mk with complete Vial and feature support.
    UPDATED: Disables LTO, COMBO, KEY_OVERRIDE to prevent compilation errors.
    """
    rules_content = """# Generated by oryx_to_olkb.py
# Planck Rev6 Vial Keymap Build Rules

# Vial support (dynamic remapping GUI)
VIAL_ENABLE = yes
DYNAMIC_KEYMAP_ENABLE = yes

# Tap dance support (required for TD() keycodes)
TAP_DANCE_ENABLE = yes

# Disable Vial's built-in tap dance (using QMK's native implementation from keymap.c)
VIAL_TAP_DANCE_ENABLE = no

# Audio support (Planck Rev6 has speaker/buzzer)
AUDIO_ENABLE = yes

# Music mode support (for encoder and audio features)
MUSIC_ENABLE = yes

# Link-Time Optimization (Disabled to prevent type mismatch errors with Vial)
LTO_ENABLE = no

# Introspection fix (Disabled to prevent conflicts with Vial's internal definitions)
COMBO_ENABLE = no
KEY_OVERRIDE_ENABLE = no
"""
    with open(output_path, 'w') as f:
        f.write(rules_content)

    print(f" ✓ Generated rules.mk")

def generate_config_h(output_path):
    """
    Generate config.h with Vial UID and unlock combo.
    """
    config_content = """#pragma once

/* Vial Configuration for Planck Rev6 */

/* 1. Vial UID - Unique identifier for this keyboard in Vial app */
/* Change the last byte (0x77) to force a layout reset if needed */
#define VIAL_KEYBOARD_UID {0x89, 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45, 0x77}

/* 2. Unlock Combo - Press these keys simultaneously to unlock Vial editing */
/* Top-Left: Esc at (0,0) and Top-Right: Backspace at (4,5) */
/* Planck matrix: Left half = rows 0-3, Right half = rows 4-7, Cols = 0-5 */
#define VIAL_UNLOCK_COMBO_ROWS { 0, 4 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 5 }
"""
    with open(output_path, 'w') as f:
        f.write(config_content)

    print(f" ✓ Generated config.h")

def generate_vial_json(output_path):
    """
    Generate vial.json definition file for sideloading.
    """
    vial_json_content = """{
  "name": "Planck Rev6",
  "vendorId": "0x03A8",
  "productId": "0xA4F9",
  "lighting": "none",
  "matrix": {
    "rows": 8,
    "cols": 6
  },
  "layouts": {
    "keymap": [
      [{"y":0,"x":0},"0,0",{"x":1},"0,1",{"x":2},"0,2",{"x":3},"0,3",{"x":4},"0,4",{"x":5},"0,5",{"x":6},"4,0",{"x":7},"4,1",{"x":8},"4,2",{"x":9},"4,3",{"x":10},"4,4",{"x":11},"4,5"],
      [{"y":1,"x":0},"1,0",{"x":1},"1,1",{"x":2},"1,2",{"x":3},"1,3",{"x":4},"1,4",{"x":5},"1,5",{"x":6},"5,0",{"x":7},"5,1",{"x":8},"5,2",{"x":9},"5,3",{"x":10},"5,4",{"x":11},"5,5"],
      [{"y":2,"x":0},"2,0",{"x":1},"2,1",{"x":2},"2,2",{"x":3},"2,3",{"x":4},"2,4",{"x":5},"2,5",{"x":6},"6,0",{"x":7},"6,1",{"x":8},"6,2",{"x":9},"6,3",{"x":10},"6,4",{"x":11},"6,5"],
      [{"y":3,"x":0},"3,0",{"x":1},"3,1",{"x":2},"3,2",{"x":3},"3,3",{"x":4},"3,4",{"x":5},"3,5",{"x":6},"7,0",{"x":7},"7,1",{"x":8},"7,2",{"x":9},"7,3",{"x":10},"7,4",{"x":11},"7,5"]
    ]
  }
}"""
    with open(output_path, 'w') as f:
        f.write(vial_json_content)
        
    print(f" ✓ Generated vial.json")

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
    new_content = re.sub(r'(#include "muse.h")', r'// \1', new_content)
    
    # FIX: Update layer_state_set_user signature for modern QMK
    new_content = re.sub(
        r'(?:uint8_t|uint32_t|layer_state_t)\s+layer_state_set_user\s*\(\s*(?:uint8_t|uint32_t|layer_state_t)\s+state\s*\)',
        r'layer_state_t layer_state_set_user(layer_state_t state)',
        new_content
    )

    # FIX: Robustly disable matrix_scan_user using preprocessor directive #if 0
    if "muse_clock_pulse" in new_content or "matrix_scan_user" in new_content:
        print("Disabling matrix_scan_user to prevent Vial conflicts...")
        new_content = comment_out_function(new_content, "matrix_scan_user")
        new_content = re.sub(r'(void\s+matrix_scan_user\s*\([^)]*\)\s*;)', r'// \1', new_content)

    # FIX: Wrap tap_dance_actions in #ifndef VIAL_ENABLE
    # This ensures Vial can take ownership of tap dances when enabled
    if "tap_dance_actions[]" in new_content:
        print("Wrapping tap_dance_actions in #ifndef VIAL_ENABLE...")
        tap_dance_pattern = r"(tap_dance_action_t\s+tap_dance_actions\[\]\s*=\s*\{[\s\S]*?\};)"
        replacement = "#ifndef VIAL_ENABLE\\n\\1\\n#endif"
        new_content = re.sub(tap_dance_pattern, replacement, new_content)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_KEYMAP, "w", encoding="utf-8") as f:
        f.write(f"// Converted by oryx_to_olkb.py\\n// Retains Vial/OLKB Matrix Compatibility\\n{new_content}")
    print(f" ✓ Generated keymap.c")

    # Generate rules.mk
    generate_rules_mk(OUTPUT_RULES)

    # Generate config.h
    generate_config_h(OUTPUT_CONFIG)
    
    # Generate vial.json
    generate_vial_json(OUTPUT_VIAL_JSON)

    print("\n" + "=" * 50)
    print(" SUCCESS! Generated 4 files in 'olkb_firmware/':")
    print(" - keymap.c")
    print(" - rules.mk")
    print(" - config.h")
    print(" - vial.json")
    print("\n" + "=" * 50)
    print(" ACTION REQUIRED:")
    print(" 1. Copy 'keymap.c', 'rules.mk', 'config.h' to your QMK keymap folder:")
    print("    cp olkb_firmware/*.c olkb_firmware/*.mk olkb_firmware/*.h qmk_firmware/keyboards/planck/keymaps/vial/")
    print(" 2. Sideload 'vial.json' in the Vial app if automatic detection fails.")
    print("\n Then compile with:")
    print(" qmk compile -kb planck/rev6 -km vial")
    print("=" * 50)

if __name__ == "__main__":
    main()