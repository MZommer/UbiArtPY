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


Supported platforms:
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
