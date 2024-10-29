You can also have a look at the [GERMAN](https://github.com/hellerqr/X-Touch-for-MA-Dot2/blob/master/README_DE.md) instruction.
# Acknowledgements

Thanks to [ArtGateOne](https://github.com/ArtGateOne) for the software [dot2bcf2000](https://github.com/ArtGateOne/dot2bcf2000), which was an inspiration for the code.

Thanks to [Linus Groschke](https://github.com/linusgke) for the software [pyMAdot2](https://github.com/linusgke/pyMAdot2), which also served as an inspiration for the code.

Thanks to the support association of [Gymnasium Köln Pesch](https://gymnasium-koeln-pesch.de/) for covering the acquisition costs of the Behringer X-Touch for use in the "AG für Veranstaltungstechnik".

# How to make the software ready for operation

1. Connect the Behringer X-Touch via USB.
2. Start the controller in the mode CtrlRel USB. 
3. Start `Dot2 on pc`.
4. Start `dot2.py`.

# Functions of the software

## Encoders

- Encoder 1: PAN
- Encoder 2: Tilt
- Encoder 3: Dimmer
- Encoder 4: Fokus
- Encoder 5: Shutter
- Encoder 6: Red
- Encoder 7: Green
- Encoder 8: Blue
- Big Encoder: Dimmer

## Faders

- Fader 1 - 8: Executor faders from dot2
- Fader 9: Master Dimmer (! Attention: Software-based changes do not alter the fader value)

## Buttons

- **Buttons on top of faders:**
  - Select: Lowest button among the executor faders
  - Mute: Button among the executor faders
  - Solo: Executor 201 - 209
  - Rec: Executor 101 - 109
  - FLIP:
    - When the Master is at 100: Activate Blackoff
    - When the Master is not at 100: Disable Blackoff
- **Encoders:**
  - By clicking on the encoder, you can choose between two step sizes.
- **Fader Bank:**
  - `<`: Page -
  - `>`: Page +

  Warning: Don't go past page 99
- **Channel:**
  - `<`: Previous
  - `>`: Next
- **Drop: Delete**
  - Click on "Drop".
  - Place your finger on the fader you want to delete.
- **Replace: Move**
  - Click on "Move".
  - Place your finger on the fader you want to move.
  - Place your finger on the fader that will be used in the future.
- **Write: Label**
  - Click on "Write".
  - Place your finger on the fader you want to name.
  - Use the GUI to type in a label
- **Marker: Colorize**
  - Click on "Marker"
  - Place your finger on the fader you want to colorize.
  - Use the GUI to choose a color
- **Save: Store**
  - Place your finger on the fader you want to save to **OR**
  - Select a button from F1 to F8 to save selected lamps to a group.
- **Function:**
  - F1 - F8: Group 1 - Group 8
- **"Joystick" Buttons:**
  - Up: Up
  - Down: Down
  - Left: Previous
  - Right: Next
  - Middle: Set
- **Cancel: Clear (Press twice like pressing the clear button twice)**
- **Undo: Oops**
- **Enter: Please**
- **Encoder Assign**
  - Track: Dimmer Page
  - Pan/Soundaround: Position Page
  - EQ: Gobo Page
  - Send: Color Page
  - Plug-in: Beam Page
  - Inst: Focus Page

# Simple bug fixing

- Please try restarting your entire system.
- Create an issue with a screenshot and a description of the error.
- Please make sure that the controller is in the “CtrlRel USB” module.

# Want to use another button?

Create an issue with the note of the button and describe the desired function.
