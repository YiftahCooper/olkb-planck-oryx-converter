#pragma once

/*
 * Adjust Tapping Term for Tap Danc and Mod Taps.
 * Oryx defaults usually hover around 175-200ms.
 */
#define TAPPING_TERM 200

/*
 * Mouse Keys settings to make them feel more natural (Oryx-like)
 */
#define MOUSEKEY_INTERVAL 16
#define MOUSEKEY_DELAY 0
#define MOUSEKEY_TIME_TO_MAX 60
#define MOUSEKEY_MAX_SPEED 7
#define MOUSEKEY_WHEEL_DELAY 0

/*
 * Enable/Disable audio features
 */
#ifdef AUDIO_ENABLE
    #define STARTUP_SONG SONG(PLANCK_SOUND)
    #define AUDIO_CLICKY
#endif

/*
 * Combo Count
 */
#define COMBO_COUNT 0 // Disable combos if not used
