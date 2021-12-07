import numpy as np
from scipy import signal

def rotation(start, end, azStart, azEnd, song, song_sr, HRIR, elStart = 4, elEnd = 4):
    sound = song[start*song_sr:end*song_sr]
    azimuthVariation = azEnd - azStart
    processedL = []
    processedR = []

    
    i = azStart // 5

    for i in range(0,azimuthVariation // 5):
        processedL.append(signal.fftconvolve(sound[:], HRIR[elStart*72 + i][0][:]))
        processedR.append(signal.fftconvolve(sound[:], HRIR[elStart*72 + i][1][:]))

    srVariation = sound.shape[0]//(azimuthVariation//5)

    firstDecay = np.concatenate([np.ones(srVariation-512), np.linspace(1,0,1024)])
    firstDecay = np.pad(firstDecay, (0,len(processedL[0])-len(firstDecay)), mode='constant', constant_values=0)

    lastAttack = np.concatenate([np.linspace(0,1,1024), np.ones(srVariation-512)])
    lastAttack = np.pad(lastAttack, (len(processedL[0])-len(lastAttack),0), mode='constant', constant_values=0)

    for i in range(0,azimuthVariation // 5):
        if(i==0):
            processedL[i] = processedL[i]*firstDecay
            processedR[i] = processedR[i]*firstDecay

            returnL = processedL[i]
            returnR = processedR[i]
        elif(i+1==azimuthVariation // 5):
            processedL[i] = processedL[i]*lastAttack
            processedR[i] = processedR[i]*lastAttack

            returnL = np.add(returnL, processedL[i])
            returnR = np.add(returnR, processedR[i])
        else:
            ASR = np.concatenate([np.linspace(0,1,1024), np.ones(srVariation-1024), np.linspace(1,0,1024)])
            ASR = np.pad(ASR, ((i*srVariation)-512,0), mode='constant', constant_values=0)
            ASR = np.pad(ASR, (0,len(processedL[0])-len(ASR)), mode='constant', constant_values=0)
            processedL[i] = processedL[i]*ASR
            processedR[i] = processedR[i]*ASR

            returnL = np.add(returnL, processedL[i])
            returnR = np.add(returnR, processedR[i])
        
    return returnL, returnR