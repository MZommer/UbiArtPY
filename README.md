# UbiArtPY
 Python module for working with the Ubi Art Framework



## Audio Handler
Is important that [`FFMPEG`](https://ffmpeg.org),
both `OpusEncoder` and `OpusDecoder` (you can find this on the NX (Nintendo Switch) SDK),
`DSPADPCM` (you can find this in Wii SDK),
`xma2encode` (you can find this in x360 SDK or on the Durango (XOne) SDK, both work)
and [`vgmstream`](https://github.com/vgmstream/vgmstream/)
are in *`PATH`*.

I cannot provide a download link for any of this.


### Supported platforms:
| Platform | Format | Implemented | 
| :--- | :---: | ---: |
| **PC** | PCM | ✅ |
| **GGP (Google Stadia)** | PCM | ✅ |
| **X360** | XMA2 | ✅ |
| **Durango (XOne)** | XMA2 | ✅ (untested) |
| **XBSX (Series X)** | ❓ | ❓ |
| **PS3** | MP3 | ✅ |
| **PSVita** | AT9 | ❌ |
| **Orbis (PS4)** | PCM | ✅ |
| **Prospero (PS5)** | ❓ | ❓ |
| **PC** | PCM | ✅ |
| **Wii** | DSP | ❌ |
| **Cafe (WiiU)** | DSP | ❌ |
| **Citra (3DS)** | CWAV | ❌ |
| **NX (Nintendo Switch)** | Opus (Nintendo) | ✅ |
### Usage
RAKI is the format of the `cooked` audio files.
This module provides the `RAKI` class.

### Methods

---
`RAKI.Cook(file: path, output: path, platform: str, isAMB: bool=False, Format: str=None)` Cooks the RAKI object

`RAKI.UnCook(file: path, output: path)` UnCooks a RAKI file

`RAKI.UnCookAndCook(file: path, output: path, platform: str)` Reformat a RAKI file into another platform/format

`RAKI.SyncJDUAudio(file: path, output: path, startBeat: int, markers: list[int], amboutput: path=None)`
Syncronizes a JDU audio into a local one



#### Example
The following is a simple example on how to cook an audio.
```py
from UbiArtPY import RAKI
audio = RAKI()
audio.Cook("stargate.wav", "stargate.wav.ckd", "PC")
```

The following is a simple example on how to uncook an audio.
```py
from UbiArtPY import RAKI
RAKI.UnCook("stargate.wav.ckd", "stargate.wav")
```

The following is a simple example on how to UnCook and Cook an audio.
```py
from UbiArtPY import RAKI
RAKI.UnCookAndCook("stargate.wav.ckd", "stargate_wii.wav.ckd", "WII")
```

