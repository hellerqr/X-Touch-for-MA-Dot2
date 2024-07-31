import asyncio
import aiohttp
import mido
from dot2api import Dot2

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            console = await Dot2.create(session, "127.0.0.1", "")
            print("Verbunden mit Dot2")
            await console.fade(0, 1.0)
            await asyncio.create_task(read_midi_messages_sync(console, "X-Touch 0"))
            await asyncio.sleep(30)
            await console.disconnect()
    except Exception as e:
        print(f"Fehler beim Ausführen von main(): {e}")

async def read_midi_messages_sync(console, port_name):
    try:
        with mido.open_input(port_name) as inport:
            print(f"Lese MIDI-Nachrichten von {port_name}...")
            for msg in inport:
                if msg.type == "control_change":
                    value = msg.value / 127
                    control = msg.control
                    await console.fade(0, value)  # Hier wird asyncio.run() sicher innerhalb eines Threads verwendet
    except Exception as e:
        print(f"Fehler beim Öffnen des MIDI-Ports: {e}")

if __name__ == "__main__":
    asyncio.run(main())
