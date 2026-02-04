#include QMK_KEYBOARD_H
#ifdef AUDIO_ENABLE
// #include "muse.h"
#endif
#include "eeprom.h"
#ifndef ZSA_SAFE_RANGE
#define ZSA_SAFE_RANGE SAFE_RANGE
#endif

enum custom_keycodes {
  RGB_SLD = ZSA_SAFE_RANGE,
};


enum tap_dance_codes {
  DANCE_0,
  DANCE_1,
  DANCE_2,
  DANCE_3,
  DANCE_4,
  DANCE_5,
  DANCE_6,
};

enum planck_layers {
  _BASE,
  _LOWER,
  _RAISE,
  _ADJUST,
};

#define LOWER MO(_LOWER)
#define RAISE MO(_RAISE)

#define DUAL_FUNC_0 LT(5, KC_D)

#define LOWER MO(_LOWER)
#define RAISE MO(_RAISE)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = { // Converted from _BASE
        { KC_TAB , KC_Q   , KC_W   , KC_E   , KC_R   , KC_T    }, // L0
        { TD(DANCE_0), KC_A   , KC_S   , KC_D   , KC_F   , KC_G    }, // L1
        { DUAL_FUNC_0, KC_Z   , KC_X   , KC_C   , KC_V   , KC_B    }, // L2
        { LSFT(KC_LEFT_ALT), KC_TRANSPARENT, KC_LEFT_GUI, TD(DANCE_3), MT(MOD_LSFT, KC_BSLS), TD(DANCE_4) }, // L3
        { KC_Y   , KC_U   , KC_I   , KC_O   , KC_P   , KC_ESCAPE }, // R0
        { KC_H   , KC_J   , KC_K   , KC_L   , KC_SCLN, TT(1)   }, // R1
        { KC_N   , KC_M   , KC_COMMA, KC_DOT , TD(DANCE_1), TD(DANCE_2) }, // R2
        { KC_NO  , TD(DANCE_5), TD(DANCE_6), MT(MOD_RSFT, KC_QUOTE), MT(MOD_RCTL, KC_SLASH), KC_EQUAL }, // R3
    },
    [_LOWER] = { // Converted from _LOWER
        { KC_TILD, KC_1   , KC_2   , KC_3   , KC_4   , KC_5    }, // L0
        { KC_DELETE, KC_HOME, KC_UP  , KC_END , KC_PAGE_UP, KC_KP_ASTERISK }, // L1
        { KC_BSPC, KC_LEFT, KC_DOWN, KC_RIGHT, KC_PGDN, KC_KP_SLASH }, // L2
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_BSLS, KC_LEFT_SHIFT, KC_TRANSPARENT }, // L3
        { KC_6   , KC_7   , KC_8   , KC_9   , KC_0   , KC_TRANSPARENT }, // R0
        { KC_KP_PLUS, KC_KP_4, KC_KP_5, KC_KP_6, KC_KP_EQUAL, KC_TRANSPARENT }, // R1
        { KC_KP_MINUS, KC_KP_1, KC_KP_2, KC_KP_3, KC_TRANSPARENT, KC_TRANSPARENT }, // R2
        { KC_NO  , KC_KP_COMMA, KC_KP_0, KC_KP_DOT, KC_MINUS, KC_EQUAL }, // R3
    },
    [_RAISE] = { // Converted from _RAISE
        { KC_TRANSPARENT, KC_F1  , KC_F2  , KC_F3  , KC_F4  , KC_F5   }, // L0
        { KC_TRANSPARENT, KC_F7  , KC_F8  , KC_F9  , KC_F10 , KC_F11  }, // L1
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // L2
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // L3
        { KC_F6  , KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R0
        { KC_F12 , KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R1
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R2
        { KC_NO  , KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R3
    },
    [_ADJUST] = { // Converted from _ADJUST
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // L0
        { KC_DELETE, KC_TRANSPARENT, QK_AUDIO_ON, QK_AUDIO_OFF, AU_TOGG, KC_TRANSPARENT }, // L1
        { KC_TRANSPARENT, KC_TRANSPARENT, QK_MUSIC_ON, QK_MUSIC_OFF, MU_TOGG, KC_TRANSPARENT }, // L2
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // L3
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R0
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, QK_BOOT }, // R1
        { KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R2
        { KC_NO  , KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT }, // R3
    },
};




typedef struct {
    bool is_press_action;
    uint8_t step;
} tap;

enum {
    SINGLE_TAP = 1,      
    SINGLE_HOLD,         
    DOUBLE_TAP,          
    DOUBLE_HOLD,         
    DOUBLE_SINGLE_TAP,   
    MORE_TAPS            
};

static tap dance_state[7];

uint8_t dance_step(tap_dance_state_t *state);

uint8_t dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}


void on_dance_0(tap_dance_state_t *state, void *user_data);
void dance_0_finished(tap_dance_state_t *state, void *user_data);
void dance_0_reset(tap_dance_state_t *state, void *user_data);

void on_dance_0(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
    }
    if(state->count > 3) {
        tap_code16(KC_DELETE);
    }
}

void dance_0_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[0].step = dance_step(state);
    switch (dance_state[0].step) {
        case SINGLE_TAP: register_code16(KC_DELETE); break;
        case DOUBLE_TAP: register_code16(LCTL(KC_DELETE)); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_DELETE); register_code16(KC_DELETE);
    }
}

void dance_0_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[0].step) {
        case SINGLE_TAP: unregister_code16(KC_DELETE); break;
        case DOUBLE_TAP: unregister_code16(LCTL(KC_DELETE)); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_DELETE); break;
    }
    dance_state[0].step = 0;
}
void on_dance_1(tap_dance_state_t *state, void *user_data);
void dance_1_finished(tap_dance_state_t *state, void *user_data);
void dance_1_reset(tap_dance_state_t *state, void *user_data);

void on_dance_1(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_LBRC);
        tap_code16(KC_LBRC);
        tap_code16(KC_LBRC);
    }
    if(state->count > 3) {
        tap_code16(KC_LBRC);
    }
}

void dance_1_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[1].step = dance_step(state);
    switch (dance_state[1].step) {
        case SINGLE_TAP: register_code16(KC_LBRC); break;
        case SINGLE_HOLD: register_code16(KC_RIGHT_GUI); break;
        case DOUBLE_TAP: register_code16(LSFT(KC_LBRC)); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_LBRC); register_code16(KC_LBRC);
    }
}

void dance_1_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[1].step) {
        case SINGLE_TAP: unregister_code16(KC_LBRC); break;
        case SINGLE_HOLD: unregister_code16(KC_RIGHT_GUI); break;
        case DOUBLE_TAP: unregister_code16(LSFT(KC_LBRC)); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_LBRC); break;
    }
    dance_state[1].step = 0;
}
void on_dance_2(tap_dance_state_t *state, void *user_data);
void dance_2_finished(tap_dance_state_t *state, void *user_data);
void dance_2_reset(tap_dance_state_t *state, void *user_data);

void on_dance_2(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_RBRC);
        tap_code16(KC_RBRC);
        tap_code16(KC_RBRC);
    }
    if(state->count > 3) {
        tap_code16(KC_RBRC);
    }
}

void dance_2_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[2].step = dance_step(state);
    switch (dance_state[2].step) {
        case SINGLE_TAP: register_code16(KC_RBRC); break;
        case SINGLE_HOLD: register_code16(KC_RIGHT_ALT); break;
        case DOUBLE_TAP: register_code16(LSFT(KC_RBRC)); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_RBRC); register_code16(KC_RBRC);
    }
}

void dance_2_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[2].step) {
        case SINGLE_TAP: unregister_code16(KC_RBRC); break;
        case SINGLE_HOLD: unregister_code16(KC_RIGHT_ALT); break;
        case DOUBLE_TAP: unregister_code16(LSFT(KC_RBRC)); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_RBRC); break;
    }
    dance_state[2].step = 0;
}
void dance_3_finished(tap_dance_state_t *state, void *user_data);
void dance_3_reset(tap_dance_state_t *state, void *user_data);

void dance_3_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[3].step = dance_step(state);
    switch (dance_state[3].step) {
        case SINGLE_HOLD: register_code16(KC_LEFT_CTRL); break;
        case DOUBLE_TAP: register_code16(KC_CAPS); break;
    }
}

void dance_3_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[3].step) {
        case SINGLE_HOLD: unregister_code16(KC_LEFT_CTRL); break;
        case DOUBLE_TAP: unregister_code16(KC_CAPS); break;
    }
    dance_state[3].step = 0;
}
void on_dance_4(tap_dance_state_t *state, void *user_data);
void dance_4_finished(tap_dance_state_t *state, void *user_data);
void dance_4_reset(tap_dance_state_t *state, void *user_data);

void on_dance_4(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
    }
    if(state->count > 3) {
        tap_code16(KC_SPACE);
    }
}

void dance_4_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[4].step = dance_step(state);
    switch (dance_state[4].step) {
        case SINGLE_TAP: register_code16(KC_SPACE); break;
        case SINGLE_HOLD: register_code16(KC_ENTER); break;
        case DOUBLE_TAP: register_code16(KC_SPACE); register_code16(KC_SPACE); break;
        case DOUBLE_HOLD: register_code16(LSFT(KC_ENTER)); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_SPACE); register_code16(KC_SPACE);
    }
}

void dance_4_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[4].step) {
        case SINGLE_TAP: unregister_code16(KC_SPACE); break;
        case SINGLE_HOLD: unregister_code16(KC_ENTER); break;
        case DOUBLE_TAP: unregister_code16(KC_SPACE); break;
        case DOUBLE_HOLD: unregister_code16(LSFT(KC_ENTER)); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_SPACE); break;
    }
    dance_state[4].step = 0;
}
void on_dance_5(tap_dance_state_t *state, void *user_data);
void dance_5_finished(tap_dance_state_t *state, void *user_data);
void dance_5_reset(tap_dance_state_t *state, void *user_data);

void on_dance_5(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_BSPC);
        tap_code16(KC_BSPC);
        tap_code16(KC_BSPC);
    }
    if(state->count > 3) {
        tap_code16(KC_BSPC);
    }
}

void dance_5_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[5].step = dance_step(state);
    switch (dance_state[5].step) {
        case SINGLE_TAP: register_code16(KC_BSPC); break;
        case SINGLE_HOLD: register_code16(KC_RIGHT_SHIFT); break;
        case DOUBLE_TAP: register_code16(RCTL(KC_BSPC)); break;
        case DOUBLE_HOLD: register_code16(KC_BSPC); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_BSPC); register_code16(KC_BSPC);
    }
}

void dance_5_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[5].step) {
        case SINGLE_TAP: unregister_code16(KC_BSPC); break;
        case SINGLE_HOLD: unregister_code16(KC_RIGHT_SHIFT); break;
        case DOUBLE_TAP: unregister_code16(RCTL(KC_BSPC)); break;
        case DOUBLE_HOLD: unregister_code16(KC_BSPC); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_BSPC); break;
    }
    dance_state[5].step = 0;
}
void on_dance_6(tap_dance_state_t *state, void *user_data);
void dance_6_finished(tap_dance_state_t *state, void *user_data);
void dance_6_reset(tap_dance_state_t *state, void *user_data);

void on_dance_6(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
    }
    if(state->count > 3) {
        tap_code16(KC_DELETE);
    }
}

void dance_6_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[6].step = dance_step(state);
    switch (dance_state[6].step) {
        case SINGLE_TAP: register_code16(KC_DELETE); break;
        case SINGLE_HOLD: register_code16(KC_RIGHT_CTRL); break;
        case DOUBLE_TAP: register_code16(RCTL(KC_DELETE)); break;
        case DOUBLE_HOLD: register_code16(KC_DELETE); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_DELETE); register_code16(KC_DELETE);
    }
}

void dance_6_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[6].step) {
        case SINGLE_TAP: unregister_code16(KC_DELETE); break;
        case SINGLE_HOLD: unregister_code16(KC_RIGHT_CTRL); break;
        case DOUBLE_TAP: unregister_code16(RCTL(KC_DELETE)); break;
        case DOUBLE_HOLD: unregister_code16(KC_DELETE); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_DELETE); break;
    }
    dance_state[6].step = 0;
}

tap_dance_action_t tap_dance_actions[] = {
        [DANCE_0] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_0, dance_0_finished, dance_0_reset),
        [DANCE_1] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_1, dance_1_finished, dance_1_reset),
        [DANCE_2] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_2, dance_2_finished, dance_2_reset),
        [DANCE_3] = ACTION_TAP_DANCE_FN_ADVANCED(NULL, dance_3_finished, dance_3_reset),
        [DANCE_4] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_4, dance_4_finished, dance_4_reset),
        [DANCE_5] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_5, dance_5_finished, dance_5_reset),
        [DANCE_6] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_6, dance_6_finished, dance_6_reset),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
  switch (keycode) {
            
                case DUAL_FUNC_0:
      if (record->tap.count > 0) {
        if (record->event.pressed) {
          register_code16(KC_BSPC);
        } else {
          unregister_code16(KC_BSPC);
        }
      } else {
        if (record->event.pressed) {
          register_code16(LCTL(KC_BSPC));
        } else {
          unregister_code16(LCTL(KC_BSPC));
        }  
      }  
      return false;
  }
  return true;
}

#ifdef AUDIO_ENABLE
bool muse_mode = false;
uint8_t last_muse_note = 0;
uint16_t muse_counter = 0;
uint8_t muse_offset = 70;
uint16_t muse_tempo = 50;

void encoder_update(bool clockwise) {
    if (muse_mode) {
        if (IS_LAYER_ON(_RAISE)) {
            if (clockwise) {
                muse_offset++;
            } else {
                muse_offset--;
            }
        } else {
            if (clockwise) {
                muse_tempo+=1;
            } else {
                muse_tempo-=1;
            }
        }
    } else {
        if (clockwise) {
        #ifdef MOUSEKEY_ENABLE
            register_code(KC_MS_WH_DOWN);
            unregister_code(KC_MS_WH_DOWN);
        #else
            register_code(KC_PGDN);
            unregister_code(KC_PGDN);
        #endif
        } else {
        #ifdef MOUSEKEY_ENABLE
            register_code(KC_MS_WH_UP);
            unregister_code(KC_MS_WH_UP);
        #else
            register_code(KC_PGUP);
            unregister_code(KC_PGUP);
        #endif
        }
    }
}

#if 0 // Disabled by oryx_to_olkb
/* void matrix_scan_user(void) {
#ifdef AUDIO_ENABLE
    if (muse_mode) {
        if (muse_counter == 0) {
            uint8_t muse_note = muse_offset + SCALE[muse_clock_pulse()];
            if (muse_note != last_muse_note) {
                stop_note(compute_freq_for_midi_note(last_muse_note));
                play_note(compute_freq_for_midi_note(muse_note), 0xF);
                last_muse_note = muse_note;
            }
        }
        muse_counter = (muse_counter + 1) % muse_tempo;
    }
#endif
} */
#endif

bool music_mask_user(uint16_t keycode) {
    switch (keycode) {
    case RAISE:
    case LOWER:
        return false;
    default:
        return true;
    }
}
#endif

layer_state_t layer_state_set_user(layer_state_t state) {
    return update_tri_layer_state(state, _LOWER, _RAISE, _ADJUST);
}


