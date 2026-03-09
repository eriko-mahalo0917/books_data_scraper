###ここでコードを作成してdata.pyにCSVデータを保存する################
import sys
import os
import datetime
import csv

#__file__は今開いているファイル
#os.path.abspath(...)はbooks_scraper.pyの正確な住所を教えて
#2階層上にutilsがあるからos.path.dirnameを2回
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


#--------------
# 自作モジュール
#--------------
#logger
from utils.logger import SimpleLogger
from utils.path_helper import get_data_dir_path


class DataSaver:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()

    #----------------------------------------------
    #1つ目のフロー:データ受取＋保存準備
    #保存先のdataフォルダを決めて、CSV保存パス作成
    #⚠️exeファイルのパスが変わらないように注意
    #----------------------------------------------
    #file_name="books.csv" は「初期値（デフォルト値）」
    #ファイル名を指定しなかった場合、自動的に "books.csv"にする
    def create_csv_path(self, books_details_results, file_name = "books.csv"):
        self.logger.info("受け取ったデータをCSVに保存する処理を開始します")
        
        #もし渡されたデータが空っぽだったら、処理中断
        if not books_details_results:
            self.logger.warning("保存するデータが空っぽです!処理を中断します!")
            return None
        
        #ここでファイル名に今日の日付が付くようにする!そうすればいつ実行したデータか分かる
        #datetime.datetime.now()は今の時間を（年・月・日・時・分・秒）」を取得する命令
        #.strftime("%Y%m%d")は%Yは4桁の年、%mは2桁の月、%dは2桁の日を表す
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        
        #もとのファイル名の前に、日付とアンダーバーをくっつる
        #「20260308」+「_」+「books.csv」 ➔ 「20260308_books.csv」
        final_file_name = f"{today_str}_{file_name}"
        
        #既にある　dataフォルダを確認する
        #後の処理でも使い回せるよう、selfをつけて「自分の持ち物」にする
        data_dir = get_data_dir_path()
        
        #保存パスを作成
        books_file_path = data_dir / final_file_name
        self.logger.info(f"保存先フォルダを確認しました:{books_file_path}")
        
        return books_file_path
        
    #----------------------------------------------
    #２つ目のフロー:CSVファイルを開く
    #保存パスにCSVファイルを作成して開く
    #CSV書き込み用をする writer作成 → 書き込む道具を作る
    #----------------------------------------------    
    def open_csv_file(self, books_file_path):
        try:
            self.logger.info("CSVのファイルを開き、書き込み準備を開始します")
            #encoding="utf-8" → 日本語対応
            #newline="" → WindowsでCSVの空行バグを防ぐモード
            #CSVファイルを「書き込みモード」で開く"w"は書き込み
            csv_file = open(books_file_path, "w" ,encoding="utf-8-sig",newline="")
            #csvモジュールを使ってCSV書き込み用のwriterを作成
            #準備しただけで書き込みはまだ
            csv_writer = csv.writer(csv_file)
            
            self.logger.info("CSVのファイルを開き、書き込み準備が完了しました")
            #２つのreturnを返す
            return csv_file, csv_writer
        
        except Exception as e:
            self.logger.error( f"CSVファイルを開けませんでした:{e}")
            # open_csv_file() は (csv_file, csv_writer) の2つを返す関数なのでNoneが２つ
            return None, None
            
    #----------------------------------------------
    #３つ目のフロー
    #CSVの１行目に見出し(ヘッダー)を書き込む
    #----------------------------------------------
    def write_csv_header(self, csv_writer, books_details_results):
        try:
            self.logger.info("CSVヘッダーの書き込みを開始します")
            #1件目のデータ辞書からキーを取り出す
            #{"title": "本A", "price": "100円"} ➔ ["title", "price"]
            #[0] は1件目のデータでキーだけを取り出している
            books_csv_header = list(books_details_results[0].keys())
            
            #csv_writerを使って1行目を書き込む
            #writerow（ライト・ロウ）は「1行書く」という命令!
            #取り出した1件目のデータの辞書のキーを1行目に書く命令
            csv_writer.writerow(books_csv_header)
            
            self.logger.info(f"CSVヘッダーの書き込みが成功しました:{books_csv_header}")
            return books_csv_header
        
        except Exception as e:
            self.logger.error(f"ヘッダーの書き込みに失敗しました: {e}")
            return None
            
    
    #----------------------------------------------
    #４つ目のフロー:データの書き込み ＆ 保存完了
    #データを１行ずつ書き写す(ループ)
    #----------------------------------------------
    def write_csv_rows(self, csv_writer, csv_file, books_details_results):
        try:
            self.logger.info(f"合計{len(books_details_results)}件のデータ書き込みを開始します")
            #取得した辞書のリストのデータを順番に書き込みをする
            for  book_data in books_details_results:
                #辞書のvalueだけをリストに1行ずつしていく
                #.writerowは1行ずつ書くので、改行しなくても大丈夫! →CSVのメソッド
                #data.values() : 辞書から中身（商品）だけを取り出す→listで取り出したものをリスト化
                csv_writer.writerow(list(book_data.values()))
                
            #CSVを作成し終わったら、ファイルを閉じる
            csv_file.close()
            
            self.logger.info("CSVデータの書き込みと保存が完了しました!")
            #成功したことを宣言するためのTrue返し
            return True
            
        except Exception as e:
            self.logger.error(f"データの書き込み中にエラーが発生しました:{e}")
            #念の為、エラーの時もファイルを閉じるようにしておく
            csv_file.close()
            #失敗したことを宣言するための返し
            return False
"""        
#％％％％％％％％％％％％％％％％％％％％％％％％
#テスト用
#％％％％％％％％％％％％％％％％％％％％％％％％
if __name__ == "__main__":
    dummy_results = [
        {"title": "Python超入門", "price": "2,000円", "status": "在庫あり"},
        {"title": "はじめてのスクレイピング", "price": "2,500円", "status": "残りわずか"},
        {"title": "設計力が上がる本", "price": "3,000円", "status": "在庫あり"}
    ]
    #インスタンス作成
    saver = DataSaver()
    #①CSV保存パス作成
    csv_path = saver.create_csv_path(dummy_results)
    if not csv_path:
        print("CSVパス作成失敗")
        #終了
        exit()
        
    #②CSVファイルを開く
    csv_file, csv_writer = saver.open_csv_file(csv_path)
    if not csv_file:
        print("CSVファイルを開けませんでした")
        exit()
        
    #③ヘッダーの書き込み
    header = saver.write_csv_header(csv_writer, dummy_results)
    if not header:
        print("ヘッダー書き込み失敗")
        exit()
        
    #④データの書き込み
    result = saver.write_csv_rows(csv_writer, csv_file, dummy_results)
    if result:
        print("CSV保存テスト成功！")
    else:
        print("CSV保存テスト失敗")
"""