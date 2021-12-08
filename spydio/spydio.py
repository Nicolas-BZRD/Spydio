import os
import numpy as np
import scipy.io.wavfile as spiow
from SOFASonix import SOFAFile
from scipy import signal

class WavSpydio:
    def __init__(self, path:str, **kwargs):
        if path != None:
            self.song_sr, self.song = spiow.read(path)
            self.song = np.asarray(self.song)
            self.duration = len(self.song)/self.song_sr
            self.dim = self.song[0].size
        else:
            self.song_sr = kwargs["song_sr"]
            self.song = kwargs["song"]
            self.duration = len(self.song)/self.song_sr
            self.dim = self.song[0].size

class Spydio:
    def __init__(self, HRIR:int=0, verbose:bool=False):
        self.sofaFile = SOFAFile.load(os.path.abspath(os.getcwd())+"/spydio/hrir/{}.sofa".format(HRIR), verbose=False)
        self.HRIR = self.sofaFile.data_ir
        if verbose: 
            print(self.sofaFile.getParam('GLOBAL:ListenerDescription'))
            print(self.sofaFile.getParam("GLOBAL:Comment"))

    def spatialize(self, wavSpydio:WavSpydio, azimuth:int, elevation:int=4, channel:int=0):
        if elevation > 8 or elevation < 0: elevation = 4
        if azimuth < 0 or azimuth > 360: azimuth = abs(azimuth//360)

        if azimuth == 0 or azimuth == 360: azimuth = 0
        else: azimuth = round((360-azimuth)/5)

        if wavSpydio.dim == 1:
            processedL = np.array(signal.fftconvolve(wavSpydio.song[:], self.HRIR[(72*elevation)+azimuth][0][:]))
            processedR = np.array(signal.fftconvolve(wavSpydio.song[:], self.HRIR[(72*elevation)+azimuth][1][:]))
        else:
            processedL = np.array(signal.fftconvolve(wavSpydio.song[:,0], self.HRIR[(72*elevation)+azimuth][0][:]))
            processedR = np.array(signal.fftconvolve(wavSpydio.song[:,1], self.HRIR[(72*elevation)+azimuth][1][:]))

        song = np.array([processedL, processedR]).transpose()
        return WavSpydio(path=None, song=song, song_sr=wavSpydio.song_sr)        

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