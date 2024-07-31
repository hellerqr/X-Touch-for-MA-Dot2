import mido
from mido import MidiFile, MidiTrack, Message
import mido.backends.rtmidi

tasten = [False for i in range(127)]
def send_control_change(port_name, control, value, channel=0):
    """ Sendet eine Control Change Nachricht an den angegebenen MIDI-Ausgangsport. """
    try:
        with mido.open_output(port_name) as outport:
            msg = Message('control_change', control=control, value=value, channel=channel)
            outport.send(msg)
            print(f"Gesendet: {msg}")
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")

def send_note(port_name, note, velocity, channel=0):
    """ Sendet eine Note"""
    try:
        with mido.open_output(port_name) as outport:
            msg = Message("note_on", note=note, velocity=velocity)
            outport.send(msg)
            print(f"Gesendet: {msg}")
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")
def read_midi_messages(port_name):
    """ Liest MIDI-Nachrichten vom angegebenen Port. """
    try:
        with mido.open_input(port_name) as inport:
            print(f"Lese MIDI-Nachrichten von {port_name}...")
            for msg in inport:
                print(msg)
                """if msg.type == "control_change":
                    value = msg.value
                    control = msg.control
                    send_control_change(write_port_name, control+1, value)
                    print(control, value)
                if msg.type == "note_on":
                    note = msg.note
                    velocity = msg.velocity
                    channel = msg.channel
                    if velocity == 127:
                        tasten[note] = not tasten[note]
                        x = 127 if tasten[note] else 0
                        send_note(write_port_name, note, x, channel)"""
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")


if __name__ == "__main__":
    read_port_name = "X-Touch 0"
    write_port_name = "X-Touch 1"
    read_midi_messages(read_port_name)
