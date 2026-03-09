######exeファイルからjsonファイルとconfig.pyを呼び出すよ用#########

from pathlib import Path
import sys

##########################

def get_root_path():
    #getattr(オブジェクト,属性名,デフォルト値　→　あるか分からない属性を、安全に取り出す係
    #実行はexeファイルされているのか判定　sys frozenはこれってexeですか？　→　Trueならはい！
    if getattr(sys, 'frozen', False):
        #executableはexeファイルの場所を返していて.parentでその親フォルダを指す
        return Path(sys.executable).parent
    
    else:
        #Pythonでの実行はこのファイルから２つ上の階層を返す
        return Path(__file__).parents[1]
    

def get_data_dir_path():
    #ルートパスにdataをくっつけたパスを返す(/)で繋げるのがpathlib
    return get_root_path()/"data"