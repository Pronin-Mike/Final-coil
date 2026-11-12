import traceback,json
try:
 exec(compile(open('D:/GameDevelop/FinalCoil/Scripts/install_compact_village.py',encoding='utf-8-sig').read(),'install_compact_village.py','exec'),{})
except BaseException:
 open('D:/GameDevelop/FinalCoil/Review/CompactVillage/install_error.txt','w',encoding='utf-8').write(traceback.format_exc())
 raise
