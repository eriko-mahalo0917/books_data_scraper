# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$%$$$$$$$$$$$$$$$$$$$
#標準モジュールのloggingを呼び出す
import logging
#現時点の日付をしるために呼び出す
from datetime import datetime

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$%$$$$$$$$$$$$$$$$$$$
#**********************************************************************************
#Formatterは標準モジュールの中にあるものをクラスとして呼び出して継承している

class LoggerBasicColor(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",  # グレー
        "INFO": "\033[94m",   # 青色
        "WARNING": "\033[93m", # 黄色
        "ERROR": "\033[91m",   # 赤色
        "CRITICAL": "\033[95m", # マゼンダ
    }
    
    # 基本の色
    RESET = "\033[0m"
    
    # ----------------------------------------------------------------------------------
    # loggingのformatをカスタムしてログレベルに応じた色付けを行う
    def format(self,record):
        message = super().format(record) #親クラス　logging.Formatterのformatを呼び出す
        color = self.COLORS.get(record.levelname,"") #色を取得
        return f"{color}{message}{self.RESET}" #メッセージの色のみ変更して、元に戻す

# ----------------------------------------------------------------------------------
# **********************************************************************************
#記録係を自動で準備してくれるクラスを作る
class SimpleLogger:
    #:boolは型ヒントでTrueかFalseのどちらかを入れてくださいというヒント　間違い防止
    def __init__(self,debugMode: bool = True): 
        #自分で決めた変数名にお決まりの定型文を入れているイメージ
        #特別なロガーをもらい、ここに変数名を入れている
        self.logger = logging.getLogger(__name__)
        #Trueなら、記録の細かさ（loggingLevel）を一番細かいDEBUGレベルにします。そうでなければ、普通のINFOレベルにします。
        self.loggingLevel = logging.DEBUG if debugMode else logging.INFO
        #さっきもらった記録ノートに記録してほしいと伝えている
        self.logger.setLevel(self.loggingLevel)
        
        
        #インスタンスを作成する 今の時刻を表示して、表示形式をしている
        self.currentDate = datetime.now().strftime('%y%m%d')
        self.setUptoLogger() #addHandlerにて追加したものを反映
        
        
    # ----------------------------------------------------------------------------------
    # カスタムされたloggerをセットする
    def setUptoLogger(self):
        if not self.logger.handlers:
            #ログをコンソール（ターミナル）に表示させる設定
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(self.loggingLevel)
            
            #ログのメッセージの基本フォーマット→時間→ログレベル→エラーメッセージ
            consoleHandler.setFormatter(LoggerBasicColor("%(asctime)s - %(levelname)s - %(message)s"))
            #記録ノートに今作ったを画面に出せるようにしている
            self.logger.addHandler(consoleHandler)
            
            #ログFileを出力を定義
            #拡張する際にはここのPathを変更する
            #記録を保存するためのFileの名前を決めている（250927Debug.log）
            log_file_path = f"{self.currentDate}Debug.log"
            
            #ログをFileに出力させる設定
            #encoding="utf-8"は、日本語が文字化しないようにしている
            fileHandler = logging.FileHandler(log_file_path,encoding="utf-8")
            #DEBUGレベルの情報まで、全ての記録を残すように設定
            fileHandler.setLevel(logging.DEBUG)
            #ファイルに書き込みするときの見た目を設定
            fileHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            #記録が画面とファイルの両方に残るようになる
            self.logger.addHandler(fileHandler)
            #ログの出力を重複させない設定
            self.logger.propagate = False
            
    #------------------------------------------------------------------------------------
    #カスタムされたLoggerを取得する
    
    def get_logger(self):
        return self.logger
    
    #------------------------------------------------------------------------------------
    
    # 呼び出す際
    # from method.base.utils.logger import SimpleLogger
    # でimportして

    # 対象のクラスのinit内で
    # self.logger_setup = SimpleLogger()
    # self.logger = self.logger_setup.get_logger()
    # を定義

    # 実際のコードでは
    # self.logger.info("ログメッセージ")
    # self.logger.debug("デバッグメッセージ")
    # self.logger.warning("警告メッセージ")
    # self.logger.error("エラーメッセージ")
    # self.logger.critical("重大なエラーメッセージ")
    
    
#****************************************************************************************
#「もしこのファイルが主役として直接実行されたら、この下のコードを動かしてね」という特別な合図
if __name__ == "__main__":
    #テストコード
    test_logger = SimpleLogger(debugMode=True)
    logger = test_logger.get_logger()
    logger.debug("これはデバッグメッセージです")
    logger.info("これは情報メッセージです")
    logger.warning("これは警告メッセージです")
    logger.error("これはエラーメッセージです")
    logger.critical("これは重大なエラーメッセージです")