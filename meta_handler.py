from lib.mt5 import Request,MT5Handler
from config import *

req=Request(BASE_MASTER_URL,token)

meta =MT5Handler(req,meta_path)
meta.start()
