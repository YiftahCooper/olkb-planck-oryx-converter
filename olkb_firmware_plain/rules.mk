# MCU name
MCU = STM32F303

# Bootloader selection
BOOTLOADER = stm32-dfu

# Build Options
#   change yes to no to disable 'no'
#
BOOTMAGIC_ENABLE = yes      # Enable Bootmagic Lite
MOUSEKEY_ENABLE  = yes      # Mouse keys
EXTRAKEY_ENABLE  = yes      # Audio control and System control
CONSOLE_ENABLE   = no       # Console for debug
COMMAND_ENABLE   = yes      # Commands for debug and configuration
NKRO_ENABLE      = yes      # Enable N-Key Rollover
BACKLIGHT_ENABLE = no       # Enable keyboard backlight functionality
RGBLIGHT_ENABLE  = no       # Enable keyboard RGB underglow
AUDIO_ENABLE     = yes      # Audio output
TAP_DANCE_ENABLE = yes      # Enable Tap Dance functionality (Required for Oryx keymap)
ENCODER_ENABLE   = yes      # Enable encoder support
LTO_ENABLE       = yes      # Link Time Optimization (smaller binary)
