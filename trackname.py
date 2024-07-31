import time
import mido
from mido import MidiFile, MidiTrack, Message
import mido.backends.rtmidi

# Funktion, um einen Text-String in eine SysEx-Nachricht umzuwandeln
def text_to_sysex_message(track_number=0, text=0):
    sysex_header = [0xF0, 0x00, 0x20, 0x32, 0x14, 0x4C, 0x00, 0x35]
    text_data = [0x48, 0x61, 0x6C, 0x6c, 0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    foot = [0xF7]

    sysex_message = sysex_header + text_data + foot



    print(sysex_message)
    return sysex_message


def generate_sysex(text, lcd_number, backlight_color=7):
    # Device ID für X-Touch ist 0x14
    device_id = 0x14

    # LCD Nummer begrenzt auf 0..7
    lcd_number = lcd_number % 8

    # Backlight-Farbe begrenzt auf 0..7
    backlight_color = backlight_color % 8

    # ASCII-Zeichen auffüllen und begrenzen
    ascii_chars = text.ljust(14, '\x00')[:14]

    # SysEx Nachricht aufbauen
    sysex = [0xF0, 0x00, 0x20, 0x32, device_id, 0x4C, lcd_number, backlight_color]

    # ASCII Zeichen hinzufügen
    for char in ascii_chars:
        sysex.append(ord(char))

    # SysEx End hinzufügen
    sysex.append(0xF7)
    print(sysex)
    return sysex


def time_to_sysex():
    # Get the current time
    current_time = time.strftime('%H%M%S')

    # Define segment map for 7-segment display (0-9)
    segment_map = {
        '0': 0b0111111,
        '1': 0b0000110,
        '2': 0b1011011,
        '3': 0b1001111,
        '4': 0b1100110,
        '5': 0b1101101,
        '6': 0b1111101,
        '7': 0b0000111,
        '8': 0b1111111,
        '9': 0b1101111
    }

    # Convert time to segment data
    segment_data = [segment_map[digit] for digit in current_time]

    # Add two empty segments at the beginning
    segment_data = [0, 0, 0] + segment_data

    # Fill up segment data to 12 elements
    while len(segment_data) < 12:
        segment_data.append(0)

    # Determine dot positions
    dots1 = 0b000000  # For displays 1 to 7
    dots2 = 0b000000  # For displays 8 to 12

    # Create the SysEx message
    device_id = 0x14  # Assuming X-Touch
    sysex_msg = [0xF0, 0x00, 0x20, 0x32, device_id, 0x37] + segment_data + [dots1, dots2] + [0xF7]
    write_port_name = "X-Touch 1"
    with mido.open_output(write_port_name) as outport:
        # msg = mido.Message.from_bytes(generate_sysex("COOL", 1, 9))
        while True:
            msg = Message.from_bytes(sysex_msg)
            outport.send(msg)
            time.sleep(0.5)


def send_note(port_name, note, velocity, channel=0):
    """ Sendet eine Note"""
    try:
        with mido.open_output(port_name) as outport:
            msg = Message("note_on", note=note, velocity=velocity)
            outport.send(msg)
            print(f"Gesendet: {msg}")
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")

if __name__ == "__main__":
    read_port_name = "X-Touch 0"
    write_port_name = "X-Touch 1"
    with mido.open_output(write_port_name) as outport:
        msg = mido.Message.from_bytes(generate_sysex("COOL", 1, 8))
        outport.send(msg)

