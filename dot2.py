import hashlib
import json
import time
import websocket
import threading
from mido import Message
import tkinter as tk
from tkinter import simpledialog, messagebox
import os

import dot2
from midi import *
import actions
import atexit

# Zustand der Tasten und Fader
tasten = [False for _ in range(127)]
fader_values = [0 for _ in range(8)]
last_fader_change = [time.time() for _ in range(8)]
button_100 = [0 for _ in range(8)]
button_200 = [0 for _ in range(8)]
button1 = [0 for _ in range(8)]
button2 = [0 for _ in range(8)]
speed = {"tilt": 1, "pan": 1, "dim": 1, "shutter": 1, "R": 10, "G": 10, "B": 10, "zoom": 1}
speed_view = {"tilt": 80, "pan": 81, "dim": 82, "shutter": 83, "R": 85, "G": 86, "B": 87}
fader_names = [["" for _ in range(8)] for _ in range(100)]
fader_color = [[0 for _ in range(8)] for _ in range(100)]
button_types = [[] for _ in range(8)]
button_types_100 = ["" for _ in range(8)]
button_types_200 = ["" for _ in range(8)]
last_msg = time.time()
server_ready = False
in_port = "X-Touch 0"
out_port = "X-Touch 1"
page = 0
request = 0
counter = 0
clear = False
store = False
select_for_lable = False
blackout = False
work_buttons = {"store": False, "select_for_lable": False, "delete": False, "move": False}
work_buttons_code = {"store": 71, "select_for_lable": 69, "delete": 83, "move": 84}
multi_select_work_buttons = {"move": []}
midioutport = None
if os.path.exists("colors.json"):
    with open('colors.json', 'r') as file:
        fader_color = json.load(file)
if os.path.exists("names.json"):
    with open('names.json', 'r') as file:
        fader_names = json.load(file)


def close_port():
    global midioutport
    if midioutport:
        print("Schließe den MIDI-Port...")
        midioutport.close()
        outport = None


atexit.register(close_port)


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
        with (mido.open_input(in_port) as inport):
            for msg in inport:

                if msg.type == "control_change":
                    value = msg.value
                    control = msg.control
                    if control >= 70 and control <= 77 and console:
                        actions.fader(fader_values, console, control, value, last_fader_change, time)

                    def update_big(action):
                        if speed[action] == 10:
                            send_control_change(speed_view[action], 0)
                        else:
                            send_control_change(speed_view[action], 127)

                    def update_small(action):
                        if speed[action] == 1:
                            send_control_change(speed_view[action], 0)
                        else:
                            send_control_change(speed_view[action], 127)


                    if control >= 78 and control <= 88 and console:
                        actionlist = {
                            78: lambda: actions.special_master(console, value, send_note),
                            79: lambda: actions.nothing(control=control),
                            80: lambda: actions.wheel1(value, console, send_control_change, speed, update_small),
                            81: lambda: actions.wheel2(value, console, send_control_change, speed, update_small),
                            82: lambda: actions.wheel3(value, console, send_control_change, speed, update_small),
                            83: lambda: actions.wheel4(value, console, send_control_change, speed, update_small),
                            84: lambda: actions.wheel5(value, console, send_control_change, speed, update_small),
                            85: lambda: actions.wheel6(value, console, send_control_change, speed, update_big),
                            86: lambda: actions.wheel7(value, console, send_control_change, speed, update_big),
                            87: lambda: actions.wheel8(value, console, send_control_change, speed, update_big),
                            88: lambda: actions.big_wheel(value, console, send_control_change)
                        }
                        actionlist[control]()

                if msg.type == "note_on":
                    note = msg.note
                    velocity = msg.velocity
                    if velocity == 127:
                        if 8 <= note <= 15 and console:
                            if work_buttons["store"]:
                                if button_types_100[note - 8] == "Leer":
                                    console.command(f"Store Executor {page + 1}.{note - 8 + 101}")
                                    send_note(work_buttons_code["store"], 0)
                                    work_buttons["store"] = False
                                else:
                                    messagebox.showerror(title="Speicherfehler",
                                                         message="Nutze zum Speichern auf belegten Fadern die GUI")
                                continue
                            elif work_buttons["delete"]:
                                console.command(f"Delete Executor {page + 1}.{note - 8 + 101}")
                                work_buttons[i] = False
                                send_note(work_buttons_code["delete"], 0)
                                work_buttons["delete"] = False
                                continue
                            elif work_buttons["move"]:
                                multi_select_work_buttons["move"].append([page + 1, note - 8 + 101])
                                if len(multi_select_work_buttons["move"]) == 2:
                                    work_buttons[i] = False
                                    send_note(work_buttons_code[i], 0)
                                    e1 = multi_select_work_buttons["move"][0]
                                    e2 = multi_select_work_buttons["move"][1]
                                    console.command(f"Move Executor {e1[0]}.{e1[1]} AT {e2[0]}.{e2[1]}")
                                    fader_names[e2[0] - 1][e2[1] - 1], fader_names[e1[0] - 1][e1[1] - 1] = \
                                        fader_names[e1[0] - 1][e1[1] - 1], fader_names[e2[0] - 1][e2[1] - 1]
                                    fader_color[e2[0] - 1][e2[1] - 1], fader_color[e1[0] - 1][e1[1] - 1] = \
                                        fader_color[e1[0] - 1][e1[1] - 1], fader_color[e2[0] - 1][e2[1] - 1]
                                    fill_displays()
                                    multi_select_work_buttons["move"] = []
                                continue
                            if button_types_100[note - 8] == "Toggle":
                                if button1[note - 8] != 127:
                                    button1[note - 8] = 127
                                    console.command(f"Toggle Executor {page + 1}.{note - 8 + 101}")
                                    send_note(note, 127)
                                else:
                                    button1[note - 8] = 0
                                    console.command(f"Toggle Executor {page + 1}.{note - 8 + 101}")
                                    send_note(note, 0)
                            elif button_types_100[note - 8] == "Flash":
                                button1[note - 8] = 127
                                console.command(f"Flash Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 127)
                            elif button_types_100[note - 8] == "Temp":
                                button1[note - 8] = 127
                                console.command(f"Temp Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 127)
                            elif button_types_100[note - 8] == "Go":
                                console.command(f"Go Executor {page + 1}.{note - 8 + 101}")
                            elif button_types_100[note - 8] == "GoBack":
                                console.command(f"GoBack Executor {page + 1}.{note - 8 + 101}")
                            elif button_types_100[note - 8] == "Pause":
                                console.command(f"Pause Executor {page + 1}.{note - 8 + 101}")
                            elif button_types_100[note - 8] == "Learn":
                                console.command(f"Learn Executor {page + 1}.{note - 8 + 101}")
                            elif button_types_100[note - 8] == "Select":
                                console.command(f"Select Executor {page + 1}.{note - 8 + 101}")
                            elif button_types_100[note - 8] == "Swop":
                                button1[note - 8] = 127
                                console.command(f"Swop Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 127)
                        elif 16 <= note <= 23 and console:
                            if work_buttons["store"]:
                                if button_types_200[note - 16] == "Leer":
                                    console.command(f"Store Executor {page + 1}.{note - 16 + 201}")
                                    send_note(work_buttons_code["store"], 0)
                                    work_buttons["store"] = False
                                else:
                                    messagebox.showerror(title="Speicherfehler",
                                                         message="Nutze zum Speichern auf belegten Fadern die GUI")
                                continue
                            elif work_buttons["delete"]:
                                console.command(f"Delete Executor {page + 1}.{note - 16 + 201}")
                                send_note(work_buttons_code["delete"], 0)
                                work_buttons["delete"] = False
                                continue
                            elif work_buttons["move"]:
                                multi_select_work_buttons["move"].append([page + 1, note - 16 + 201])
                                if len(multi_select_work_buttons["move"]) == 2:
                                    work_buttons[i] = False
                                    send_note(work_buttons_code[i], 0)
                                    e1 = multi_select_work_buttons["move"][0]
                                    e2 = multi_select_work_buttons["move"][1]
                                    console.command(f"Move Executor {e1[0]}.{e1[1]} AT {e2[0]}.{e2[1]}")
                                    fader_names[e2[0] - 1][e2[1] - 1], fader_names[e1[0] - 1][e1[1] - 1] = \
                                        fader_names[e1[0] - 1][e1[1] - 1], fader_names[e2[0] - 1][e2[1] - 1]
                                    fader_color[e2[0] - 1][e2[1] - 1], fader_color[e1[0] - 1][e1[1] - 1] = \
                                        fader_color[e1[0] - 1][e1[1] - 1], fader_color[e2[0] - 1][e2[1] - 1]
                                    fill_displays()
                                    multi_select_work_buttons["move"] = []
                                    continue
                            if button_types_200[note - 16] == "Toggle":
                                if button1[note - 16] != 127:
                                    button1[note - 16] = 127
                                    console.command(f"Toggle Executor {page + 1}.{note - 16 + 201}")
                                    send_note(note, 127)
                                else:
                                    button1[note - 16] = 0
                                    console.command(f"Toggle Executor {page + 1}.{note - 16 + 201}")
                                    send_note(note, 0)
                            elif button_types_200[note - 16] == "Flash":
                                button1[note - 16] = 127
                                console.command(f"Flash Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 127)
                            elif button_types_200[note - 16] == "Temp":
                                button1[note - 16] = 127
                                console.command(f"Temp Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 127)
                            elif button_types_200[note - 16] == "Go":
                                console.command(f"Go Executor {page + 1}.{note - 16 + 201}")
                            elif button_types_200[note - 16] == "GoBack":
                                console.command(f"GoBack Executor {page + 1}.{note - 16 + 201}")
                            elif button_types_200[note - 16] == "Pause":
                                console.command(f"Pause Executor {page + 1}.{note - 16 + 201}")
                            elif button_types_200[note - 16] == "Learn":
                                console.command(f"Learn Executor {page + 1}.{note - 16 + 201}")
                            elif button_types_200[note - 16] == "Select":
                                console.command(f"Select Executor {page + 1}.{note - 16 + 201}")
                            elif button_types_200[note - 16] == "Swop":
                                button1[note - 16] = 127
                                console.command(f"Swop Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 127)
                        elif 32 <= note <= 39 and console:  ## SELECT
                            if button_types[note - 32][1] == "Toggle":
                                if button1[note - 32] != 127:
                                    button1[note - 32] = 127
                                    console.command(f"Toggle Executor {page + 1}.{note - 32 + 1}")
                                    send_note(note, 127)
                                else:
                                    button1[note - 32] = 0
                                    console.command(f"Toggle Executor {page + 1}.{note - 32 + 1}")
                                    send_note(note, 0)
                            elif button_types[note - 32][1] == "Flash":
                                button1[note - 32] = 127
                                console.command(f"Flash Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 127)
                            elif button_types[note - 32][1] == "Temp":
                                button1[note - 32] = 127
                                console.command(f"Temp Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 127)
                            elif button_types[note - 32][1] == "Go":
                                console.command(f"Go Executor {page + 1}.{note - 32 + 1}")
                            elif button_types[note - 32][1] == "GoBack":
                                console.command(f"GoBack Executor {page + 1}.{note - 32 + 1}")
                            elif button_types[note - 32][1] == "Pause":
                                console.command(f"Pause Executor {page + 1}.{note - 32 + 1}")
                            elif button_types[note - 32][1] == "Learn":
                                console.command(f"Learn Executor {page + 1}.{note - 32 + 1}")
                            elif button_types[note - 32][1] == "Select":
                                console.command(f"Select Executor {page + 1}.{note - 32 + 1}")
                            elif button_types[note - 32][1] == "Swop":
                                button1[note - 32] = 127
                                console.command(f"Swop Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 127)
                        elif 24 <= note <= 31 and console:  ## SELECT
                            if button_types[note - 24][0] == "Toggle":
                                if button1[note - 24] != 127:
                                    button1[note - 24] = 127
                                    console.command(f"Toggle Executor {page + 1}.{note - 24 + 1}")
                                    send_note(note, 127)
                                else:
                                    button1[note - 24] = 0
                                    console.command(f"Toggle Executor {page + 1}.{note - 24 + 1}")
                                    send_note(note, 0)
                            elif button_types[note - 24][0] == "Flash":
                                button1[note - 24] = 127
                                console.command(f"Flash Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 127)
                            elif button_types[note - 24][0] == "Temp":
                                button1[note - 24] = 127
                                console.command(f"Temp Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 127)
                            elif button_types[note - 24][0] == "Go":
                                console.command(f"Go Executor {page + 1}.{note - 24 + 1}")
                            elif button_types[note - 24][0] == "GoBack":
                                console.command(f"GoBack Executor {page + 1}.{note - 24 + 1}")
                            elif button_types[note - 24][0] == "Pause":
                                console.command(f"Pause Executor {page + 1}.{note - 24 + 1}")
                            elif button_types[note - 24][0] == "Learn":
                                console.command(f"Learn Executor {page + 1}.{note - 24 + 1}")
                            elif button_types[note - 24][0] == "Select":
                                console.command(f"Select Executor {page + 1}.{note - 24 + 1}")
                            elif button_types[note - 24][0] == "Swop":
                                button1[note - 24] = 127
                                console.command(f"Swop Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 127)
                        elif 58 <= note <= 65 and console:
                            if not work_buttons["store"]:
                                console.command(f"Group {note - 58 + 1}")
                            else:
                                console.command(f"Store Group {note - 58 + 1}")
                                work_buttons["store"] = False
                                send_note(work_buttons_code["store"], 0)

                        ##Sonstige Tasten
                        def nextpage():
                            global page
                            page += 1
                            fill_displays()

                        def prevpage():
                            global page
                            if page > 0:
                                page -= 1
                                fill_displays()

                        def wheel_button_little_speed(action):
                            if speed[action] == 1:
                                speed[action] = 10
                                send_control_change(speed_view[action], 127)
                            else:
                                speed[action] = 1
                                send_control_change(speed_view[action], 0)

                        def wheel_button_large_speed(action):
                            if speed[action] == 10:
                                speed[action] = 20
                                send_control_change(speed_view[action], 127)
                            else:
                                speed[action] = 10
                                send_control_change(speed_view[action], 0)

                        def clear():
                            global clear
                            console.command("Clear")
                            clear = not clear
                            if clear:
                                send_note(78, 64)
                            else:
                                send_note(78, 0)

                        def flip():
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

                        def write():
                            work_buttons["select_for_lable"] = not work_buttons["select_for_lable"]
                            if work_buttons["select_for_lable"]:
                                send_note(note, 64)
                                for i, v in work_buttons.items():
                                    if not i == "select_for_lable":
                                        work_buttons[i] = False
                            else:
                                send_note(note, 0)

                        actionlist = {
                            70: lambda: console.command("Fixture@"),
                            71: lambda: actions.store(work_buttons, send_note, note),
                            72: lambda: console.command("Oops@"),
                            77: lambda: console.command("Group@"),
                            78: lambda: clear(),
                            79: lambda: console.command("Please@"),
                            83: lambda: actions.delete(work_buttons, send_note, note),
                            84: lambda: actions.replace(work_buttons, send_note, note, multi_select_work_buttons),
                            87: lambda: console.command("GoBack"),
                            88: lambda: console.command("Go"),
                            90: lambda: console.command("Pause"),
                            92: lambda: prevpage(),
                            93: lambda: nextpage(),
                            94: lambda: console.command("Previous"),
                            95: lambda: console.command("Next"),
                            96: lambda: console.command("Up"),
                            97: lambda: console.command("Down"),
                            98: lambda: console.command("Previous"),
                            99: lambda: console.command("Next"),
                            100: lambda: console.command("MAtricks Toggle"),
                            0: lambda: wheel_button_little_speed("tilt"),
                            1: lambda: wheel_button_little_speed("pan"),
                            2: lambda: wheel_button_little_speed("dim"),
                            3: lambda: wheel_button_little_speed("shutter"),
                            4: lambda: wheel_button_little_speed("zoom"),
                            5: lambda: wheel_button_large_speed("R"),
                            6: lambda: wheel_button_large_speed("G"),
                            7: lambda: wheel_button_large_speed("B"),
                            40: lambda: console.command('PresetType "Dimmer"'),
                            41: lambda: console.command('PresetType "Position"'),
                            42: lambda: console.command('PresetType "Gobo"'),
                            43: lambda: console.command('PresetType "Color"'),
                            44: lambda: console.command('PresetType "Beam"'),
                            45: lambda: console.command('PresetType "Control"'),
                            57: lambda: flip(),
                            69: lambda: write()
                        }
                        if note >= 0 and note <= 100 and console:
                            if note in actionlist:
                                actionlist[note]()
                            else:
                                if not 8 <= note <= 39 and not 58 <= note <= 65:
                                    actions.nothing(note=note)

                        if note >= 110 and note <= 117 and any(work_buttons.values()):  ## Fader als Knopf
                            for i, v in work_buttons.items():
                                if v:
                                    if i == "select_for_lable":
                                        get_name(page, note - 110)
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "store":
                                        if fader_names[page][note - 110] != "":
                                            messagebox.showerror("Speicherfehler",
                                                                 "Zum Speichern belegter Fader bitte die GUI nutzen")
                                        else:
                                            console.command(f"Store Executor {page + 1}.{note - 109}")
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "delete":
                                        console.command(f"Delete Executor {page + 1}.{note - 109}")
                                        work_buttons[i] = False
                                        send_note(work_buttons_code[i], 0)
                                    elif i == "move":
                                        multi_select_work_buttons["move"].append([page + 1, note - 109])
                                        if len(multi_select_work_buttons["move"]) == 2:
                                            work_buttons[i] = False
                                            send_note(work_buttons_code[i], 0)
                                            e1 = multi_select_work_buttons["move"][0]
                                            e2 = multi_select_work_buttons["move"][1]
                                            console.command(f"Move Executor {e1[0]}.{e1[1]} AT {e2[0]}.{e2[1]}")
                                            fader_names[e2[0] - 1][e2[1] - 1], fader_names[e1[0] - 1][e1[1] - 1] = \
                                            fader_names[e1[0] - 1][e1[1] - 1], fader_names[e2[0] - 1][e2[1] - 1]
                                            fader_color[e2[0] - 1][e2[1] - 1], fader_color[e1[0] - 1][e1[1] - 1] = \
                                            fader_color[e1[0] - 1][e1[1] - 1], fader_color[e2[0] - 1][e2[1] - 1]
                                            fill_displays()
                                            multi_select_work_buttons["move"] = []
                    elif velocity == 0:
                        if note >= 32 and note <= 39 and console:  ## SELECT
                            if button_types[note - 32][1] == "Flash":
                                button1[note - 32] = 0
                                console.command(f"Flash Off Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 0)
                            elif button_types[note - 32][1] == "Temp":
                                button1[note - 32] = 0
                                console.command(f"Temp Off Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 0)
                            elif button_types[note - 32][1] == "Swop":
                                button1[note - 32] = 0
                                console.command(f"Swop Off Executor {page + 1}.{note - 32 + 1}")
                                send_note(note, 0)
                        elif note >= 24 and note <= 31 and console:  ## SELECT
                            if work_buttons["store"]:
                                work_buttons["store"] = False
                                send_note(work_buttons_code["store"], 0)
                                continue
                            if button_types[note - 24][0] == "Flash":
                                button1[note - 24] = 0
                                console.command(f"Flash Off Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 0)
                            elif button_types[note - 24][0] == "Temp":
                                button1[note - 24] = 0
                                console.command(f"Temp Off Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 0)
                            elif button_types[note - 24][0] == "Swop":
                                button1[note - 24] = 0
                                console.command(f"Swop Off Executor {page + 1}.{note - 24 + 1}")
                                send_note(note, 0)
                        elif note >= 8 and note <= 15 and console:  ## SELECT
                            if work_buttons["store"]:
                                work_buttons["store"] = False
                                send_note(work_buttons_code["store"], 0)
                                continue
                            if button_types_100[note - 8] == "Flash":
                                button1[note - 8] = 0
                                console.command(f"Flash Off Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 0)
                            elif button_types_100[note - 8] == "Temp":
                                button1[note - 8] = 0
                                console.command(f"Temp Off Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 0)
                            elif button_types_100[note - 8] == "Swop":
                                button1[note - 8] = 0
                                console.command(f"Swop Off Executor {page + 1}.{note - 8 + 101}")
                                send_note(note, 0)
                        elif note >= 16 and note <= 23 and console:  ## SELECT
                            if button_types_200[note - 16] == "Flash":
                                button1[note - 16] = 0
                                console.command(f"Flash Off Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 0)
                            elif button_types_200[note - 16] == "Temp":
                                button1[note - 16] = 0
                                console.command(f"Temp Off Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 0)
                            elif button_types_200[note - 16] == "Swop":
                                button1[note - 16] = 0
                                console.command(f"Swop Off Executor {page + 1}.{note - 16 + 201}")
                                send_note(note, 0)
    except Exception as e:
        print(f"1 Fehler beim Öffnen des Lese Ports: {e}")


def send_note(note, velocity, channel=0):
    global midioutport
    """Sendet eine Note."""
    try:
        msg = Message("note_on", note=note, velocity=velocity)
        midioutport.send(msg)
    except Exception as e:
        print(f"2 Fehler beim Öffnen des Ports (Send Note): {e}")
        send_note(note, velocity, channel)


def send_control_change(control, value, channel=0):
    """Sendet eine Control Change Nachricht an den angegebenen MIDI-Ausgangsport."""
    global midioutport
    try:
        msg = Message('control_change', control=control, value=value, channel=channel)
        midioutport.send(msg)
    except Exception as e:
        print(f"3 Fehler beim Öffnen des Ports (Send CC): {e}")
        send_control_change(control, value, channel)


def send_sysex(sysex):
    global midioutport
    try:
        msg = Message.from_bytes(sysex)
        midioutport.send(msg)
    except Exception as e:
        print(f"4 Fehler beim Öffnen des Ports (Sende Sysex): {e}\tSysex: {sysex}")


def time_to_sysex():
    print("Uhrzeitanzeige gestartet!")

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

            global page
            page_str = str(page + 1).zfill(2)  # Ensure 'page' is two digits, adding leading zero if necessary
            page_segment_data = [segment_map[digit] for digit in page_str]

            # Add two empty segments at the beginning
            segment_data = page_segment_data + [0] + segment_data  ###WHEN NOT WORKING: [0,0,0] + segment_data

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
    if fader_color[lpage][lnum] % 8 == 0:
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
        global server_ready
        data = json.loads(message)
        request += 1
        if request >= 9:  #No idea what it does, but it's important not to touch it
            self.send({"session": self.session_id})
            self.send({"requestType": "getdata", "data": "set", "session": self.session_id, "maxRequests": 1})
            request = 0
        if "status" in data:
            if data["status"] == "server ready":
                print("Server ready")
                server_ready = True
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
            self.send(
                {"requestType": "login", "username": "remote", "password": self.password, "session": self.session_id,
                 "maxRequests": 0})

        if "responseType" in data:
            if data["responseType"] == "login":
                print("Login erfolgreich")
                self.start_update_interval()
            if data["responseType"] == "playbacks":
                for i in range(8):
                    new_value = int(data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["fader"]["v"] * 127)
                    if last_fader_change[i] + 0.5 < time.time():
                        if fader_values[i] != new_value:
                            send_control_change(70 + i, new_value)
                            fader_values[i] = new_value
                    is_emty = data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["fader"]["max"] == 0
                    button_types[i] = [data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["button1"]["t"],
                                       data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["button2"]["t"]]
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
                    """new_value = int(data["itemGroups"][2]["items"][i][0]["isRun"] * 127)
                    if button_200[i] != new_value:
                        send_note(16 + i, new_value)
                        button_200[i] = new_value"""
                    send_note(16+i, int(data["itemGroups"][2]["items"][i][0]["isRun"] * 127))
                for i in range(8):
                    """new_value = int(data["itemGroups"][1]["items"][i][0]["isRun"] * 127)
                    if button_100[i] != new_value:
                        send_note(8 + i, new_value)
                        button_100[i] = new_value"""
                    send_note(8 + i, int(data["itemGroups"][1]["items"][i][0]["isRun"] * 127))
                for i in range(8):
                    """new_value = int(data["itemGroups"][0]["items"][i][0]["isRun"] * 127)
                    if button1[i] != new_value:
                        send_note(32 + i, new_value)
                        button1[i] = new_value"""
                    send_note(32 + i, int(data["itemGroups"][0]["items"][i][0]["isRun"] * 127))

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
        self.send(
            {"requestType": "encoder", "name": "TILT", "value": val, "session": self.session_id, "maxRequests": 0})

    def dim(self, val):
        self.send({"requestType": "encoder", "name": "DIM", "value": val, "session": self.session_id, "maxRequests": 0})

    def shutter(self, val):
        self.send(
            {"requestType": "encoder", "name": "SHUTTER", "value": val, "session": self.session_id, "maxRequests": 0})

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
        self.send(
            {"requestType": "playbacks_userInput", "cmdline": "", "execIndex": button, "pageIndex": page, "buttonId": 0,
             "pressed": True, "released": False, "type": 0, "session": self.session_id, "maxRequests": 0})


def midi_connection_test():
    global in_port, out_port, midioutport
    midi_inputs = mido.get_input_names()
    midi_outputs = mido.get_output_names()
    for i in midi_inputs:
        if i.startswith('X-Touch'):
            print("MIDI Input gefunden! Input device:", i)
            in_port = i
            break
    else:
        print("Kein kompatibler Controller als Eingabegerät gefunden")
        exit()
    for i in midi_outputs:
        if i.startswith('X-Touch'):
            print("MIDI Output gefunden! Output device:", i)
            out_port = i
            break
    else:
        print("Kein kompatibler Controller als Ausgabegerät gefunden")
        exit()
    try:
        if midioutport is None:
            midioutport = mido.open_output(out_port)
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")
        exit()


def main():
    midi_connection_test()
    console = Dot2("127.0.0.1", "")
    console.connect()
    time.sleep(1)
    send_control_change(78, 127)
    console.specialmaster("2.1", "100")
    time_to_sysex()
    fill_displays()
    try:
        while True:
            read_midi_messages(console)
    except KeyboardInterrupt:
        close_port()
        console.ws.close()


if __name__ == "__main__":
    main()
