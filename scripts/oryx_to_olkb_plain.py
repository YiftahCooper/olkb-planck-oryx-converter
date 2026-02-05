#!/usr/bin/env python3
"""
oryx_to_olkb_plain.py

Converts a ZSA Oryx keymap.c (Planck EZ / Moonlander / etc.) into a clean QMK keymap.c 
for the OLKB Planck Rev6, using LAYOUT_planck_grid(48 keys).

It strips ZSA-specific headers and modernizes function signatures for current QMK.
"""

import argparse
import re
from pathlib import Path
import sys

# Locate the start of the keymaps array
KEYMAP_RE = re.compile(
    r"const\s+uint16_t\s+PROGMEM\s+keymaps\s*\[\]\s*\[\s*MATRIX_ROWS\s*\]\s*\[\s*MATRIX_COLS\s*\]\s*=\s*\{",
    re.MULTILINE,
)

def find_matching_brace(text: str, start_idx: int) -> int:
    """Find the closing brace } matching the brace at text[start_idx]."""
    depth = 0
    for i in range(start_idx, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Unmatched '{' while locating keymaps block.")

def split_top_level_commas(s: str):
    """Split string by commas, ignoring commas inside (), [], {}."""
    out, buf = [], []
    depth_paren = 0
    depth_brack = 0
    depth_brace = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "(":
            depth_paren += 1
        elif c == ")":
            depth_paren -= 1
        elif c == "[":
            depth_brack += 1
        elif c == "]":
            depth_brack -= 1
        elif c == "{":
            depth_brace += 1
        elif c == "}":
            depth_brace -= 1

        if c == "," and depth_paren == 0 and depth_brack == 0 and depth_brace == 0:
            item = "".join(buf).strip()
            if item:
                out.append(item)
            buf = []
        else:
            buf.append(c)
        i += 1

    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out

def extract_layout_args(call_text: str):
    """Parse LAYOUT_xxx(...) and return the list of keycode arguments."""
    open_paren = call_text.find("(")
    if open_paren < 0:
        raise ValueError("Layout call missing '('")
    
    # walk to matching ')'
    depth = 0
    for i in range(open_paren, len(call_text)):
        if call_text[i] == "(":
            depth += 1
        elif call_text[i] == ")":
            depth -= 1
            if depth == 0:
                inside = call_text[open_paren + 1 : i]
                return split_top_level_commas(inside)
    raise ValueError("Unmatched '(' in layout call")

def convert_keymaps_block(block_text: str, target_layout="LAYOUT_planck_grid"):
    """
    Finds every [LAYER] = LAYOUT_xxx(...) entry and rewrites it to target_layout(...) 
    formatted as a 4x12 grid.
    """
    
    # Regex to capture one layer assignment: [NAME] = LAYOUT_xxx( ...args... ),
    # We use a non-greedy .*? inside the parens, but relies on python logic to actually parse args correctly
    # because regex recursive matching is hard.
    # Instead, we'll just find the start, then parse manually.

    layer_start_re = re.compile(r"(\[\s*[^]]+\s*\]\s*=\s*)(LAYOUT_[A-Za-z0-9_]+)\s*\(", re.MULTILINE)
    
    # We rebuild the string piece by piece
    output_parts = []
    last_idx = 0
    
    for m in layer_start_re.finditer(block_text):
        # Text before this match
        output_parts.append(block_text[last_idx:m.start()])
        
        prefix = m.group(1) # [LAYER] = 
        layout_name = m.group(2) # LAYOUT_planck_grid
        
        # Now define the full call starting from where LAYOUT_... started
        start_call = m.start(2)
        
        # Find the end of this function call by brace counting
        depth = 0
        end_call = -1
        for i in range(m.end() - 1, len(block_text)): # start at the '('
            if block_text[i] == '(':
                depth += 1
            elif block_text[i] == ')':
                depth -= 1
                if depth == 0:
                    end_call = i + 1
                    break
        
        if end_call == -1:
             raise ValueError(f"Could not find closing ')' for layer starting at {m.start()}")
        
        full_call = block_text[start_call:end_call]
        args = extract_layout_args(full_call)
        
        if len(args) == 47:
            # Oryx/ZSA sometimes exports 47 keys for Planck (missing the 2u spacebar dupe or MIT layout?)
            # Planck Grid requires 48. We usually double the 41st key (Space) or add NO.
            # But let's check if it's MIT (47 keys) vs Grid (48 keys).
            # If target is planck_grid, we need 48.
            print("Warning: Layer has 47 keys. Duplicating key #41 (Space?) to fill 48-key grid.")
            args.insert(41, args[41]) 

        if len(args) != 48:
             print(f"ERROR: Layer {prefix.strip()} has {len(args)} keys, but Planck Grid requires 48.")
             # We won't abort, but the compile will likely fail or layout will be shifted.
        
        # Format cleanly: 4 rows of 12
        rows = []
        for r in range(0, 48, 12):
            row_keys = args[r : r+12]
            # pad shorter rows if needed (shouldn't happen if len=48)
            rows.append(", ".join(row_keys))
        
        rendered_args = ",\n    ".join(rows)
        
        new_layer = f"{prefix}{target_layout}(\n    {rendered_args}\n)"
        output_parts.append(new_layer)
        
        last_idx = end_call
    
    output_parts.append(block_text[last_idx:])
    return "".join(output_parts)

def patch_source_code(text: str) -> str:
    """Fix common incompatibilities between Oryx export and standard QMK."""
    
    # 1. Update layer_state_set_user signature
    text = re.sub(
        r"uint8_t\s+layer_state_set_user\s*\(\s*uint8_t\s+state\s*\)",
        "layer_state_t layer_state_set_user(layer_state_t state)",
        text
    )
    
    # 2. Fix ZSA_SAFE_RANGE ifdef mess (simplify it)
    if "SAFE_RANGE" in text and "ZSA_SAFE_RANGE" not in text:
        pass # standard
    else:
        # Oryx defines enum custom_keycodes { ... = ZSA_SAFE_RANGE }
        # We just want QMK's SAFE_RANGE
        text = text.replace("ZSA_SAFE_RANGE", "SAFE_RANGE")

    # 3. Comment out ZSA includes that don't exist in standard QMK
    text = re.sub(r'(#include "zsa.h")', r'// \1', text)
    text = re.sub(r'(#include "version.h")', r'// \1', text)

    # 4. Remove duplicate definitions if Oryx includes them
    # (Sometimes Oryx defines LOWER/RAISE/ADJUST macros that conflict with user code)
    
    return text

def main():
    input_file = "zsa_oryx_source/keymap.c"
    output_file = "olkb_firmware_plain/keymap.c"
    
    print(f"Reading {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    # 1. Parse and replace the keymaps[] block
    m = KEYMAP_RE.search(src)
    if not m:
        print("Error: Could not find keymaps[] definition.")
        sys.exit(1)
        
    brace_start = src.find("{", m.end() - 1)
    brace_end = find_matching_brace(src, brace_start)
    
    # Extract original block including braces
    keymaps_block = src[brace_start : brace_end + 1]
    
    # Convert it
    new_block = convert_keymaps_block(keymaps_block, target_layout="LAYOUT_planck_grid")
    
    # Reassemble file
    new_src = src[:brace_start] + new_block + src[brace_end + 1 :]
    
    # 2. Apply other patches
    new_src = patch_source_code(new_src)
    
    # 3. Write output
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"// Converted from Oryx to QMK Planck Grid\n{new_src}")
    
    print(f"Success! Wrote converted keymap to {output_file}")
    print("\nNext steps:")
    print("1. cp olkb_firmware_plain/keymap.c qmk_firmware/keyboards/planck/keymaps/YOUR_KEYMAP/")
    print("2. qmk compile -kb planck/rev6 -km YOUR_KEYMAP")

if __name__ == "__main__":
    main()