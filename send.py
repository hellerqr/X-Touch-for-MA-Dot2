import time
import mido
from mido import Message

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
def list_output_ports():
    """ Listet alle verfügbaren MIDI-Ausgangsports auf. """
    print("Verfügbare MIDI Ausgangsports:")
    for port in mido.get_input_names():
        print(port)



if __name__ == "__main__":
    list_output_ports()

    # Benutzeraufforderung zur Auswahl des Ports
    port_name = "X-Touch 1"
    j = 0
    while True:
        j = 20 if j == 127 else 127
        for i in range(89, 98):
            send_control_change(port_name, i, j, 0)
            time.sleep(0.03)

    #send_control_change(port_name, control, value, channel)
    send_note(port_name, 89, 127)
