#==================================================
#--------------
# 自作モジュール
#--------------
from scraper.books_scraper import BooksScraper
from utils.save_data import DataSaver
from utils.logger import SimpleLogger
import config

#==================================================
class BooksScrapingMainFlow:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
    # ----------------------------------------------
    # 1つ目のフロー：HTMLを取得し、HTMLのTextを取得する
    # ----------------------------------------------
    def run_scraping_flow(self):
        self.logger.info("データ収集を開始します")
        books_scraper = BooksScraper()
        data_saver = DataSaver()
        
        #全ページ分のデータを溜める空リスト
        all_books: list[dict] = []
        
        #最初のページを取得する
        next_page_url = config.TARGET_URL #最初のページのURLをセット
        #next_page_urlがある間はループしてくれる
        #回数が分からないからwhileを使っている
        while next_page_url:
            page_html = books_scraper.get_html(next_page_url)
            #次のページがなければそこで終了
            if not page_html:
                break
        
            #----------------------------------------------
            #2つ目のフロー:HTMLから本の商品情報(タイトルと価格と評価と在庫状況とURL)を取得
            #----------------------------------------------
            books_data = books_scraper.get_books_details(page_html)
            #.extendはall_booksに個々の辞書が展開されて追加
            #全ページ分のデータを1つのリストにまとめたいから
            all_books.extend(books_data)
            
            #----------------------------------------------
            #３つ目のフロー:次のページのURLを取得
            #----------------------------------------------
            next_page_url = books_scraper.get_next_page_url(page_html)
            
        #----------------------------------------------
        #save_data
        #----------------------------------------------
        #１つ目のフロー：CSVパスの保存
        books_file_path = data_saver.create_csv_path(books_details_results=all_books, file_name="books.csv")
        
        #２つ目のフロー：CSVファイルを開く
        csv_file, csv_writer = data_saver.open_csv_file(books_file_path)
        
        #３つ目のフロー：CSVのヘッダーを書き込み
        data_saver.write_csv_header(csv_writer, config.CSV_HEADERS)
        
        #4つ目のフロー：CSVデータの書き込み
        data_saver.write_csv_rows(csv_writer, csv_file, books_details_results=all_books)
        
        self.logger.info("CSVの保存が完了しました!")