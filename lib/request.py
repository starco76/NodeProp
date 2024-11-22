import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Request:
    def __init__(self,base_url:str,
        token:str,) -> None:
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.ip='ip'
    
    def _req(self,path:str,data:dict={}):
        url = self.base_url + f"/node/{path.lstrip('/')}"
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.post(url,json=data,headers=headers,verify=False)
        return response.json()
        
    def check_node(self):
        return self._req('check',data={'ip':self.ip})
    
    def alarm(self,message:str):
        return self._req('alarm',{'message':message})
        
    def send_data(self, data: dict):
       
        return self._req('account-info',{'data':data})
        
    def get_accounts(self):
        accounts:list = self._req('accounts',data={'ip':self.ip})
        return accounts
    
    