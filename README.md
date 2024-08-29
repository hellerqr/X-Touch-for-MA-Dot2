<h1>Acknowledgements</h1>
<p>Thanks to <a href="https://github.com/ArtGateOne">ArtGateOne</a> for the <a href="https://github.com/ArtGateOne/dot2bcf2000">dot2bcf2000</a> software, which was the inspiration for the code.</p>
<p>Thanks to <a href="https://github.com/linusgke">Linus Groschke</a> for the <a href="https://github.com/linusgke/pyMAdot2">pyMAdot2</a> software, whis also was an inspiration for the code.
<p>Thanks to the Förderverein of the <a href="https://gymnasium-koeln-pesch.de/">Gymnasium Köln Pesch</a> for taking over the acquisition costs of the Behringer X Touch for use in the "AG für Veranstaltungstechnik".</p>
<h1>How to make the software ready for operation</h1>
<ul>
  <li>Connect Behringer X-Touch via USB</li>
  <li>Start Dot2 on pc</li>
  <li>Start dot2.py</li>
</ul>

<h1>Functions of the software</h1>
<h2>Encoder</h2>
<li>Encoder 1: PAN</li>
<li>Encoder 2: Tilt</li>
<li>Encoder 3: Dimmer</li>
<li>Encoder 4 & 5: unused at the time</li>
<li>Encoder 6: Red</li>
<li>Encoder 7: Green</li>
<li>Encoder 8: Blue</li>
<li>Big Encoder: Dimmer</li>
<h2>Fader</h2>
<li>Fader 1 - 8: Executorfader from dot2</li>
<li>Fader 9: Master Dimmer (! Attention: Software-based changes don't change the fader Value</li>
<h2>Buttons</h2>
<ul>
  <li>Buttons on top of faders</li>
    <ul>
      <li>Select: Lowest button among the executor faders</li>
      <li>Mute: Button among the executor faders</li>
      <li>Solo: Executor 201 - 209</li>
      <li>Rec: Executor 101 - 109</li>
      <li>FLIP:</li>
      <ul>
        <li>When Master is at 100: Activate Blackoff</li>
        <li>When Master is not at 100: Diable Blackoff</li>
      </ul>
    </ul>
  <li>Encoder</li>
    <ul>
      <li>By clicking on the encoder you can choose between two step sizes</li>
    </ul>
  <li>Faderbank:</li>
  <ul>
    <li>`<`: Privios Page</li>
    <li>`>`: Next Page</li>
  </ul>
  <li>Channel</li>
  <ul>
    <li>`<`: Privios</li>
    <li>`>`: Next</li>
  </ul>
  <li>Drop: Delete</li>
  <ul>
    <li>Click on Drop</li>
    <li>Place your finger on the fader you want to delete</li>
  </ul>
  <li>Replace: Move</li>
    <ul>
      <li>Click on Move</li>
      <li>Place your finger on the fader you want to move</li>
      <li>Place your finger on the fader that is to be used in the future</li>
    </ul>
  <li>Write: Lable</li>
      <ul>
        <li>Click on Write</li>
        <li>Place your finger on the fader you want to name</li>
      </ul>
  <li><li>Save: Store</li>
      <ul>
        <li>Place your finger on the fader you want to save to <b>OR</b></li>
        <li>Select a button F1 to F8 to save selected lamps to a group</li>
      </ul>
  <li>Funktion</li>
      <ul>
        <li>F1 - F8: Group 1 - Group 8</li>
      </ul>
  <li>"Joystick" Buttons</li>
      <ul>
        <li>Up: Up</li>
        <li>Down: Down</li>
        <li>Left: Previos</li>
        <li>Right: Next</li>
        <li>Middel: Set</li>
      </ul>
  <li>Cancel: Clear (Press twice like press clear button twice)</li>
  <li>Undo: Oops</li>
  <li>Enter: Please</li>
</ul>

<h1>Simple Bug Fixing</h1>
<h2>"X-Touch 1" Or "X-Touch 0" is not a valid MIDI out-/input</h2>
Please run midi.py and look to the labels of the Behringer X-Touch device, change the value of "in_port" and "out_port" in line 29 and 30 in dot2.py
<h2>Any other Error</h2>
<ul>
  <li>Please try to restart your full system</li>
  <li>Fill an Issue with a screenshot and discription of the error</li>
</ul>
<h1>You want to use another button?</h1>
Create an issue with the note of the button and describe the desired function
