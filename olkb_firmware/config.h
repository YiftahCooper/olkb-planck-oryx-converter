#pragma once

/* Vial Configuration for Planck Rev6 */

/* 1. Vial UID - Unique identifier for this keyboard in Vial app */
/* Change the last byte (0x77) to force a layout reset if needed */
#define VIAL_KEYBOARD_UID {0x89, 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45, 0x77}

/* 2. Unlock Combo - Press these keys simultaneously to unlock Vial editing */
/* Top-Left: Esc at (0,0) and Top-Right: Backspace at (4,5) */
/* Planck matrix: Left half = rows 0-3, Right half = rows 4-7, Cols = 0-5 */
#define VIAL_UNLOCK_COMBO_ROWS { 0, 4 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 5 }

/* 3. Explicitly disable Vial's Tap Dance to avoid linker conflicts */
#define VIAL_TAP_DANCE_ENABLE 0
