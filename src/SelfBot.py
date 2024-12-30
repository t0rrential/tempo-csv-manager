# import discord
from time import sleep
import requests

class SelfBot():
    def __init__(self):
        pass
    
    def check(self, authToken):
        url = "https://discord.com/api/v9/users/@me/billing/country-code"

        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Authorization': authToken,
            'X-Discord-Locale': 'en-GB',
            'X-Debug-Options': 'bugReporterEnabled',
            'Origin': 'https://discord.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Length': '0',
            'TE': 'trailers'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload, timeout=30)
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            print(e)
            sleep(1)
            self.check(authToken)