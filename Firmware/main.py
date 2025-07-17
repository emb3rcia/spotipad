import board
import usb_cdc
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.media_keys import MediaKeys

import displayio
import adafruit_displayio_ssd1306
import busio
import terminalio
from kmk.modules.encoder import EncoderHandler

keyboard = KMKKeyboard()

encoder_a = board.GP28
encoder_b = board.GP29
encoder_press = board.GP0

encoder_handler = EncoderHandler()
encoder_handler.pins = (encoder_a, encoder_b, encoder_press)
encoder_handler.map = {
    KC.VOLU,
    KC.VOLD,
    KC.MUTE,
}

keyboard.modules = [encoder_handler]
keyboard.extensions.append(MediaKeys())

keyboard.col_pins = (board.GP1, board.GP2, board.GP4)
keyboard.row_pins = (board.GP27,)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

displayio.release_displays()

i2c = busio.I2C(scl=board.GP7, sda=board.GP6)

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

splash = displayio.Group()
display.show(splash)

track_label = adafruit_displayio_ssd1306.label.Label(terminalio.FONT, text="Oczekiwanie...", color=0xFFFFFF, x=0, y=10)
splash.append(track_label)

author_label = adafruit_displayio_ssd1306.label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=0, y=30)
splash.append(author_label)


keyboard.keymap = [
    [
        KC.MNXT,
        KC.MPLY,
        KC.MPRV,
    ]
]


def update_display_from_pc():
    """
    Check for incoming data from the PC via USB CDC.
    If data is received, update the display with track and artist information.
    Expects format "TRACK_NAME|ARTIST_NAME".
    """
    if usb_cdc.data.in_waiting:
        try:
            data = usb_cdc.data.readline().strip().decode('utf-8')
            print(f"Recieved from PC: {data}")

            if "|" in data:
                track_name, artist_name = data.split("|", 1)
                track_label.text = track_name
                author_label.text = artist_name
            else:
                print(f"Invalid data format: {data}")

        except Exception as e:
            print(f"Error in receiving data from PC: {e}")

if __name__ == "__main__":
    def my_loop_hook():
        update_display_from_pc()
        time.sleep(0.01)

    keyboard.on_runtime_enable_loop.append(my_loop_hook)

    keyboard.go()