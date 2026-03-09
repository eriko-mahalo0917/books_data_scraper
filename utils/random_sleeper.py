#=================================================
#ランダムスリーパー用
import time
import random

#=================================================

#ランダムスリープを追加
class RandomSleeper:
    #人間っぽくランダムに待機時間を持たせる
    def __init__(self):
        pass
    
    def sleep_time(self, min_time: float = 1.0, max_time: float = 3.0):
        #ランダムモジュールの関数
        wait_time = random.uniform(min_time,max_time)
        #import timeのメソッドで一時停止させる
        time.sleep(wait_time) 