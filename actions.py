def big_wheel(value, console, send_control_change):
    if value == 1:
        console.encoder("DIM", -5)
    if value == 65:
        console.encoder("DIM", 5)


def wheel1(value, console, send_control_change, speed, update):
    if value == 1:
        console.pan(-speed["pan"])
    if value == 65:
        console.pan(speed["pan"])
    update("pan")


def wheel2(value, console, send_control_change, speed, update):
    if value == 1:
        console.tilt(-speed["tilt"])
    if value == 65:
        console.tilt(speed["tilt"])
    update("tilt")


def wheel3(value, console, send_control_change, speed, update):
    if value == 1:
        console.dim(-speed["dim"])
    if value == 65:
        console.dim(speed["dim"])
    update("dim")


def wheel4(value, console, send_control_change, speed, update):
    if value == 1:
        console.shutter(-speed["shutter"])
    if value == 65:
        console.shutter(speed["shutter"])
    update("shutter")


def wheel5(value, console, send_control_change, speed, update):
    if value == 1:
        console.encoder("zoom", -speed["ZOOM"])
    if value == 65:
        console.encoder("zoom", speed["ZOOM"])
    update("zoom")


def wheel6(value, console, send_control_change, speed, update):
    if value == 1:
        console.encoder("colorrgb1", -speed["R"])
    if value == 65:
        console.encoder("colorrgb1", speed["R"])
    update("R")


def wheel7(value, console, send_control_change, speed, update):
    if value == 1:
        console.encoder("colorrgb2", -speed["G"])
    if value == 65:
        console.encoder("colorrgb2", speed["G"])
    update("G")


def wheel8(value, console, send_control_change, speed, update):
    if value == 1:
        console.encoder("colorrgb3", -speed["B"])
    if value == 65:
        console.encoder("colorrgb3", speed["B"])
    update("B")


def fader(fader_values, console, control, value, last_fader_change, time):
    if fader_values[control - 70] != value:
        fader_values[control - 70] = value
        last_fader_change[control - 70] = time.time()
        console.fade(control - 70, value / 127)


def special_master(console, value, send_note, master="2.1"):
    console.specialmaster(master, str(int((value / 127) * 100)))
    if str(int((value / 127) * 100)) != "100":
        send_note(57, 64)
        blackout = True
    else:
        blackout = False
        send_note(57, 0)


def nothing(control=None, note=None):
    if control is None and note is not None:
        print("KEINE AKTION HINTERLEGT! NOTE:", note)
    if note is None and control is not None:
        print("KEINE AKTION HINTERLEGT! CONTROL:", control)


def store(work_buttons, send_note, note):
    work_buttons["store"] = not work_buttons["store"]
    if work_buttons["store"]:
        send_note(note, 64)
        for i, v in work_buttons.items():
            if not i == "store":
                work_buttons[i] = False
    else:
        send_note(note, 0)


def delete(work_buttons, send_note, note):
    work_buttons["delete"] = not work_buttons["delete"]
    if work_buttons["delete"]:
        send_note(note, 64)
        for i, v in work_buttons.items():
            if not i == "delete":
                work_buttons[i] = False
    else:
        send_note(note, 0)


def replace(work_buttons, send_note, note, multi_select_work_buttons):
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
