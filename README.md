# Spydio
Spydio allows to simulate 3D audio to have a rendering like Dolby Atmos through simple headphones
An audio file with a rotation is available in the "demo" folder (! Headset require !).
The effect can vary from person to person depending on the shape of their head. Do not hesitate to use another HRIR when you initialise Spydio.

## How it's work:
### 1 - Initialise Spydio
```python
from spydio import Spydio
sp = Spydio()
```

### 2 - Open your wav files with Spydio 
```python
song = sp.loadWavFile("test.wav")
```

### 3 - Virtualization operations
```python
song = sp.rotation(song, 120, 250) #To virtualize the song with a rotation (120° -> 250°)
# or
song = sp.spatialize(song, -90) #To spatialize the song at -90° (270°)
```

### 4 - Save when operations are done
```python
sp.saveWavFile(song, 'rot_spatialize')
```
