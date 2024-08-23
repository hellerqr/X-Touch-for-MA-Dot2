import time
import aiohttp
import asyncio
import json
import hashlib
import time
import mido
from mido import Message

def send_control_change(control, value, channel=0):
    """ Sendet eine Control Change Nachricht an den angegebenen MIDI-Ausgangsport. """
    try:
        with mido.open_output("X-Touch 1") as outport:
            msg = Message('control_change', control=control, value=value, channel=channel)
            outport.send(msg)
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")
def send_note(note, velocity, channel=0):
    """ Sendet eine Note"""
    try:
        with mido.open_output("X-Touch 1") as outport:
            msg = Message("note_on", note=note, velocity=velocity)
            outport.send(msg)
            print(f"Gesendet: {msg}")
    except Exception as e:
        print(f"Fehler beim Öffnen des Ports: {e}")


class Dot2:
    def __init__(self, session: aiohttp.ClientSession, address: str, password: str):
        self.session = session
        self.address = address
        self.password = hashlib.md5(password.encode("utf-8")).hexdigest()
        self._initializing = False
        self._readyEvent = asyncio.Event()
        self.initialized = False

    @classmethod
    async def create(
            cls, session: aiohttp.ClientSession, address: str, password: str
    ):
        instance = cls(session, address, password)
        await instance.initialize()
        return instance

    async def initialize(self) -> None:
        """Initialize socket."""
        if self._initializing or self.initialized:
            raise RuntimeError("Currently initializing or already initialized")

        self._initializing = True
        self.initialized = False

        self.ws = await self.session.ws_connect(f"ws://{self.address}/?ma=1")
        self.listen_task = asyncio.create_task(self.listen())

        await self._readyEvent.wait()

        self.initialized = True
        self._initializing = False
        print("Connected")

    async def disconnect(self) -> None:
        await self.send({"requestType": "close", "session": self.session_id})
        self.listen_task.cancel()

    async def listen(self) -> None:
        while True:
            message = await self.ws.receive()
            if self.initialized:
                #await self.send({"requestType": "getdata", "data": "set", "session": self.session_id, "maxRequests": 1})
                await self.send({"requestType": "playbacks", "startIndex": [0, 101, 201], "itemsCount": [6, 6, 6], "pageIndex": 1, "itemsType": [2, 3, 3], "view": 2, "execButtonViewMode": 1, "buttonsViewMode": 0, "session": self.session_id, "maxRequests": 1})

            if message.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(message.data)
                if "status" in data:
                    await self.send({"session": 0, "maxRequests": 0})

                if "session" in data:
                    self.session_id = data["session"]

                if "forceLogin" in data:
                    await self.send({"requestType": "login", "username": "remote", "password": self.password,
                                     "session": self.session_id, "maxRequests": 0})
                if "responseType" in data:
                    # print(data["responseType"])
                    self._readyEvent.set()
                    if data["responseType"] == "login":
                        print("login successful")
                    if data["responseType"] == "playbacks":

                        for i in range(3):
                            send_control_change(70 + i, int(data["itemGroups"][0]["items"][i][0]["executorBlocks"][0]["fader"]["v"]*127))
                        #print(data["itemGroups"][0]["items"][0][0]["executorBlocks"][0]["fader"]["v"], data["itemGroups"][0]["items"][1][0]["executorBlocks"][0]["fader"]["v"], end="")
                        #print(data)

    async def send(self, payload: dict) -> None:
        await self.ws.send_str(json.dumps(payload, separators=(',', ':')))

    async def command(self, command) -> None:
        await self.send({"requestType": "command", "command": command, "session": self.session_id, "maxRequests": 0})

    async def pan(self, val):
        await self.send({"requestType": "encoder", "name": "PAN", "value": val, "session": self.session_id, "maxRequests": 0})

    async def tilt(self, val):
        await self.send({"requestType": "encoder", "name": "TILT", "value": val, "session": self.session_id, "maxRequests": 0})


    async def fade(self, fadernum, value):
        await self.send({"requestType": "playbacks_userInput", "execIndex": fadernum, "pageIndex": 0, "faderValue": value, "type": 1, "session": self.session_id, "maxRequests": 0})



    async def specialmaster(self, num, val):
        print(1)
        await self.send(
            {"requestType": "command", "command": f"SpecialMaster {num} At {val}", "session": self.session_id, "maxRequests": 0})

    async def button(self, button):
        await self.send({"requestType": "playbacks_userInput", "cmdline": "", "execIndex": 200, "pageIndex": 0, "buttonId": 0, "pressed": True, "released": True, "type": 0, "session": self.session_id, "maxRequests": 0})


async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)

async def run(session):
    console = await Dot2.create(
        session,
        "127.0.0.1",
        ""
    )
    print(1)
    #await console.fade(1, 1.0)
    await console.button(201)
    await asyncio.sleep(30)
    print(2)
    await console.disconnect()
    print(3)
asyncio.run(main())
