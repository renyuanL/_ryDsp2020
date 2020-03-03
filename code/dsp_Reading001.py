# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 17:22:19 2020

@author: renyu
"""

from __future__ import print_function, division

import thinkdsp
import thinkplot

import numpy as np

from ipywidgets import interact, interactive, fixed
import ipywidgets as widgets
from IPython.display import display

#%%
cos_sig= thinkdsp.CosSignal(freq=440, amp=1.0, offset=0)
sin_sig= thinkdsp.SinSignal(freq=880, amp=0.5, offset=0)

#%%
import matplotlib.pyplot as pl

cos_sig.plot();pl.grid('on')
sin_sig.plot();pl.grid('on')

#%%
mix= sin_sig + cos_sig
mix.plot();pl.grid('on')

#%%
wave= mix.make_wave(duration=0.5, start=0, framerate=11025)

data= wave.ys
pl.plot(data)

#%%
wave= thinkdsp.read_wave('92002__jcveliz__violin-origional.wav')

data= wave.ys
pl.plot(data)
pl.grid('on')

sd.play(data= data, samplerate= wave.framerate)
#%%