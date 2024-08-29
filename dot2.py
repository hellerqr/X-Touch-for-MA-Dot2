import hashlib
import json
import time
import websocket
import threading
from mido import Message
import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from midi import *
# Zustand der Tasten und Fader
tasten = [False for _ in range(127)]
fader_values = [0 for _ in range(8)]
last_fader_change = [time.time() for _ in range(8)]
button_100 = [0 for _ in range(8)]
button_200 = [0 for _ in range(8)]
button1 = [0 for _ in range(8)]
button2 = [0 for _ in range(8)]
speed = {"tilt": 1, "pan": 1, "dim": 1, "shutter": 1, "R": 10, "G": 10, "B": 10}
fader_names = [["" for _ in range(8)] for _ in range(100)]
fader_color = [[8 for _ in range(8)] for _ in range(100)] ### 7->normal 8->off
button_types = [[] for _ in range(8)]
button_types_100 = ["" for _ in range(8)]
button_types_200 = ["" for _ in range(8)]
last_msg = time.time()
page = 0
request = 0
counter = 0
commands = {40: 'PresetType "Dimmer"', 41: 'PresetType "Position"', 42: 'PresetType "Gobo"', 43: 'PresetType "Color"', 44: 'PresetType "Beam"', 45: 'PresetType "Control"'}
clear = False
store = False
select_for_lable = False
blackout = False
work_buttons = {"store": False, "select_for_lable": False, "delete": False, "move": False}
work_buttons_code = {"store": 71, "select_for_lable": 69, "delete": 83, "move": 84}
multi_select_work_buttons = {"move": []}
if os.path.exists("colors.json"):
    with open('colors.json', 'r') as file:
        fader_color = json.load(file)
if os.path.exists("names.json"):
    with open('names.json', 'r') as file:
        fader_names = json.load(file)


def handle_drehregler(control, value, console):
    control_map = {
        80: ("pan", console.pan),
        81: ("tilt", console.tilt),
        82: ("dim", console.dim),
        83: ("shutter", console.shutter),
        85: ("colorrgb1", lambda v: console.encoder("colorrgb1", v)),
        86: ("colorrgb2", lambda v: console.encoder("colorrgb2", v)),
        87: ("colorrgb3", lambda v: console.encoder("colorrgb3", v)),
        88: ("DIM", lambda v: console.encoder("DIM", v))
    }

    if control in control_map:
        speed_key, action = control_map[control]
        adjustment = speed[speed_key]
        if value < 64:
            action(-adjustment)
        elif value > 64:
            action(adjustment)
        send_control_change(control, 64)


def handle_control_change(control, value, console):
    # Mapping für die Steuerung von Fadern (70-77)
    if 70 <= control < 78:
        index = control - 70
        if fader_values[index] != value:
            fader_values[index] = value
            last_fader_change[index] = time.time()
            console.fade(index, value / 127)

    # Spezialbehandlung für MAIN-Fader (78)
    elif control == 78:
        console.specialmaster("2.1", str(int((value / 127) * 100)))
        if int((value / 127) * 100) != 100:
            send_note(57, 64)
            blackout = True
        else:
            blackout = False
            send_note(57, 0)

    # Behandlung von Drehreglern (80-88)
    elif control in range(80, 89):
        handle_drehregler(control, value, console)




def handle_button_action(action_type, i, executor_base, note, console):
    if action_type == "Toggle":
        button1[i] = 127 if button1[i] != 127 else 0
        console.command(f"Toggle Executor {page + 1}.{executor_base + i}")
        send_note(note, button1[i])
    elif action_type in {"Flash", "Temp", "Swop"}:
        button1[i] = 127
        console.command(f"{action_type} Executor {page + 1}.{executor_base + i}")
        send_note(note, 127)
    elif action_type in {"Go", "GoBack", "Pause", "Learn", "Select"}:
        console.command(f"{action_type} Executor {page + 1}.{executor_base + i}")

def handle_store_action(i, executor_base, button_types, console):
    if button_types[i] == "":
        console.command(f"Store Executor {page + 1}.{executor_base + i}")
    else:
        messagebox.showerror(
            title="Speicherfehler",
            message="Nutze zum Speichern auf belegten Fadern die GUI"
        )

def handle_note_on(note, velocity, console):
    if velocity == 127:
        for i in range(8):
            executor_100 = 101
            executor_200 = 201
            executor_0 = 1

            if note == 8 + i:
                if work_buttons["store"]:
                    handle_store_action(i, executor_100, button_types_100, console)
                else:
                    handle_button_action(button_types_100[i], i, executor_100, note, console)
            elif note == 16 + i:
                if work_buttons["store"]:
                    handle_store_action(i, executor_200, button_types_200, console)
                else:
                    handle_button_action(button_types_200[i], i, executor_200, note, console)
            elif note == 32 + i:
                handle_button_action(button_types[i][1], i, executor_0, note, console)
            elif note == 24 + i:
                handle_button_action(button_types[i][0], i, executor_0, note, console)
            elif note == 58 + i:
                if not work_buttons["store"]:
                    console.command(f"Group {i+1}")
                else:
                    console.command(f"Store Group {i+1}")
                    work_buttons["store"] = False
                    send_note(work_buttons_code["store"], 0)

        # Weitere spezielle Tastenverarbeitungen
        handle_special_notes(note, console)

def handle_special_notes(note, console):
    special_note_actions = {
        93: lambda: (increment_page(), fill_displays()),
        92: lambda: (decrement_page(), fill_displays()) if page > 0 else None,
        87: lambda: console.command("GoBack"),
        88: lambda: console.command("Go"),
        90: lambda: console.command("Pause"),
        71: lambda: toggle_work_button("store", note),
        83: lambda: toggle_work_button("delete", note),
        84: lambda: toggle_work_button("move", note),
        78: lambda: toggle_clear(console, note),
        72: lambda: console.command("Oops@"),
        79: lambda: console.command("Please@"),
        70: lambda: console.command("Fixture@"),
        77: lambda: console.command("Group@"),
        94: lambda: console.command("Previous"),
        95: lambda: console.command("Next"),
        98: lambda: console.command("Previous"),
        99: lambda: console.command("Next"),
        96: lambda: console.command("Up"),
        97: lambda: console.command("Down"),
        100: lambda: console.command("MAtricks Toggle"),
        0: lambda: toggle_speed("pan"),
        1: lambda: toggle_speed("tilt"),
        2: lambda: toggle_speed("dim"),
        3: lambda: toggle_speed("shutter"),
        5: lambda: toggle_speed("R"),
        6: lambda: toggle_speed("G"),
        7: lambda: toggle_speed("B"),
        57: lambda: toggle_blackout(console, note),
        69: lambda: toggle_work_button("select_for_lable", note)
    }

    if note in special_note_actions:
        special_note_actions[note]()

def toggle_speed(parameter):
    speed[parameter] = 10 if speed[parameter] == 1 else 1

def toggle_blackout(console, note):
    global blackout
    if blackout:
        console.specialmaster("2.1", "100")
        send_note(57, 0)
        blackout = False
        send_control_change(78, 127)
    else:
        console.specialmaster("2.1", "0")
        send_note(57, 64)
        blackout = True
        send_control_change(78, 0)

def toggle_work_button(button_name, note):
    work_buttons[button_name] = not work_buttons[button_name]
    if work_buttons[button_name]:
        send_note(note, 64)
        for key in work_buttons:
            if key != button_name:
                work_buttons[key] = False
    else:
        send_note(note, 0)

def toggle_clear(console, note):
    global clear
    console.command("Clear")
    clear = not clear
    send_note(note, 64 if clear else 0)

def increment_page():
    global page
    page += 1

def decrement_page():
    global page
    page -= 1


def read_midi_messages(console=None):
    global page
    global blackout
    global last_msg
    global clear
    global select_for_lable
    global commands
    global work_buttons
    global work_buttons_code
    global multi_select_work_buttons
    global fader_names
    global fader_color
    """Liest MIDI-Nachrichten vom angegebenen Port."""
    try:
        with (mido.open_input("X-Touch 0") as inport):
            for msg in inport:
                if msg.type == "control_change":
                    handle_control_change(msg.control, msg.value, console)

                elif msg.type == "note_on":
                    handle_note_on(msg.note, msg.velocity, console)
    except Exception as e:
        print(f"1 Fehler beim Öffnen des Lese Ports: {e}")

def send_note(note, velocity, channel=0, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            with mido.open_output("X-Touch 1") as outport:
                msg = Message("note_on", note=note, velocity=velocity)
                outport.send(msg)
                return  # Erfolgreich gesendet, Funktion beenden
        except Exception as e:
            print(f"Fehler beim Öffnen des Ports (Send Note): {e}")
            attempt += 1
            time.sleep(0.5)  # Wartezeit zwischen den Versuchen

    print(f"Fehler: Send Note nach {retries} Versuchen fehlgeschlagen.")

def send_control_change(control, value, channel=0, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            with mido.open_output("X-Touch 1") as outport:
                msg = Message('control_change', control=control, value=value, channel=channel)
                outport.send(msg)
                return  # Erfolgreich gesendet, Funktion beenden
        except Exception as e:
            print(f"Fehler beim Öffnen des Ports (Send CC): {e}")
            attempt += 1
            time.sleep(0.5)  # Wartezeit zwischen den Versuchen

    print(f"Fehler: Send Control Change nach {retries} Versuchen fehlgeschlagen.")


def send_sysex(sysex, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            with mido.open_output("X-Touch 1") as outport:
                msg = Message.from_bytes(sysex)
                outport.send(msg)
                return  # Erfolgreich gesendet, Funktion beenden
        except Exception as e:
            print(f"Fehler beim Öffnen des Ports (Send Sysex): {e}\tSysex: {sysex}")
            attempt += 1
            time.sleep(0.5)  # Wartezeit zwischen den Versuchen

    print(f"Fehler: Send Sysex nach {retries} Versuchen fehlgeschlagen.")


def time_to_sysex():
    def update_time():
        while True:
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
            send_sysex(sysex_msg)
            time.sleep(1)
    threading.Thread(target=update_time).start()

def get_name(lpage, lnum):
    root = tk.Tk()
    root.withdraw()  # Das Hauptfenster ausblenden
    name = simpledialog.askstring("Fader benennen", "Geben sie einen Namen für den Executer ein:")
    fader_names[lpage][lnum] = name
    fader_color[lpage][lnum] = 7
    with open('names.json', 'w') as file:
        json.dump(fader_names, file)
    with open('colors.json', 'w') as file:
        json.dump(fader_color, file)
    fill_displays()

def generate_sysex(text, lcd_number, backlight_color=7):
    device_id = 0x14
    lcd_number = lcd_number % 8
    backlight_color = backlight_color % 8
    ascii_chars = text.ljust(14, '\x00')[:14]
    sysex = [0xF0, 0x00, 0x20, 0x32, device_id, 0x4C, lcd_number, backlight_color]
    for char in ascii_chars:
        sysex.append(ord(char))
    sysex.append(0xF7)
    return sysex

def fill_displays():
    global page
    names = fader_names[page]
    colors = fader_color[page]
    for i, v in enumerate(names):
        sysex = generate_sysex(v, i, colors[i])
        send_sysex(sysex)

class Dot2:
    def __init__(self, address: str, password: str):
        self.address = address
        self.password = hashlib.md5(password.encode("utf-8")).hexdigest()
        self.initialized = False
        self.session_id = None

    def connect(self):
        """Initialize socket."""
        self.ws = websocket.WebSocketApp(f"ws://{self.address}/?ma=1",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.listen_thread = threading.Thread(target=self.ws.run_forever)
        self.listen_thread.start()
        print("INIT")

    def start_update_interval(self):
        def update():
            while self.initialized:
                self.send({
                    "requestType": "playbacks",
                    "startIndex": [0, 100, 200],
                    "itemsCount": [8, 8, 8],
                    "pageIndex": page,
                    "itemsType": [2, 3, 3],
                    "view": 2,
                    "execButtonViewMode": 1,
                    "buttonsViewMode": 1,
                    "session": self.session_id,
                    "maxRequests": 1
                })
                time.sleep(0.1)  # Update alle 0.1 Sekunden  #TEST: Nutze 0.2, 0.5 Sekunden

        threading.Thread(target=update).start()

    def on_message(self, ws, message):
        global counter
        global last_msg
        global request
        data = json.loads(message)
        request += 1
        if request >= 9:
            self.send({"session": self.session_id})
            self.send({"requestType": "getdata", "data": "set", "session": self.session_id, "maxRequests": 1})
            request = 0
        if "status" in data:
            if data["status"] == "server ready":
                print(11111111)
                self.send({"session": 0, "maxRequests": 0})

        if "session" in data:
            if data["session"] == -1:
                exit()
            elif data["session"] == 0:
                print("SESSION ERROR")
                self.send({"requestType": "login", "username": "remote", "password": self.password,
                           "session": self.session_id, "maxRequests": 0})

                self.send({"session": self.session_id})
            else:
                self.session_id = data["session"]

        if "forceLogin" in data:
            self.send({"requestType": "login", "username": "remote", "password": self.password, "session": self.session_id, "maxRequests": 0})

        if "responseType" in data:
            if data["responseType"] == "login":
                print("Login erfolgreich")
                self.start_update_interval()
            if data["responseType"] == "playbacks":
                for i in range(8):
                    new_value = int(data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["fader"]["v"]*127)
                    if last_fader_change[i] + 0.5 < time.time():
                        if fader_values[i] != new_value:
                            send_control_change(70 + i, new_value)
                            fader_values[i] = new_value
                    is_emty = data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["fader"]["max"] == 0
                    button_types[i] = [data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["button1"]["t"], data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["button2"]["t"]]
                    button_types_100[i] = data["itemGroups"][1]["items"][i][0]["executorBlocks"][0]["button1"]["t"]
                    button_types_200[i] = data["itemGroups"][2]["items"][i][0]["executorBlocks"][0]["button1"]["t"]
                    if is_emty:
                        fader_names[page][i] = ""
                        fader_color[page][i] = 8
                        fill_displays()
                    else:
                        if fader_names[page][i] == "":
                            fader_names[page][i] = "unnamed"
                        if fader_color[page][i] == 8:
                            fader_color[page][i] = 7
                        fill_displays()
                for i in range(8):
                    new_value = int(data["itemGroups"][2]["items"][i][0]["isRun"]*127)
                    if button_200[i] != new_value:
                        send_note(16 + i, new_value)
                        button_200[i] = new_value
                for i in range(8):
                    new_value = int(data["itemGroups"][1]["items"][i][0]["isRun"]*127)
                    if button_100[i] != new_value:
                        send_note(8 + i, new_value)
                        button_100[i] = new_value
                for i in range(8):
                    new_value = int(data["itemGroups"][0]["items"][i][0]["isRun"] * 127)
                    if button1[i] != new_value:
                        send_note(32 + i, new_value)
                        button1[i] = new_value

    def on_error(self, ws, error):
        print(f"5 Fehler: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### Verbindung geschlossen ###")

    def on_open(self, ws):
        self.initialized = True
        print("Verbindung hergestellt")

    def send(self, payload: dict):
        self.ws.send(json.dumps(payload, separators=(',', ':')))


    def command(self, command):
        self.send({"requestType": "command", "command": command, "session": self.session_id, "maxRequests": 0})

    def pan(self, val):
        self.send({"requestType": "encoder", "name": "PAN", "value": val, "session": self.session_id, "maxRequests": 0})
    def tilt(self, val):
        self.send({"requestType": "encoder", "name": "TILT", "value": val, "session": self.session_id, "maxRequests": 0})

    def dim(self, val):
        self.send({"requestType": "encoder", "name": "DIM", "value": val, "session": self.session_id, "maxRequests": 0})

    def shutter(self, val):
        self.send({"requestType": "encoder", "name": "Shutter", "value": val, "session": self.session_id, "maxRequests": 0})

    def encoder(self, name, val):
        self.send({"requestType": "encoder", "name": name, "value": val, "session": self.session_id,
                   "maxRequests": 0})

    def fade(self, fadernum, value):
        global page
        self.send({"requestType": "playbacks_userInput", "execIndex": fadernum, "pageIndex": page, "faderValue": value,
                   "type": 1, "session": self.session_id, "maxRequests": 0})

    def specialmaster(self, num, val):
        self.send({"requestType": "command", "command": f"SpecialMaster {num} At {val}", "session": self.session_id,
                   "maxRequests": 0})

    def button(self, button):
        global page
        self.send({"requestType": "playbacks_userInput", "cmdline": "", "execIndex": button, "pageIndex": page, "buttonId": 0,
                   "pressed": True, "released": False, "type": 0, "session": self.session_id, "maxRequests": 0})

def main():
    console = Dot2("127.0.0.1", "")
    console.connect()

    # Warten bis die Verbindung hergestellt ist
    time.sleep(1)
    send_control_change(78, 127)
    console.specialmaster("2.1", "100")
    time_to_sysex()
    fill_displays()
    try:
        while True:
            read_midi_messages(console)
    except KeyboardInterrupt:
        console.ws.close()

if __name__ == "__main__":
    main()
