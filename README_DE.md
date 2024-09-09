# Danksagungen

Vielen Dank an [ArtGateOne](https://github.com/ArtGateOne) für die Software [dot2bcf2000](https://github.com/ArtGateOne/dot2bcf2000), die eine Inspiration für den Code war.

Vielen Dank an [Linus Groschke](https://github.com/linusgke) für die Software [pyMAdot2](https://github.com/linusgke/pyMAdot2), die ebenfalls als Inspiration für den Code diente.

Danke an den Förderverein des [Gymnasium Köln Pesch](https://gymnasium-koeln-pesch.de/) für die Übernahme der Anschaffungskosten des Behringer X-Touch für den Einsatz in der "AG für Veranstaltungstechnik".

# Inbetriebnahme der Software

1. Behringer X-Touch via USB anschließen.
2. Dot2 auf dem PC starten.
3. `dot2.py` starten.

# Funktionen der Software

## Encoder

- Encoder 1: PAN
- Encoder 2: Tilt
- Encoder 3: Dimmer
- Encoder 4 & 5: Derzeit ungenutzt
- Encoder 6: Rot
- Encoder 7: Grün
- Encoder 8: Blau
- Großer Encoder: Dimmer

## Fader

- Fader 1 - 8: Executorfader von Dot2
- Fader 9: Master Dimmer (! Achtung: Softwarebasierte Änderungen ändern nicht den Faderwert)

## Tasten

- **Tasten über den Fadern:**
  - Select: Unterste Taste bei den Executorfadern
  - Mute: Taste bei den Executorfadern
  - Solo: Executor 201 - 209
  - Rec: Executor 101 - 109
  - FLIP:
    - Wenn der Master auf 100 steht: Blackoff aktivieren
    - Wenn der Master nicht auf 100 steht: Blackoff deaktivieren
- **Encoder:**
  - Durch Klicken auf den Encoder kann man zwischen zwei Schrittgrößen wählen.
- **Faderbank:**
  - `<`: Page -
  - `>`: Page +

Warnung: Nicht Seite 99 überschreiten
- **Channel:**
  - `<`: Previous
  - `>`: Next
- **Drop: Löschen**
  - Auf "Drop" klicken.
  - Finger auf den zu löschenden Fader legen.
- **Replace: Verschieben**
  - Auf "Move" klicken.
  - Finger auf den zu verschiebenden Fader legen.
  - Finger auf den zukünftigen Fader legen.
- **Write: Beschriften**
  - Auf "Write" klicken.
  - Finger auf den zu beschriftenden Fader legen.
  - Die GUI benutzen um ein Label einzugeben.
- **Marker: Färben**
  - Auf "Marker" klicken.
  - Finger auf den zu färbenden Fader legen.
  - Die GUI benutzen um eine Farbe zu wählen.
- **Save: Speichern**
  - Finger auf den Fader legen, auf dem gespeichert werden soll **ODER**
  - Eine Taste von F1 bis F8 auswählen, um die ausgewählten Lampen zu einer Gruppe zu speichern.
- **Funktion:**
  - F1 - F8: Group 1 - Group 8
- **"Joystick"-Tasten:**
  - Oben: Up
  - Unten: Down
  - Links: Previos
  - Rechts: Next
  - Mitte: Set
- **Cancel: Clear (Zweimal drücken, wie bei der Clear-Taste)**
- **Undo: Oops**
- **Enter: Please**
- **Encoder Assign**
  - Track: Dimmer Seite
  - Pan/Soundaround: Position Seite
  - EQ: Gobo Seite
  - Send: Color Seite
  - Plug-in: Beam Seite
  - Inst: Fokus Seite

# Einfache Fehlerbehebung

- Bitte versuche, dein gesamtes System neu zu starten.
- Erstelle ein Issue mit einem Screenshot und einer Beschreibung des Fehlers.

# Möchtest du eine andere Taste verwenden?

Erstelle ein Issue mit der gewünschten Taste und beschreibe die gewünschte Funktion.
