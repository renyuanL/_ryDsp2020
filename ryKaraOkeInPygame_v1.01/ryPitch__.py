from __future__ import division

'''
ryPitch__.py

此處主要處理 pitch , f0, midi_number, 音符名稱

DSP 部分尚有 bug，先擋下而已，尚未推導數學，嚴格 debug

ryF0Estimate000.py

'''

'''
__main__:184: DeprecationWarning: The binary mode of fromstring is deprecated, as it behaves surprisingly on unicode inputs. Use frombuffer instead
__main__:185: DeprecationWarning: The binary mode of fromstring is deprecated, as it behaves surprisingly on unicode inputs. Use frombuffer instead
D:\OneDrive\___PyConJP2019\ryKaraOke-master\ryPitch__.py:191: MatplotlibDeprecationWarning: The find function was deprecated in version 2.2.
  start = find(d > 0)[0]
start = find(d > 0)[0] 此行有 bug, 先擋一下吧。
'''




from numpy.fft import rfft
from numpy import argmax, mean, diff, log, log2

#from matplotlib.mlab import find

import numpy as np
def find(condition):
    res, = np.nonzero(np.ravel(condition))
    return res


try:
    from scipy.signal import blackmanharris, fftconvolve
except:
    from ryFFTConv import blackmanharris, fftconvolve

#from time import time
import sys

'''
try:
    import soundfile as sf
except ImportError:
    from scikits.audiolab import flacread
'''

#from parabolic import parabolic
#---------------------------------

from numpy import polyfit, arange

def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.
   
    f is a vector and x is an index for that vector.
   
    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.
   
    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.
   
    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
   
    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
   
    """
    #
    #
    #>>> f = [2, 3, 1, 6, 4, 2, 3, 7]
    #>>> parabolic(f, argmax(f))
    #Traceback (most recent call last):
    #  File "<pyshell#16>", line 1, in <module>
    #    parabolic(f, argmax(f))
    #  File "C:\Dropbox\ryASR\ryASR2016\ryF0Estimate000.py", line 46, in parabolic
    #    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    #IndexError: list index out of range
    #
    '''
    當最大值發生在最末端時，會產生如上Bug
    '''
    
    '''
    當最大值發生在最前端時，可能也不正常！！
    '''
    
    # 先擋一下吧：
    if x in [0, len(f)-1]: 
        xv, yv= x, f[x]
        return (xv, yv)
    
    
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def parabolic_polyfit(f, x, n):
    """Use the built-in polyfit() function to find the peak of a parabola
    
    f is a vector and x is an index for that vector.
    
    n is the number of samples of the curve used to fit the parabola.
    """    
    a, b, c = polyfit(arange(x-n//2, x+n//2+1), f[x-n//2:x+n//2+1], 2)
    xv = -0.5 * b/a
    yv = a * xv**2 + b * xv + c
    return (xv, yv)

'''
if __name__=="__main__":
    from numpy import argmax
    import matplotlib.pyplot as plt
    
    y = [2, 1, 4, 8, 11, 10, 7, 3, 1, 1]
    
    xm, ym = argmax(y), y[argmax(y)]
    xp, yp = parabolic(y, argmax(y))
    
    plot = plt.plot(y)
    plt.hold(True)
    plt.plot(xm, ym, 'o', color='silver')
    plt.plot(xp, yp, 'o', color='blue')
    plt.title('silver = max, blue = estimated max')
'''    


#---------------------------------

def freq_from_crossings(sig, fs):
    """
    Estimate frequency by counting zero crossings
    """
    # Find all indices right before a rising-edge zero crossing
    indices = find((sig[1:] >= 0) & (sig[:-1] < 0))

    # Naive (Measures 1000.185 Hz for 1000 Hz, for instance)
    # crossings = indices

    # More accurate, using linear interpolation to find intersample
    # zero-crossings (Measures 1000.000129 Hz for 1000 Hz, for instance)
    crossings = [i - sig[i] / (sig[i+1] - sig[i]) for i in indices]

    # Some other interpolation based on neighboring points might be better.
    # Spline, cubic, whatever

    return fs / mean(diff(crossings))


def freq_from_fft(sig, fs):
    """
    Estimate frequency from peak of FFT
    """
    # Compute Fourier transform of windowed signal
    windowed = sig * blackmanharris(len(sig))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f))  # Just use this for less-accurate, naive version
    true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / len(windowed)


def freq_from_autocorr(sig, fs):
    """
    Estimate frequency using autocorrelation
    """
    # Calculate autocorrelation (same thing as convolution, but with
    # one input reversed in time), and throw away the negative lags
    corr = fftconvolve(sig, sig[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first low point
    d = diff(corr)
    #
    #
    #start = find(d > 0)[0]
    #
    # 萬一 find(d > 0) == np.array([]) ！ 上面這行就有 bug 了
    #
    # 例如：
    #
    '''
    >>> sig= np.array([1,1,1,1,1,1,1,1,1])
    >>> corr = fftconvolve(sig, sig[::-1], mode='full')
    >>> corr = corr[len(corr)//2:]
    >>> d = diff(corr)
    >>> d>0
    array([False, False, False, False, False, False, False, False], dtype=bool)
    >>> find(d>0)
    array([], dtype=int64)
    >>> find(d>0)[0]
    Traceback (most recent call last):
      File "<pyshell#19>", line 1, in <module>
        find(d>0)[0]
    IndexError: index 0 is out of bounds for axis 0 with size 0
    >>> 
    '''
    try: 
        start = find(d > 0)[0]
    except:
        print('start = find(d > 0)[0] 此行有 bug, 先擋一下吧。')
        #start= 0
        fs_px= 0
        return fs_px
    

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    # Should use a weighting function to de-emphasize the peaks at longer lags.
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)

    return fs / px

'''
>>> Exception in thread Thread-4:
Traceback (most recent call last):
  File "C:\Python34\lib\threading.py", line 911, in _bootstrap_inner
    self.run()
  File "C:\Python34\lib\threading.py", line 859, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Dropbox\ryASR\ryASR2016\ry重寫錄放音.py", line 348, in 鼠鍵線程
    f0= freq_from_autocorr(x, 取樣率)
  File "C:\Dropbox\ryASR\ryASR2016\ryF0Estimate000.py", line 137, in freq_from_autocorr
    px, py = parabolic(corr, peak)
  File "C:\Dropbox\ryASR\ryASR2016\ryF0Estimate000.py", line 46, in parabolic
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
IndexError: index 1024 is out of bounds for axis 0 with size 1024
'''

def freq_from_HPS(sig, fs):
    """
    Estimate frequency using harmonic product spectrum (HPS)
    """
    windowed = sig * blackmanharris(len(sig))

    from pylab import subplot, plot, log, copy, show

    # harmonic product spectrum:
    c = abs(rfft(windowed))
    maxharms = 8
    subplot(maxharms, 1, 1)
    plot(log(c))
    for x in range(2, maxharms):
        a = copy(c[::x])  # Should average or maximum instead of decimating
        # max(c[::x],c[1::x],c[2::x],...)
        c = c[:len(a)]
        i = argmax(abs(c))
        true_i = parabolic(abs(c), i)[0]
        print ('Pass %d: %f Hz' % (x, fs * true_i / len(windowed)))
        c *= a
        subplot(maxharms, 1, x)
        plot(log(c))
    show()


noteNameL= [
     'A_', 'A#', 'B_', 'C_', 'C#', 'D_','D#','E_','F_','F#','G_','G#',
     'a_', 'a#', 'b_', 'c_', 'c#', 'd_','d#','e_','f_','f#','g_','g#'
     ]
noteEmpty= '..' # 休止符

noteMinFreq= 440 / 2**4  # 27.5
noteMaxFreq= 440*8 # 880 is special for me #440 * 2**3  # 3520 for whistle
    
#import numpy as np

def pitchQuantization2midiNum(f= 0):
    
    if f < noteMinFreq or f > noteMaxFreq:
        midiNum= 0   
    else:  
        n= int(round(12 * log2(f/440))) # 量化在這行的 int(round()) 發生

        midiNum= n+69 # A4= A_440 == midi_69    
    return midiNum
    
def pitchQuantization(f= 0, noteName= ''):
    
    if noteName != '':
        F= pitchQuantizationByNoteName(noteName)
        
    elif f < noteMinFreq or f > noteMaxFreq:
        F= 0
        noteName= ''
    
    else:  
        n= int(round(12 * log2(f/440))) # 量化在這行的 int(round()) 發生
        F= 440 * (2**(n/12))       
        
        #n += 12
        noteName= noteNameL[n%len(noteNameL)]
        midiNum= n+69 # A4= A_440 == midi_69
    
    return F, noteName

def pitchQuantizationByNoteName(noteName):
    
    if noteName in noteNameL:
        n= noteNameL.index(noteName)
        #n= n-12
        F= 440 * (2**(n/12))
    else:
        F= 0
    
    return F
    