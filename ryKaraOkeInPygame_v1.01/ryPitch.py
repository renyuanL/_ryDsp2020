'''
ryPitch.py
'''

import time
import numpy as np
import threading

from ryMic   import *


#from   ryF0Estimate000 import freq_from_autocorr, pitchQuantization, noteNameL
# debug for DSP issue ..
from   ryPitch__ import * #freq_from_autocorr, pitchQuantization, noteNameL, pitchQuantization2midiNum

class Ry音高類:

    def __init__(我, 麥= None, 框數= 16, 
                     波形能量= True,
                     mic音符= True,
                     wav音符= True):

        if 麥 is None:
            我.麥= Ry麥類(框數= 框數) #64,  # 16 框 == 1.024 秒
            我.麥.start()
        else:
            我.麥= 麥

        '''
        我.辨=       sr.Recognizer()

        我.辨認框數= 我.麥.框數   # 預設 64 框，為 4.096 秒
        我.位移框數= 我.辨認框數 // 2  # 一半時間丟去辨認1次，亦即重疊1半時間。

        我.音= None
        我.文= ''
        我.文們= []
        我.最大保留文長度= 1000 # 此值對應於實際時間是多少呢？
        
        
        我.辨認線0= threading.Thread(target= 我.辨認線程, kwargs= {'lang': 'zh-TW'})
        if 台:   我.辨認線0.start()
        
        我.辨認線1= threading.Thread(target= 我.辨認線程, kwargs= {'lang': 'ja'})
        if 日:   我.辨認線1.start()
        
        我.辨認線2= threading.Thread(target= 我.辨認線程, kwargs= {'lang': 'en'})
        if 英:   我.辨認線2.start()
        '''
        
        我.基頻= 0
        我.音符= ''
        我.基頻音符們= [] # [(0,0,0,'')] #(i框, f0, qf0, noteName)
        
        我.最大保留基頻音符長度= 10000 # 此值對應於實際時間是多少呢？
        
        我.音符線= threading.Thread(target= 我.音符線程)
        if mic音符:   我.音符線.start()
        
        我.波形能量線= threading.Thread(target= 我.波形能量線程)
        if 波形能量:    我.波形能量線.start()
        
        
        我.能量們= []
        我.最大保留能量長度= 我.最大保留基頻音符長度
        
        我.波形們= []
        我.最大保留波形長度= 64 # *1.024/16 秒
        
        我.wav基頻= 0
        我.wav音符= ''
        我.wav基頻音符們= [] # [(0,0,0,'')] #(i框, f0, qf0, noteName)
        
        我.wav音符線= threading.Thread(target= 我.wav音符線程)
        if wav音符:   我.wav音符線.start()
        
        
    """
    def 辨認線程(我, lang= 'zh-TW'):
        #global 文們, 文
        
        我.麥.等待第一圈錄音圓滿()
         
        while True: 

            i框= 我.麥.i框
            
            #y= b''.join(我.麥.框們[-我.辨認框數:])
            
            y= b''
            for k in range(-我.辨認框數,0):
                y += 我.音.框們[k]
            
            
            
            我.音= sr.AudioData(y, 我.麥.取樣率, 我.麥.每點byte數) #16000, 2) #self.樣本寬)   

            try:
                文=  我.辨.recognize_google(我.音, language= lang) #'zh-TW')
            
            except sr.UnknownValueError as e:
            
                #文= '{}= {}'.format('sr.UnknownValueError', e)
                # 4個點表示沒辨認結果，看起來比較乾淨。
                文= '.'*4 
                
            except sr.RequestError as e:
                文= '{}= {}'.format('sr.RequestError',e)
                
            
            '''
            Raises a ``speech_recognition.UnknownValueError`` exception 
                if the speech is unintelligible. 
            Raises a ``speech_recognition.RequestError`` exception 
                if the speech recognition operation failed, 
                if the key isn't valid, 
                or if there is no internet connection.
            '''
            
            我.文= 文
            
            我.文們 += [(i框, i框-我.辨認框數, lang, 文)]
            #print('[{}], ({}), {}'.format(i框, lang, 文))
            
            while len(我.文們)> 我.最大保留文長度: # 10000
                我.文們.pop(0)
                
            

            while (我.麥.i框 - i框 < 我.位移框數): pass # 這裡等最多 x.框數 個 框 (16)
                    
            #rate(1000)
    """
    def 音符線程(我):
        #global 文們, 文
        
        f0分析框數= 2
        hammingWin= np.hamming(f0分析框數*我.麥.每框點數)
        
        我.麥.等待第一圈錄音圓滿()
        
        while True: 

            i框= 我.麥.i框
            
            #yL= 我.麥.框們[-f0分析框數:] #[-1]
            #y= b''.join(yL)
            
            #'''
            y= b''
            for k in range(-f0分析框數,0):
                y += 我.麥.框們[k]
            #'''
            #y= 我.麥.框們[-1]
            
            
            y= np.fromstring(y, dtype= np.int16)
            y= y*hammingWin
                    
            f0= freq_from_autocorr(y, 我.麥.取樣率)
            
            qf0, noteName= pitchQuantization(f0)
            qf0= int(qf0)
            
            我.基頻=   qf0
            我.音符= noteName
            
            我.基頻音符們 += [(i框, f0, qf0, noteName)]
            #print('[{}], f0= {:04.1f}, qf0= {:04d}, {}'.format(i框, f0, qf0, noteName))
            
            while len(我.基頻音符們)> 我.最大保留基頻音符長度: # 10000
                我.基頻音符們.pop(0)
                

            while (我.麥.i框 - i框 < 1): pass 
                    
            #rate(1000)
    
    def wav音符線程(我):
        #global 文們, 文
        
        f0分析框數= 2 # 2 * 1/16 about 1/8 sec
        hammingWin= np.hamming(f0分析框數*我.麥.wav每框點數)
        
        #我.麥.等待第一圈錄音圓滿()
        我.麥.等待第一圈錄音圓滿_wav()
        
        while True: 

            i框= 我.麥.wav_i框
            
            #yL= 我.麥.wav框們[-f0分析框數:] #[-1]
            #y= b''.join(yL)
            
            #''' 
            y= b''
            for k in range(-f0分析框數,0):
                y += 我.麥.wav框們[k]
            #'''
            #y= 我.麥.wav框們[-1]
            
            y= np.fromstring(y, dtype= np.int16)
            y= y*hammingWin
                    
            f0= freq_from_autocorr(y, 我.麥.wav取樣率)
            
            qf0, noteName= pitchQuantization(f0)
            qf0= int(qf0)
            
            我.wav基頻=   qf0
            我.wav音符= noteName
            
            我.wav基頻音符們 += [(i框, f0, qf0, noteName)]
            #print('[{}], f0= {:04.1f}, qf0= {:04d}, {}'.format(i框, f0, qf0, noteName))
            
            while len(我.wav基頻音符們)> 我.最大保留基頻音符長度: # 10000
                我.wav基頻音符們.pop(0)            

            while (我.麥.wav_i框 - i框 < 1): pass 
                    
            #rate(1000)

    def 波形能量線程(我):
        #global 文們, 文
        
        我.麥.等待第一圈錄音圓滿()
        
        while True: 

            i框= 我.麥.i框
            
            y= 我.麥.框們[-1]
            y= np.fromstring(y, dtype= np.int16)
            
            
            我.能量= abs(y).mean()
            我.波形= y
            
            我.能量們 += [(i框, 我.能量)]
            我.波形們 += [(i框, 我.波形)]
            
            while len(我.能量們)> 我.最大保留能量長度: # 10000
                我.能量們.pop(0)

            while len(我.波形們)> 我.最大保留波形長度: # 1000 這個最吃空間，小心處理。
                我.波形們.pop(0)            
            
            '''
            f0= freq_from_autocorr(y, 我.麥.取樣率)
            
            qf0, noteName= pitchQuantization(f0)
            qf0= int(qf0)
            
            我.基頻=   f0
            我.音符= noteName
            
            我.基頻音符們 += [(i框, f0, qf0, noteName)]
            #print('[{}], f0= {:04.1f}, qf0= {:04d}, {}'.format(i框, f0, qf0, noteName))
            
            while len(我.基頻音符們)> 我.最大保留基頻音符長度: # 10000
                我.基頻音符們.pop(0)            
            '''
            
            
            while (我.麥.i框 - i框 < 1): pass 
                    
            #rate(1000)
            
RyPitch= Ry音高類   # 只是 別名

#---------
# simple demo ....
#---------
def 聽寫(ry, 秒數= 10, dt= .1):

    ry.麥.等待第一圈錄音圓滿()
    ry.麥.等待第一圈錄音圓滿_wav()
    
    while ry.基頻音符們 == []: pass
    while ry.wav基頻音符們 == []: pass

    t=0
    T= 秒數
    while t<T:
        能量=        ry.能量們[-1]
        基頻音符=    ry.基頻音符們[-1]
        wav基頻音符= ry.wav基頻音符們[-1]

        
        print('''t= {:.1f}: 能量= {}, 基頻音符= {}, wav基頻音符= {}'''.format(
                 t, 能量, 基頻音符, wav基頻音符))
        time.sleep(dt) # 1000 * .1 == 100
        t += dt


if __name__=='__main__':


    x= Ry音高類()
    聽寫(x, 秒數= 100, dt= .1)
