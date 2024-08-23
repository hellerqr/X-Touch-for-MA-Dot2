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
                    value = msg.value
                    control = msg.control
                    for i in range(0, 8):
                        if control == 70 + i and console:
                            # Überprüfe, ob der Wert sich tatsächlich geändert hat
                            if fader_values[i] != value:
                                fader_values[i] = value
                                last_fader_change[i] = time.time()
                                console.fade(i, value / 127)
                    if control == 78 and console: ## MAIN
                        console.specialmaster("2.1", str(int((value/127)*100)))
                        if str(int((value/127)*100)) != "100":
                            send_note(57, 64)
                            blackout = True
                        else:
                            blackout = False
                            send_note(57, 0)
                    if control == 80 and console: ## Drehregler 1
                        if value < 64:
                            console.pan(-speed["pan"])
                        if value > 64:
                            console.pan(speed["pan"])
                        send_control_change(80, 64)
                    if control == 81 and console: ## Drehregler 2
                        if value < 64:
                            console.tilt(-speed["tilt"])
                        if value > 64:
                            console.tilt(speed["tilt"])
                        send_control_change(81, 64)
                    if control == 82 and console: ## Drehregler 3
                        if value < 64:
                            console.dim(-speed["dim"])
                        if value > 64:
                            console.dim(speed["dim"])
                        send_control_change(82, 64)
                    if control == 83 and console: ## Drehregler 4
                        if value < 64:
                            console.shutter(-speed["shutter"])
                        if value > 64:
                            console.shutter(speed["shutter"])
                        send_control_change(83, 64)
                    ####PLATZ FÜR 5###
                    if control == 85 and console: ## Drehregler 6
                        if value < 64:
                            console.encoder("colorrgb1", -speed["R"])
                        if value > 64:
                            console.encoder("colorrgb1", speed["R"])
                        send_control_change(85, 64)
                    if control == 86 and console:  ## Drehregler 7
                        if value < 64:
                            console.encoder("colorrgb2", -speed["G"])
                        if value > 64:
                            console.encoder("colorrgb2", speed["G"])
                        send_control_change(86, 64)
                    if control == 87 and console:  ## Drehregler 8
                        if value < 64:
                            console.encoder("colorrgb3", -speed["B"])
                        if value > 64:
                            console.encoder("colorrgb3", speed["B"])
                        send_control_change(87, 64)

                    if control == 88 and console:  ## Großes Rad
                        if value == 1:
                            console.encoder("DIM", -5)
                        if value == 65:
                            console.encoder("DIM", 5)
                        send_control_change(87, 64)

                if msg.type == "note_on":
                    note = msg.note
                    velocity = msg.velocity
                    if velocity == 127:
                        for i in range(0, 8):
                            if note == 8 + i and console:
                                if work_buttons["store"]:
                                    if button_types_100[i] == "":
                                        console.command(f"Store Executor {page + 1}.{i + 101}")
                                        continue
                                    else:
                                        messagebox.showerror(title="Speicherfehler", message="Nutze zum Speichern auf belegten Fadern die GUI")
                                if button_types_100[i] == "Toggle":
                                    if button1[i] != 127:
                                        button1[i] = 127
                                        console.command(f"Toggle Executor {page + 1}.{i + 101}")
                                        send_note(note, 127)
                                    else:
                                        button1[i] = 0
                                        console.command(f"Toggle Executor {page + 1}.{i + 101}")
                                        send_note(note, 0)
                                elif button_types_100[i] == "Flash":
                                    button1[i] = 127
                                    console.command(f"Flash Executor {page + 1}.{i + 101}")
                                    send_note(note, 127)
                                elif button_types_100[i] == "Temp":
                                    button1[i] = 127
                                    console.command(f"Temp Executor {page + 1}.{i + 101}")
                                    send_note(note, 127)
                                elif button_types_100[i] == "Go":
                                    console.command(f"Go Executor {page + 1}.{i + 101}")
                                elif button_types_100[i] == "GoBack":
                                    console.command(f"GoBack Executor {page + 1}.{i + 101}")
                                elif button_types_100[i] == "Pause":
                                    console.command(f"Pause Executor {page + 1}.{i + 101}")
                                elif button_types_100[i] == "Learn":
                                    console.command(f"Learn Executor {page + 1}.{i + 101}")
                                elif button_types_100[i] == "Select":
                                    console.command(f"Select Executor {page + 1}.{i + 101}")
                                elif button_types_100[i] == "Swop":
                                    button1[i] = 127
                                    console.command(f"Swop Executor {page + 1}.{i + 101}")
                                    send_note(note, 127)
                            elif note == 16 + i and console:
                                if work_buttons["store"]:
                                    if button_types_200[i] == "":
                                        console.command(f"Store Executor {page + 1}.{i + 201}")
                                        continue
                                    else:
                                        messagebox.showerror(title="Speicherfehler",
                                                             message="Nutze zum Speichern auf belegten Fadern die GUI")
                                if button_types_200[i] == "Toggle":
                                    if button1[i] != 127:
                                        button1[i] = 127
                                        console.command(f"Toggle Executor {page + 1}.{i + 201}")
                                        send_note(note, 127)
                                    else:
                                        button1[i] = 0
                                        console.command(f"Toggle Executor {page + 1}.{i + 201}")
                                        send_note(note, 0)
                                elif button_types_200[i] == "Flash":
                                    button1[i] = 127
                                    console.command(f"Flash Executor {page + 1}.{i + 201}")
                                    send_note(note, 127)
                                elif button_types_200[i] == "Temp":
                                    button1[i] = 127
                                    console.command(f"Temp Executor {page + 1}.{i + 201}")
                                    send_note(note, 127)
                                elif button_types_200[i] == "Go":
                                    console.command(f"Go Executor {page + 1}.{i + 201}")
                                elif button_types_200[i] == "GoBack":
                                    console.command(f"GoBack Executor {page + 1}.{i + 201}")
                                elif button_types_200[i] == "Pause":
                                    console.command(f"Pause Executor {page + 1}.{i + 201}")
                                elif button_types_200[i] == "Learn":
                                    console.command(f"Learn Executor {page + 1}.{i + 201}")
                                elif button_types_200[i] == "Select":
                                    console.command(f"Select Executor {page + 1}.{i + 201}")
                                elif button_types_200[i] == "Swop":
                                    button1[i] = 127
                                    console.command(f"Swop Executor {page + 1}.{i + 201}")
                                    send_note(note, 127)
                            elif note == 32 + i and console: ## SELECT
                                if button_types[i][1] == "Toggle":
                                    if button1[i] != 127:
                                        button1[i] = 127
                                        console.command(f"Toggle Executor {page+1}.{i+1}")
                                        send_note(note, 127)
                                    else:
                                        button1[i] = 0
                                        console.command(f"Toggle Executor {page+1}.{i+1}")
                                        send_note(note, 0)
                                elif button_types[i][1] == "Flash":
                                    button1[i] = 127
                                    console.command(f"Flash Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                                elif button_types[i][1] == "Temp":
                                    button1[i] = 127
                                    console.command(f"Temp Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                                elif button_types[i][1] == "Go":
                                    console.command(f"Go Executor {page+1}.{i+1}")
                                elif button_types[i][1] == "GoBack":
                                    console.command(f"GoBack Executor {page+1}.{i+1}")
                                elif button_types[i][1] == "Pause":
                                    console.command(f"Pause Executor {page+1}.{i+1}")
                                elif button_types[i][1] == "Learn":
                                    console.command(f"Learn Executor {page+1}.{i+1}")
                                elif button_types[i][1] == "Select":
                                    console.command(f"Select Executor {page+1}.{i+1}")
                                elif button_types[i][1] == "Swop":
                                    button1[i] = 127
                                    console.command(f"Swop Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                            elif note == 24 + i and console: ## SELECT
                                if button_types[i][0] == "Toggle":
                                    if button1[i] != 127:
                                        button1[i] = 127
                                        console.command(f"Toggle Executor {page+1}.{i+1}")
                                        send_note(note, 127)
                                    else:
                                        button1[i] = 0
                                        console.command(f"Toggle Executor {page+1}.{i+1}")
                                        send_note(note, 0)
                                elif button_types[i][0] == "Flash":
                                    button1[i] = 127
                                    console.command(f"Flash Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                                elif button_types[i][0] == "Temp":
                                    button1[i] = 127
                                    console.command(f"Temp Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                                elif button_types[i][0] == "Go":
                                    console.command(f"Go Executor {page+1}.{i+1}")
                                elif button_types[i][0] == "GoBack":
                                    console.command(f"GoBack Executor {page+1}.{i+1}")
                                elif button_types[i][0] == "Pause":
                                    console.command(f"Pause Executor {page+1}.{i+1}")
                                elif button_types[i][0] == "Learn":
                                    console.command(f"Learn Executor {page+1}.{i+1}")
                                elif button_types[i][0] == "Select":
                                    console.command(f"Select Executor {page+1}.{i+1}")
                                elif button_types[i][0] == "Swop":
                                    button1[i] = 127
                                    console.command(f"Swop Executor {page+1}.{i+1}")
                                    send_note(note, 127)
                            elif note == 58 + i and console:
                                if not work_buttons["store"]:
                                    console.command(f"Group {i+1}")
                                else:
                                    console.command(f"Store Group {i+1}")
                                    work_buttons["store"] = False
                                    send_note(work_buttons_code["store"], 0)
                        ##Sonstige Tasten
                        if note == 93 and console: ## Fader Bank >
                            page += 1
                            fill_displays()
                        if note == 92 and console: ## Fader Bank <
                            if page > 0:
                                page -= 1
                                fill_displays()
                        if note == 87 and console: ## <<
                            console.command("GoBack")
                        if note == 88 and console: ## >>
                            console.command("Go")
                        if note == 90 and console: ## |>
                            console.command("Pause")
                        if note == 71 and console: ## Save
                            work_buttons["store"] = not work_buttons["store"]
                            if work_buttons["store"]:
                                send_note(note, 64)
                                for i, v in work_buttons.items():
                                    if not i == "store":
                                        work_buttons[i] = False
                            else:
                                send_note(note, 0)
                        if note == 83 and console: ## Delete
                            work_buttons["delete"] = not work_buttons["delete"]
                            if work_buttons["delete"]:
                                send_note(note, 64)
                                for i, v in work_buttons.items():
                                    if not i == "delete":
                                        work_buttons[i] = False
                            else:
                                send_note(note, 0)
                        if note == 84 and console: ## Replace
                            work_buttons["move"] = not work_buttons["move"]
                            if work_buttons["move"]:
                                multi_select_work_buttons["move"] = []
                                send_note(note, 64)
                                for i, v in work_buttons.items():
                                    if not i == "move":
                                        work_buttons[i] = False
                            else:
                                send_note(note, 0)
                                multi_select_work_buttons["move"] = []
                        if note == 78 and console: ## Cancel
                            console.command("Clear")
                            clear = not clear
                            if clear:
                                send_note(78, 64)
                            else:
                                send_note(78, 0)
                        if note == 72 and console: ## Undo
                            console.command("Oops@")
                        if note == 79 and console: ## Enter
                            console.command("Please@")
                        if note == 70 and console: ## Trim
                            console.command("Fixture@")
                        if note == 77 and console: ## Group
                            console.command("Group@")
                        if note == 94 and console: ## Channel <
                            console.command("Previous")
                        if note == 95 and console: ## Channel >
                            console.command("Next")
                        if note == 98 and console: ## Pfeiltaste <
                            console.command("Previous")
                        if note == 99 and console: ## Pfeiltaste >
                            console.command("Next")
                        if note == 96 and console: ## Pfeiltaste hoch
                            console.command("Up")
                        if note == 97 and console: ## Pfeiltaste runter
                            console.command("Down")
                        if note == 100 and console: ## Pfeiltaste mitte
                            console.command("MAtricks Toggle")
                        if note == 0 and console: ## Klick auf Drehregler 1
                            if speed["pan"] == 1:
                                speed["pan"] = 10
                            else:
                                speed["pan"] = 1
                        if note == 1 and console: ## Klick auf Drehregler 2
                            if speed["tilt"] == 1:
                                speed["tilt"] = 10
                            else:
                                speed["tilt"] = 1
                        if note == 2 and console: ## Klick auf Drehregler 3
                            if speed["dim"] == 1:
                                speed["dim"] = 10
                            else:
                                speed["dim"] = 1
                        if note == 3 and console: ## Klick auf Drehregler 4
                            if speed["shutter"] == 10:
                                speed["shutter"] = 20
                            else:
                                speed["shutter"] = 10
                        if note == 5 and console: ## Klick auf Drehregler 6
                            if speed["R"] == 10:
                                speed["R"] = 20
                            else:
                                speed["R"] = 10
                        if note == 6 and console: ## Klick auf Drehregler 7
                            if speed["G"] == 10:
                                speed["G"] = 20
                            else:
                                speed["G"] = 10
                        if note == 7 and console: ## Klick auf Drehregler 8
                            if speed["B"] == 10:
                                speed["B"] = 20
                            else:
                                speed["B"] = 10
                        if note == 57 and console: ## FLIP
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
                        if note == 69 and console: ###WRITE
                            work_buttons["select_for_lable"] = not work_buttons["select_for_lable"]
                            if work_buttons["select_for_lable"]:
                                send_note(note, 64)
                                for i, v in work_buttons.items():
                                    if not i == "select_for_lable":
                                        work_buttons[i] = False
                            else:
                                send_note(note, 0)
                        if note in commands:
                            console.command(commands[note])
                        if note >=110 and note <=117 and any(work_buttons.values()): ## Fader als Knopf
                            for i, v in work_buttons.items():
                                if v:
                                    if i == "select_for_lable":
                                        get_name(page, note-110)
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "store":
                                        if fader_names[page][note-110] != "":
                                            messagebox.showerror("Speicherfehler", "Zum Speichern belegter Fader bitte die GUI nutzen")
                                        else:
                                            console.command(f"Store ExecButton2 {page + 1}.{note - 109}")
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "delete":
                                        console.command(f"Delete ExecButton2 {page + 1}.{note - 109}")
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "move":
                                        multi_select_work_buttons["move"].append([page+1, note-109])
                                        if len(multi_select_work_buttons["move"]) == 2:
                                            work_buttons[i] = False
                                            send_note(work_buttons_code[i], 0)
                                            e1 = multi_select_work_buttons["move"][0]
                                            e2 = multi_select_work_buttons["move"][1]
                                            console.command(f"Move ExecButton2 {e1[0]}.{e1[1]} AT {e2[0]}.{e2[1]}")
                                            fader_names[e2[0]-1][e2[1]-1], fader_names[e1[0]-1][e1[1]-1] = fader_names[e1[0]-1][e1[1]-1], fader_names[e2[0]-1][e2[1]-1]
                                            fader_color[e2[0]-1][e2[1]-1], fader_color[e1[0]-1][e1[1]-1] = fader_color[e1[0] - 1][e1[1] - 1], fader_color[e2[0]-1][e2[1]-1]
                                            fill_displays()
                                            multi_select_work_buttons["move"] = []
                    elif velocity == 0:
                        for i in range(0, 8):
                            if note == 32 + i and console: ## SELECT
                                if button_types[i][1] == "Flash":
                                    button1[i] = 0
                                    console.command(f"Flash Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                                elif button_types[i][1] == "Temp":
                                    button1[i] = 0
                                    console.command(f"Temp Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                                elif button_types[i][1] == "Swop":
                                    button1[i] = 0
                                    console.command(f"Swop Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                            elif note == 24 + i and console: ## SELECT
                                if work_buttons["store"]:
                                    work_buttons["store"] = False
                                    send_note(work_buttons_code["store"], 0)
                                    continue
                                if button_types[i][0] == "Flash":
                                    button1[i] = 0
                                    console.command(f"Flash Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                                elif button_types[i][0] == "Temp":
                                    button1[i] = 0
                                    console.command(f"Temp Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                                elif button_types[i][0] == "Swop":
                                    button1[i] = 0
                                    console.command(f"Swop Off Executor {page+1}.{i+1}")
                                    send_note(note, 0)
                            elif note == 8 + i and console: ## SELECT
                                if work_buttons["store"]:
                                    work_buttons["store"] = False
                                    send_note(work_buttons_code["store"], 0)
                                    continue
                                if button_types_100[i] == "Flash":
                                    button1[i] = 0
                                    console.command(f"Flash Off Executor {page+1}.{i+101}")
                                    send_note(note, 0)
                                elif button_types_100[i] == "Temp":
                                    button1[i] = 0
                                    console.command(f"Temp Off Executor {page+1}.{i+101}")
                                    send_note(note, 0)
                                elif button_types_100[i] == "Swop":
                                    button1[i] = 0
                                    console.command(f"Swop Off Executor {page+1}.{i+101}")
                                    send_note(note, 0)
                            elif note == 16 + i and console: ## SELECT
                                if button_types_200[i] == "Flash":
                                    button1[i] = 0
                                    console.command(f"Flash Off Executor {page+1}.{i+201}")
                                    send_note(note, 0)
                                elif button_types_200[i] == "Temp":
                                    button1[i] = 0
                                    console.command(f"Temp Off Executor {page+1}.{i+201}")
                                    send_note(note, 0)
                                elif button_types_200[i] == "Swop":
                                    button1[i] = 0
                                    console.command(f"Swop Off Executor {page+1}.{i+201}")
                                    send_note(note, 0)
    except Exception as e:
        print(f"1 Fehler beim Öffnen des Lese Ports: {e}")

def send_note(note, velocity, channel=0):
    """Sendet eine Note."""
    try:
        with mido.open_output("X-Touch 1") as outport:
            msg = Message("note_on", note=note, velocity=velocity)
            outport.send(msg)
    except Exception as e:
        print(f"2 Fehler beim Öffnen des Ports (Send Note): {e}")
        send_note(note, velocity, channel)
def send_control_change(control, value, channel=0):
    """Sendet eine Control Change Nachricht an den angegebenen MIDI-Ausgangsport."""
    try:
        with mido.open_output("X-Touch 1") as outport:
            msg = Message('control_change', control=control, value=value, channel=channel)
            outport.send(msg)
    except Exception as e:
        print(f"3 Fehler beim Öffnen des Ports (Send CC): {e}")
        send_control_change(control, value, channel)

def send_sysex(sysex):
    try:
        with mido.open_output("X-Touch 1") as outport:
            msg = Message.from_bytes(sysex)
            outport.send(msg)
    except Exception as e:
        print(f"4 Fehler beim Öffnen des Ports (Sende Sysex): {e}\tSysex: {sysex}")
        send_sysex(sysex)

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
                time.sleep(0.1)  # Update alle 0.1 Sekunden

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
