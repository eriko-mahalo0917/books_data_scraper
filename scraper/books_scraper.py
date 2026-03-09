#=================================================
import sys
import os
#__file__は今開いているファイル
#os.path.abspath(...)はbooks_scraper.pyの正確な住所を教えて
#2階層上にutilsがあるからos.path.dirnameを2回
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#--------------
#外部ライブラリ
#--------------
import requests
from bs4 import BeautifulSoup

#--------------
# 自作モジュール
#--------------
#logger
from utils.logger import SimpleLogger
#random_sleeper
from utils.random_sleeper import RandomSleeper
#=================================================
class BooksScraper:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
        self.random_sleeper = RandomSleeper()
        
    #----------------------------------------------
    #1つ目のフロー
    #URLへアクセスし、HTMLのTextを取得する
    #----------------------------------------------
    def get_html(self,target_url):
        self.logger.info(f"アクセスを開始します:{target_url}")
        self.random_sleeper.sleep_time()
        
        try:
            #URLを開いてというリクエスト
            html_response = requests.get(target_url)
            #.raise_for_status()はrequestsのライブラリ→200番代(成功),400番台(自分のミス),500番台(サーバーが悪い)
            html_response.raise_for_status()
            #文字化け対策：「たぶんこれ」な設定(encoding)に、「絶対これ！」な自動判定(apparent)を上書きする
            html_response.encoding = html_response.apparent_encoding
            
            self.logger.info("HTMLの取得に成功しました!")
            #取得した中身を(HTMLの文字データ)を返却 →Textがでないと失敗判定
            return html_response.text
        
        except Exception as e:
            #エラーだった場合は処理ストップ
            self.logger.error(f"エラーが発生しました:{e}")
            return None
    
    #----------------------------------------------
    #2つ目のフロー
    #HTMLから本の商品情報(タイトルと価格と評価と在庫状況とURL)を取得
    #----------------------------------------------
    def get_books_details(self,html_text):
        self.logger.info("HTMLから商品情報の抽出を開始します")
        
        #BeautifulSoupを使って読込して解析をする html.parserは標準でHTML文字列を読み込んでツリー構造に変換する
        books_soup = BeautifulSoup(html_text, "html.parser")
        #本全体の囲っている一番外側の枠を探してそこのデータを取得する(１冊分の情報が詰まっている)
        #<article class="product_pod">この部分!!全部のデータの中からそれを探してきて!お決まりの書き方
        books_data = books_soup.find_all("article", class_= "product_pod")
        
        self.logger.info(f"ページ内に{len(books_data)}件の本を見つけました")
        
        #取得したものをリストにまとめる
        books_details_results :list[dict] = []
        
        #１冊ずつデータの情報を取得していく
        for book in books_data:
            try:
                #①タイトル:h3の中の<a〜>の中にあるtitle="本の名前"を取得する
                book_title = book.h3.a["title"]
                
                #②価格:<p class="price_color">の中からテキスト部分の金額を取得する
                book_price = book.find("p", class_ = "price_color").text
                
                #③評価:<p class="star-rating Three">数字部分が評価によって変わる
                #半角スペースでクラスが2つに分かれるため、リストの2番目 [1] を取得する！
                books_rating = book.find("p", class_ = "star-rating")["class"][1]
                
                #④在庫状況:<p class="instock availability">→これ以下の在庫ありのテキストの前後に大量の空白があるため、.strip()で文字の前後を消す
                book_stock = book.find("p", class_ = "instock availability").text.strip()
                
                
                #⑤商品詳細URL:h3の中のhref="../../a-light-in-the-attic_1000/index.html"だけど、
                #このままでは使えないため、修正する
                relative = book.h3.a["href"]
                #replace(A, B)で余分なA"../をB""空っぽにしてね
                clean_url = relative.replace("../","")
                
                #本の詳細へ行くときのURLはhttp://books.toscrape.com/catalogue/the-black-maria_991/index.htmlで
                #catalogue/があるが（省略されていたら）足す
                if "catalogue/" not in clean_url:
                    clean_url = "catalogue/" + clean_url
                
                book_detail_url = f"http://books.toscrape.com/{clean_url}"
                
                #1冊分の①〜⑤を辞書にまとめる
                book_dict = {"title" : book_title, "price": book_price, "rating": books_rating, "stock": book_stock, "url": book_detail_url}
                
                #1冊分の辞書を最初に用意したリストに追加する
                books_details_results.append(book_dict)
                
            except Exception as e:
                #もしもHTMLが壊れていてエラーになった場合でも次の本へ進むようにする
                self.logger.error(f"1件のデータ抽出に失敗しました:{e}")
                continue
        
        #最終的な件数を報告する
        self.logger.info(f"合計{len(books_details_results)}件の抽出が完了しました")
        return books_details_results
        
        
        
    
    #----------------------------------------------
    #3つ目のフロー
    #次のページのURLを取得する
    #----------------------------------------------
    def get_next_page_url(self, html_text):
        self.logger.info("次のページのURLを取得します")
        
        #BeautifulSoupを使って読込して解析をする html.parserは標準でHTML文字列を読み込んでツリー構造に変換する
        book_soup = BeautifulSoup(html_text, "html.parser")
        
        #まずは親分の<li class="next">を探す
        next_li = book_soup.find("li", class_ = "next")
        
        #もし次へボタンがあったら ※最後のページでなければ!
        if next_li:
            #<a>タグのなからurlがある["href"]を引っこ抜く
            next_url = next_li.a["href"]
            self.logger.info(f"次のページを見つけました:{next_url}")
            return next_url
        
        #見つからなかったら ※最終ページもこれになる
        else:
            self.logger.info("次のページはありません(最終ページです)")
            return None

        
        
"""        
#％％％％％％％％％％％％％％％％％％％％％％％％
#テスト用
#％％％％％％％％％％％％％％％％％％％％％％％％
if __name__ == "__main__":
    #インスタンス作成
    test_scraper = BooksScraper()
    
    url = "http://books.toscrape.com/"
    
    print("実行を開始します")
    #=============1つ目のフロー=================
    result_html = test_scraper.get_html(url)
    
    if result_html:
        print("1つ目のフロー成功")
        
    #=============２つ目のフロー================
        books = test_scraper.get_books_details(result_html)
    
        if books:
            print(f"検出結果{len(books)}件:最初の1件のみ表示")
            #.items()はキーとvalueをセットで渡すぞの意味
            for key, value in books[0].items():
                print(f"{key}: {value}")
            
            print("2つ目フロー成功")
        
        #=============3つ目のフロー================
        print("3つ目のフロー次へのボタンのURL探しを始めます")
        next_url = test_scraper.get_next_page_url(result_html)
        
        if next_url:
            print(f"次のページのURL:{next_url}")
        else:
            print("次のページが見つからないか最終ページです")
    else:
        print("失敗です!ログを見てください")
"""