# OLKB Planck Oryx Converter

This repository contains tools to convert ZSA Oryx source code to firmware compatible with the OLKB Planck Rev 6 (and 6.1) keyboard, with full **Vial** support.

## Problem Statement
The OLKB Planck Rev 6 uses a "folded" electrical matrix (8 rows x 6 columns) which is fundamentally different from the visual 4x12 grid layout. ZSA Oryx exports code assuming a linear 4x12 layout, which causes keys to be scrambled when flashed directly to an OLKB board. Additionally, standard ZSA exports lack the necessary configuration for Vial (dynamic remapping).

## Solution
The script `scripts/oryx_to_olkb.py` automatically:
1. **Transposes the Matrix**: Splits the 4x12 visual grid into two 4x6 halves and maps them to the correct Planck Rev 6 matrix rows.
2. **Preserves Logic**: Retains your macros, tap dances, and custom keycodes from the Oryx export.
3. **Enables Vial**: Generates `rules.mk` and `config.h` with the required settings (`VIAL_ENABLE`, `VIAL_KEYBOARD_UID`, unlock combos) to make the keyboard detected by the Vial app.
4. **Fixes Conflicts**: Automatically handles conflicts between ZSA's `muse` audio/matrix scanning and Vial's requirements.

## Usage

1. **Export from Oryx**: Download the source code for your layout from ZSA Oryx.
2. **Place Source**: Copy the `keymap.c` file from the download into the `zsa_oryx_source/` folder.
3. **Run Script**:
   ```bash
   python3 scripts/oryx_to_olkb.py
   ```
4. **Deploy**: The script generates 3 files in `olkb_firmware/`:
   - `keymap.c` (Converted keymap)
   - `rules.mk` (Build rules with Vial & Audio enabled)
   - `config.h` (Vial configuration)

   Copy **all 3 files** to your QMK directory:
   ```
   qmk_firmware/keyboards/planck/keymaps/vial/
   ```

5. **Compile**:
   ```bash
   qmk compile -kb planck/rev6 -km vial
   ```

## Features
- **Matrix Transposition**: 8x2 (ZSA) → 8x6 (Planck Rev 6).
- **Vial Support**: Generates valid UID and unlock combo (Top-Left + Top-Right keys).
- **Audio Enabled**: Enables `AUDIO_ENABLE` and `MUSIC_ENABLE` by default.
- **Optimization**: Enables `LTO_ENABLE` to save firmware size.
- **Conflict Resolution**: Safely disables `matrix_scan_user` to prevent build errors.

## Credits
Based on the "Comprehensive Report: Resolving Vial Layout Rendering Issues and ZSA-to-OLKB Firmware Conversion for Planck Rev 6".
