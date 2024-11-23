import MetaTrader5 as mt5
from time import sleep, time
from starco.utils import chunks
import math
from datetime import datetime
import importlib
import os
import shutil
from starco.debug import Debug
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from .request import Request


class MT5Handler:
    def __init__(
        self,
        req: Request,
        meta_path: list[str],
        first_login={'login': 52123848, 'password': 'TjZ!7qXq',
                     'server': 'Alpari-MT5-Demo'}
    ) -> None:
        self.first_login = first_login
        self.terminals: list = []
        self.acc_infos: list[dict] = []
        self.data = {}
        self.meta_path = meta_path
        self.log = Debug(True, log_name='log.log').debug
        self.symbols_info = {}
        self.req = req

    def _ready_path(self, path: str):
        return (path.rstrip('\\').rstrip('/'))+'\\terminal64.exe'

    def init_terminals(self):
        self.terminals = []
        for path in self.meta_path:
            try:
                path = self._ready_path(path)
                cls = self.check_terminal(path)
                self.terminals.append(cls)
            except Exception as e:
                self.req.alarm(f'{path} {e}')
                self.log(e,extra=path)
                continue

    
    def check_terminal(self, path: str):
        idx = len(self.terminals)
        base_path = mt5.__file__.replace(f'{os.sep}__init__.py', '')
        target = f"{base_path}{idx}"

        if not os.path.exists(target):
            shutil.copytree(base_path, target)
        mt = importlib.import_module(f'MetaTrader5{idx}')
        cfg = self.first_login
        cfg['timeout'] = 10000
        if mt.initialize(path, **cfg):
            return mt
        else:
            raise Exception(mt.last_error())
        mt.shutdown()

    def action(self):
        os.system('cls')
        print(f'count meta:{len(self.terminals)}\n start collecting')

        accounts = self.req.get_accounts()

        if not accounts or not self.terminals:
            return

        batch_accounts = chunks(accounts, math.ceil(
            len(accounts) / len(self.terminals)))

        with ThreadPoolExecutor(len(self.terminals)) as proccessor:
            # with ProcessPoolExecutor(len(self.terminals)) as proccessor:
            proccess = []
            for idx, item in enumerate(self.terminals):
                try:
                    batch = batch_accounts[idx]
                    proccess += [proccessor.submit(self.collect_data, idx, batch)]
                except:pass
            for future in as_completed(proccess):
                try:
                    data = future.result(timeout=2)
                except:
                    pass

    def get_deal_orders(self, cls, start_ts=None):
        now = datetime(datetime.now().year + 1, 1, 5)

        if start_ts == None:
            start_ts = datetime(1971, 1, 1)
        histories = cls.history_deals_get(start_ts, now)
        histories_orders = []  # cls.history_orders_get(start_ts, now)
        positions = cls.positions_get()
        return histories, histories_orders, positions

    def get_symbol_info(self, cls, symbol):
        if symbol in [None, '']:
            return {}
        saved = self.symbols_info.get(symbol)
        if saved:
            return saved
        cls.symbol_select(symbol, True)
        data = cls.symbol_info(symbol)._asdict()
        self.symbols_info[symbol] = data
        return data

    def get_history(self, cls, saved_tickets, histories, histories_orders, positions):
        position_data = {}
        out = []
        for position in positions:
            data = position._asdict()
            position_data[data['ticket']] = {
                'sl': data['sl'],
                'tp': data['tp'],
            }

        for history in histories:
            data = history._asdict()
            ticket = data['ticket']

            if ticket not in position_data and ticket in saved_tickets:
                continue
            position_id = data['position_id']
            position_info = position_data.get(position_id, {})
            data['sl'] = position_info.get('sl')
            data['tp'] = position_info.get('tp')
            symbol = data['symbol']
            data['digits'] = self.get_symbol_info(cls, symbol).get('digits', 0)
            out.append(data)
        return out

    def get_first_balance(self, histories):
        try:
            first_balance = histories[0]._asdict()['profit']
            return first_balance
        except:
            pass

    def collect_data(self, terminal_idx, accounts):

        cls: mt5 = self.terminals[terminal_idx]
        for account in accounts:
            ts = time()
            try:
                login = account['login']
                password = account['password']
                server = account['server']
                saved_tickets = account['saved_tickets']
                first_balance_needed = account['first_balance_needed']

                res = cls.login(login, password, server, timeout=2000)
                if not res:
                    continue
                # print(f"checking checker{i['login']}")
                account_info = cls.account_info()._asdict()
                if login != account_info['login']:
                    continue

                now_balance = account_info['balance']
                now_equity = account_info['equity']
                histories, histories_orders, positions = self.get_deal_orders(
                    cls, None)
                history = self.get_history(
                    cls, saved_tickets, histories, histories_orders, positions)
                response = {'ip': self.req.ip, 'login': login}

                # if 'account_info' in actions:
                response['account_info'] = account_info
                # if 'history' in actions:
                response['history'] = history
                # if 'now_balance' in actions:
                response['now_balance'] = now_balance
                # if 'now_equity' in actions:
                response['now_equity'] = now_equity

                if first_balance_needed:
                    response['first_balance'] = self.get_first_balance(
                        histories)
                response['time'] = datetime.now(tz=pytz.UTC).timestamp()
                res = self.req.send_data(response)
                print(res)

            except Exception as e:
                self.log(e)
            print(f"{login} checked {time() - ts:.2f} seconds")

            sleep(0.1)

    def start(self):
        print('initializing terminals')
        self.init_terminals()
        print('terminals initialized')
        last_check = 0
        while True:
            try:
                if time() - last_check > 60:
                    self.req.check_node()
                    last_check = time()
                
                    self.action()
            except Exception as e:
                self.req.alarm(str(e))
                self.log(e)

            sleep(0.5)
