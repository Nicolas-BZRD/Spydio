import os
import numpy as np
from numpy.lib.function_base import gradient
import scipy.io.wavfile as spiow
from SOFASonix import SOFAFile
from scipy import signal

class WavSpydio:
    """
    WavSpydio
    =====

    Provides an object used to store and manage a .wav file within the Spydio
    library.
    """

    def __init__(self, path:str, **kwargs):
        """
        Create an object of type WavSpydio. A WavSpydio object is used 
        to store and manage a wav file within the Spydio library.

        Parameters
        ----------
        path: str
            Path to the wav file you wish to open.
        **kwargs: Any, optional (not recommended)
            To create your own WavSpydio.
            Set the path parameter to None, then enter the sample rates
            of the audio file you want and the audio samples array.

        Examples
        --------
        >>> wavSpp = WavSpydio("path/file.wav")
        >>> wavSpp = WavSpydio(None, song=[samples], song_sr=44100)
        """
        if path != None:
            self.song_sr, self.song = spiow.read(path)
            self.song = np.asarray(self.song)
            self.spDuration = len(self.song)
            self.duration = self.spDuration/self.song_sr
            self.dim = self.song[0].size
        else:
            self.song_sr = kwargs["song_sr"]
            self.song = kwargs["song"]
            self.spDuration = len(self.song)
            self.duration = self.spDuration/self.song_sr
            self.dim = self.song[0].size

class Spydio:
    def __init__(self, HRIR:int=0, verbose:bool=False):
        self.sofaFile = SOFAFile.load(os.path.dirname(os.path.abspath(__file__))+"/HRIR/{}.sofa".format(HRIR), verbose=False)
        self.HRIR = self.sofaFile.data_ir
        if verbose: 
            print(self.sofaFile.getParam('GLOBAL:ListenerDescription'))
            print(self.sofaFile.getParam("GLOBAL:Comment"))

    def spatialize(self, wavSpydio:WavSpydio, azimuth:int, elevation:int=4, channel:int=0):
        if elevation > 8 or elevation < 0: elevation = 4
        if azimuth < 0 or azimuth > 360: azimuth = azimuth%360

        if azimuth == 360: azimuth = 0
        else: azimuth = (360-azimuth)//5

        if wavSpydio.dim == 1:
            processedL = np.array(signal.fftconvolve(wavSpydio.song[:], self.HRIR[(72*elevation)+azimuth][0][:]))
            processedR = np.array(signal.fftconvolve(wavSpydio.song[:], self.HRIR[(72*elevation)+azimuth][1][:]))
        else:
            processedL = np.array(signal.fftconvolve(wavSpydio.song[:,channel], self.HRIR[(72*elevation)+azimuth][0][:]))
            processedR = np.array(signal.fftconvolve(wavSpydio.song[:,channel], self.HRIR[(72*elevation)+azimuth][1][:]))

        song = np.array([processedL, processedR]).transpose()
        return WavSpydio(path=None, song=song, song_sr=wavSpydio.song_sr)

    def rotation(self, wavSpydio:WavSpydio, azimuthStart:int, azimuthEnd:int, elevationStart:int=4, elevationEnd:int=4, channel:int=0, clockwiseRotation:bool=True):
        azimuthStart = (5*round(azimuthStart/5))%360
        azimuthEnd = (5*round(azimuthEnd/5))%360
        azimuthVariation = azimuthEnd - azimuthStart

        if(azimuthStart>azimuthEnd and clockwiseRotation): azimuthVariation = (360-azimuthStart)+azimuthEnd
        elif(azimuthStart<azimuthEnd and not clockwiseRotation): azimuthVariation = (360-azimuthEnd)+azimuthStart
        else: azimuthVariation = abs(azimuthEnd-azimuthStart)

        azimuthEnd = azimuthEnd+5 if clockwiseRotation else azimuthEnd-5
        if(azimuthEnd == 360): azimuthEnd == 0

        azimuth = azimuthStart
        elevation = elevationStart
        spatialized = []
        while azimuth != azimuthEnd:
            spatialized.append(self.spatialize(wavSpydio, azimuth, elevation, channel=channel))
            azimuth = (azimuth+5 if clockwiseRotation else azimuth-5)%360

        leftChannel = []
        rightChannel = []
        srVariation = wavSpydio.spDuration//(azimuthVariation//5)
        for i in range(0, azimuthVariation//5):
            if(i==0):
                gate = self.gradientGate(srVariation-512, srVariation+512, 1, 0, spDuration=spatialized[i].spDuration)
                leftChannel = spatialized[i].song[:,0]*gate
                rightChannel = spatialized[i].song[:,1]*gate
            elif(i+1==azimuthVariation//5):
                gate = self.gradientGate((srVariation*i)-512, (srVariation*i)+512, 0, 1, spDuration=spatialized[i].spDuration)
                leftChannel = np.add(leftChannel, spatialized[i].song[:,0]*gate)
                rightChannel = np.add(rightChannel, spatialized[i].song[:,1]*gate)
            else:
                gate = self.gate((srVariation*i)-512, (srVariation*i)+512, (srVariation*(i+1))-512, (srVariation*(i+1))+512, spDuration=spatialized[i].spDuration)
                leftChannel = np.add(leftChannel, spatialized[i].song[:,0]*gate)
                rightChannel = np.add(rightChannel, spatialized[i].song[:,1]*gate)

        song = np.array([leftChannel, rightChannel]).transpose()
        return WavSpydio(path=None, song=song, song_sr=wavSpydio.song_sr)

    def gradientGate(self, start:int, end:int, startAmplitude:float, endAmplitude:float, spDuration:int=0):
        if(start > end):
            tmp = end
            end = start
            start = tmp
        if(start < 0): start = 0
        if(end > spDuration): spDuration = end

        if(start == 0 and spDuration-end == 0):
            attack = np.linspace(startAmplitude,endAmplitude,end-start)
        elif(start == 0):
            attack = np.concatenate([np.linspace(startAmplitude,endAmplitude,end-start), np.full((spDuration-end), endAmplitude)])
        elif(spDuration-end == 0):
            attack = np.concatenate([np.full((start), startAmplitude), np.linspace(startAmplitude,endAmplitude,end-start)])
        else:
            attack = np.concatenate([np.full((start), startAmplitude), np.linspace(startAmplitude,endAmplitude,end-start), np.full((spDuration-end), endAmplitude)])
        return attack

    def gate(self, startIncrease:int, endIncrease:int, startDecrease:int, endDecrease:int, startAmplitude:float=0, sustainAmplitude:float=1, endAmplitude:float=0, spDuration:int=0):
        attack = self.gradientGate(0, endIncrease-startIncrease, startAmplitude, endAmplitude=sustainAmplitude)
        sustain = np.full((startDecrease-endIncrease), sustainAmplitude)
        decrease = self.gradientGate(0, endDecrease-startDecrease, sustainAmplitude, endAmplitude)

        if(startIncrease != 0 and endIncrease !=spDuration):
            start = np.full((startIncrease), startAmplitude)
            end = np.full((spDuration-endDecrease), endAmplitude)
            gate = np.concatenate([start, attack, sustain, decrease, end])
        elif(startIncrease != 0):
            start = np.full((startIncrease), startAmplitude)
            gate = np.concatenate([start, attack, sustain, decrease])
        elif(endIncrease !=spDuration):
            end = np.full((spDuration-endDecrease), endAmplitude)
            gate = [attack, sustain, decrease, end]
        return gate

    def loadWavFile(self, path:str):
        wav = WavSpydio(path)
        return wav

    def saveWavFile(self, wavSpydio:WavSpydio, path:str):
        if path.endswith(".wav") == False: path = path+".wav"

        if wavSpydio.dim == 1: leftChannel, rightChannel = wavSpydio.song, wavSpydio.song
        else: leftChannel, rightChannel = wavSpydio.song[:,0], wavSpydio.song[:,1]

        leftChannel = leftChannel - np.mean(leftChannel)
        rightChannel = rightChannel - np.mean(rightChannel)
        leftChannel = leftChannel/np.amax(leftChannel) 
        rightChannel = rightChannel/np.amax(rightChannel)

        spiow.write(path, wavSpydio.song_sr, np.vstack([leftChannel, rightChannel]).transpose())