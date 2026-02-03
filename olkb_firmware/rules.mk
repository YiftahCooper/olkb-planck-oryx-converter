VIA_ENABLE = yes
VIAL_ENABLE = yes
QMK_SETTINGS = yes
LTO_ENABLE = yes
ifeq ($(strip $(AUDIO_ENABLE)), yes)
    SRC += muse.c
endif
