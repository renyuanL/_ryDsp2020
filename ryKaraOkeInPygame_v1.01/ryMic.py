'''
ryMic.py

ryMic003_deque.py
ryMic002_waveFile.py

ryMic.py
ry重寫錄放音.py

Renyuan Lyu
2016/08/03, 08/06, 08/15, 08/21

'''
import threading
import time
import pyaudio
import numpy as np
import wave
import struct

from collections import deque

#
# 語音的時間單位要精細劃分，
# 點 < 框 < 秒 < 段
#
# 點 即是 樣本點，為最小的時間單位
#
# 點、秒 可透過 取樣率 來設定
# 每秒點數 即為 取樣率， 
# 習慣上可設為 44100, 16000
#
# 在此：
# 1 框 = 1024 點 (取 2**10 ，適合後面的 FFT 運算)
#

class Ry麥類:

    def __init__(我, 取樣率= 16000,  每框點數= 1024, 框數= 32):#16):
    
        我.音訊=  pyaudio.PyAudio()

        我.取樣率= 我.每秒點數=  取樣率 #16000 # 10240 #10000
        我.每框點數=            每框點數 #1024  # 1000
        我.每點byte數= 每點byte數=           2

        我.音流=  我.音訊.open(
                    rate=     我.取樣率, 
                    channels= 1, # 麥克風鎖定 1 聲道，若是 wav file，則可處理多聲道。
                    format=   我.音訊.get_format_from_width(
                                        每點byte數, 
                                        unsigned= 'False'), #8,
                    
                    frames_per_buffer= 我.每框點數, #1000,
                    
                    input= True, 
                    output=True
                    )
        
        #主要　語音資料在此！！　將維持　.框數　個框
        我.框們=  deque() #[] # 據說用 deque 比用 list 快很多 leftpop() vs pop(0) ，練習看看。
        我.i框=   0        
        
        '''         
        我.秒數= 秒數 #1
        我.點數= 我.秒數 * 我.每秒點數
        我.框數= 我.點數 // 我.每框點數 
        '''
        我.框數= 框數
        我.點數= 我.框數 * 我.每框點數
        我.秒數= 我.點數 / 我.每秒點數 # 秒數非整數，在此預設值計算為 1.024
        
        # 由於這裡會無條件捨去小數點，
        # 故實際秒數會變小一點。 
        

        # 計算初始環境雜訊之資訊，可模仿之來撰寫其他演算法
        我.初框= {'mean':0, 'std':1, 'fmean':0, 'fstd':1}
        
        #
        # 用多線程
        #
        我.錄音線=  threading.Thread(target= 我.錄音線程 )
        我.放音線=  threading.Thread(target= 我.放音線程 )       
        我.初框線=  threading.Thread(target= 我.初框線程)
        我.wav初框線=  threading.Thread(target= 我.初框線程,kwargs={'source':'wav'})
        
        #
        # 加入 wav 擋 當作 麥 來用，可同時使用。
        #
        
        我.wav錄放音線=  threading.Thread(target= 我.wav錄放音線程)
        
        我.wav取樣率= 我.wav每秒點數=  我.取樣率 #16000 # 10240 #10000
        我.wav每框點數=                我.每框點數 #1024  # 1000
        我.wav每點byte數=              我.每點byte數=           2
        
        我.wav框們=  deque() #[]
        我.wav_i框=   0        
        
        '''         
        我.秒數= 秒數 #1
        我.點數= 我.秒數 * 我.每秒點數
        我.框數= 我.點數 // 我.每框點數 
        '''
        我.wav框數= 我.框數
        我.wav點數= 我.框數 * 我.每框點數
        我.wav秒數= 我.點數 / 我.每秒點數 # 秒數非整數，在此預設值計算為 1.024

    def 錄音線程(我):
    
        #global 框們, 錄音線程活著
        #
        # 最初 決定 框數= 10，每框點數= 1000， 每框點數應小於 y.get_read_available()
        #
        #
        #框數     = 10
        #每框點數 = 1000
        #
        print('錄音線程()....')
        
        我.i框= 0
        我.框們=  deque() #[]
        for i in range(我.框數):
            z= 我.音流.read(我.每框點數) #, exception_on_overflow= False )
            
            #我.音流.write(z) ## 即時放音
            
            我.框們 += [z]
            我.i框  += 1
            

        #
        # 往後一直維持 相同框數(=10)，讀進 最新 @10 (末端)，丟棄 最舊 @0 (前端)
        # 框們[0 .. -1]
        #
        
 
        我.錄音線程活著= True
        while 我.錄音線程活著: #True:
            
            z= 我.音流.read(我.每框點數)
            
            我.框們 += [z]  # 新框加在尾端
            我.i框  += 1
            #if len(我.框們) > 我.框數:
            我.框們.popleft()#pop(0)  # 舊框彈出
        
        # 如此，框們[:] ==框們[0,...,(N-1)] == 框們[-N,...,-1]

    def 等待第一圈錄音圓滿(我):
        while (len(我.框們) < 我.框數): time.sleep(.01)
        return True
        
    def 放音線程(我):
        #global 放音線程活著
        
        print('放音線程()....')
        
        我.等待第一圈錄音圓滿()
        #while (len(框們) != 框數): time.sleep(.01)
        
        我.放音線程活著= True
        while 我.放音線程活著: #True:
            z= 我.框們[0] # [0..-1] # 錄音進 框們[-1] 之後，放音與其相距 (框數-1) 個框
            我.音流.write(z)
           
        '''
        Good....
        錄音從最右邊進來
        到達最左邊才放音
        '''
        
    def 結束錄放音線程(我):

        #global 錄音線程活著, 放音線程活著

        我.錄音線程活著= False
        我.放音線程活著= False
        我.wav錄音線程活著= False
        
        time.sleep(.1) # 等一下，讓錄放音線程停車
        
        
        我.音流.close()
        我.音訊.terminate()


    def start(我, 錄= True, 放= False, 初= True, wav= True):

        if 錄:   我.錄音線.start()
        if 放:   我.放音線.start()
        if 初:   
            我.初框線.start()
            我.wav初框線.start()
            
        if wav:  我.wav錄放音線.start()

    def stop(我):
        我.結束錄放音線程()
    
       
    def 初框線程(我, source= 'mic'):
        #global 初框
                
        #我.等待第一圈錄音圓滿()

        #取 最初框、算振幅平均mean、振幅標準差std
        
        print('{}, source= {}\n'.format('初框線程()....', source))
        
        if source == 'mic':
            我.等待第一圈錄音圓滿()
            x= 我.框們 #.copy()
        else: #source == 'wav': # source= 'wav'
            我.等待第一圈錄音圓滿_wav()
            x= 我.wav框們 #.copy()
        
        x= b''.join(x) # 二進位數字串 b'...'
        x= np.fromstring(x, dtype= np.int16) # 須轉為 int

        #m=  x.mean()
        #s=  x.std()
        m= abs(x).mean()
        s= abs(x).std()
        
          
        #
        # 把頻譜當作 機率分布，算 平均頻率
        #
        N= 我.每框點數
        k= np.arange(N//2)
        
        平均頻率=0
        平均平方頻率=0
        for i in range(我.框數):
            X= np.fft.fft(x[(0+i*N):(N+i*N)])
            X= abs(X)
            X= X[0:N//2]
     
            平均頻率 += (k*X).sum()/X.sum() #* 取樣率/每框點數
            
            平均平方頻率 += (k*k*X).sum()/X.sum() #* (取樣率/每框點數)**2
        
        平均頻率 /= 我.框數
        平均平方頻率 /= 我.框數
        
        頻率var= 平均平方頻率-平均頻率**2
        頻率std= 頻率var**.5
        
        平均頻率 *= 我.取樣率/我.每框點數
        頻率std *= 我.取樣率/我.每框點數
        
        if source=='mic':
            我.初框=    {'mean':m, 'std':s, 'fmean':平均頻率, 'fstd':頻率std}
        else:  #source=='wav':
            我.wav初框= {'mean':m, 'std':s, 'fmean':平均頻率, 'fstd':頻率std}

        
        #我.重新計算初框活著= False
        #print('初框= ',我.初框)
        
        
        #重新計算初框活著= False

    def 等待第一圈錄音圓滿_wav(我):
        while (len(我.wav框們) < 我.wav框數): time.sleep(.01)
        return True
        
    def wav錄放音線程(我, 音檔名= 'rySongs/ryKira16K01C.wav'):
            
        print('wav錄放音線程().... 音檔名= ', 音檔名)
        

        音檔名們= [ 'rySongs/ry_GangHui16K03C_JC18_2001_江蕙_家後_官方MV.wav',
                    'rySongs/ryNadasosoRimi16K03C.wav',
                    'rySongs/ryTokiDo16K03C.wav',
                    'rySongs/ry_16K03C_木蘭の涙.wav'
                    ]
        
        音檔名們= [ 'rySongs/ryNadasosoRimi16K03C.wav',
                    'rySongs/ryTokiDo16K03C.wav',
                    'rySongs/ry_16K03C_木蘭の涙.wav',
                    'rySongs/ry_GangHui16K03C_JC18_2001_江蕙_家後_官方MV.wav'] 
        # 目前只有這2檔案 有 歌詞時間點
        
       
        
        
        np.random.shuffle(音檔名們) # 不要每次都是一樣的順序
        
        p= 我.音訊
        
        我.wav錄音線程活著= True
        i音檔名們= 0
        
        我.wav_i框= 0 #我.i框 #0 # 用 來同步，起初同步，運作過程未知。待研究！！
        我.wav框們=  deque() #[]
        while 我.wav錄音線程活著:
        
            我.音檔名= 音檔名= 音檔名們[i音檔名們%len(音檔名們)]
            
            #我.wav_i框= 0 #我.i框 #0 # 用 來同步，起初同步，運作過程未知。待研究！！
            #我.wav框們=  [] # 不能再 reset 了，會讓別處 無框可處理！！
            
            with wave.open(音檔名,'rb') as f:
                   
                fm= p.get_format_from_width(f.getsampwidth())
                ch= f.getnchannels()
                我.wav取樣率= rt= f.getframerate()
                
                print('音檔名={}, fm= {}, ch= {}, rt= {}'.format(音檔名, fm, ch, rt))

                我.w音流= stream= p.open(
                                format=   fm,
                                channels= max(ch-1,1),  #1,  #ch, 永遠只放音單聲道
                                rate=     rt,
                                output= True)
                                           
                我.wav_i框= 0 #我.i框 #0 # 用 來同步，起初同步，運作過程未知。待研究！！
                
                我.wav錄音線程活著= True
                while 我.wav錄音線程活著: #True:
                    
                    z= f.readframes(我.每框點數)
                    
                    if z==b'' or len(z)<我.每框點數*我.每點byte數*ch: break #f.rewind() # 重複
                    
                    
                    if ch==1:
                        z0= z1= z
                        
                    elif ch==2:
                        #
                        # 1 sterio ==> 2 mono , for short int
                        #
                        nFrames= 我.每框點數 #4
                        x= z #f.readframes(nFrames)
                        
                        xx= struct.unpack('<'+'hh'*nFrames,x)
                        
                        x0= xx[0::2]
                        x1= xx[1::2]
                        
                        z0= struct.pack('<'+'h'*nFrames, *x0)
                        z1= struct.pack('<'+'h'*nFrames, *x1)
                    
                    elif ch==3:
                        #
                        # 1 sterio ==> listening 
                        # 1 mono ==> analysis and processing, teacher's voice
                        #
                        nFrames= 我.每框點數 #4
                        x= z #f.readframes(nFrames)
                        
                        xx= struct.unpack('<'+'lh'*nFrames,x) # 'l'== 4 bytes, 'h'== 2 bytes
                        
                        x0= xx[0::2] # 左右放音, 4 bytes = 2 bytes + 2 bytes
                        x1= xx[1::2] # 分析,     2 bytes
                        
                        z0= struct.pack('<'+'l'*nFrames, *x0)
                        z1= struct.pack('<'+'h'*nFrames,  *x1)
                   
                    else: 
                        z0= z1= b''
                        print('ch= {}, not processed'.format(ch))
                        break

                    
                    我.w音流.write(z0)
                    
                    我.wav框們 += [z1]  # 新框加在尾端
                    
                    我.wav_i框  += 1
                    #我.wav_i框= 我.i框 #0 # 用 來同步
                    我.i框=  我.wav_i框
                    
                    
                    while len(我.wav框們) > 我.wav框數:
                        我.wav框們.popleft()#pop(0)  # 舊框彈出
                
                我.w音流.stop_stream()
                我.w音流.close()
            i音檔名們 += 1
                        

if __name__=='__main__':        
    x= Ry麥類()
    x.start()
    print('ryEnjoy.....! 記得　x.stop()')
     
