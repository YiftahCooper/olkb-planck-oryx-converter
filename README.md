# OLKB Planck Oryx Converter

This repository contains tools to convert ZSA Oryx source code to firmware compatible with the OLKB Planck Rev 6 (and 6.1) keyboard.

## Problem Statement
The OLKB Planck Rev 6 uses a "folded" electrical matrix (8 rows x 6 columns) which is fundamentally different from the visual 4x12 grid layout. ZSA Oryx exports code assuming a linear 4x12 layout, which causes keys to be scrambled when flashed directly to an OLKB board.

## Solution
The script `scripts/oryx_to_olkb.py` automatically transposes the keymap matrix:
1. Parses the ZSA `keymap.c`.
2. Splits the 4x12 visual grid into two 4x6 halves.
3. Maps the Left Half to Matrix Rows 0-3.
4. Maps the Right Half to Matrix Rows 4-7.
5. Generates a new `keymap.c` that works correctly on the OLKB hardware.

## Usage

1. **Export from Oryx**: Download the source code for your layout from ZSA Oryx.
2. **Place Source**: Copy the `keymap.c` file from the download into the `zsa_oryx_source/` folder.
3. **Run Script**:
   ```bash
   python3 scripts/oryx_to_olkb.py
   ```
4. **Flash**: Use the generated file in `olkb_firmware/keymap.c` to compile and flash your firmware (using QMK or Vial).

## Manual Steps Required
The script handles the keymap transposition perfectly, but you must manually copy these sections from your ZSA source to the output file if you use them:
- `enum custom_keycodes`
- `enum tap_dance_codes`
- `tap_dance_actions[]`
- Macros and `process_record_user` functions

## Credits
Based on the "Comprehensive Report: Resolving Vial Layout Rendering Issues and ZSA-to-OLKB Firmware Conversion for Planck Rev 6".