import mido
from mido import get_input_names, get_output_names

def list_midi_devices():
    input_devices = get_input_names()
    output_devices = get_output_names()

    print("Eingabegeräte (Input Devices):")
    if input_devices:
        for device in input_devices:
            print(f"  - {device}")
    else:
        print("  Keine Eingabegeräte gefunden.")

    print("\nAusgabegeräte (Output Devices):")
    if output_devices:
        for device in output_devices:
            print(f"  - {device}")
    else:
        print("  Keine Ausgabegeräte gefunden.")

if __name__ == "__main__":
    list_midi_devices()
