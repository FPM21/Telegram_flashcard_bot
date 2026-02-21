import requests

class Api_request:
    def __init__(self, api="https://api.dictionaryapi.dev/api/v2/entries/en/"):
        self.api = api

    def getdefinition(self, word):
        self.word = word
        try:
            x = requests.get(f"{self.api}{self.word}")
            if x.status_code == 200:
                for idx, i in enumerate(x.json()[0]["meanings"][0]["definitions"]):
                    print(f"{idx}: {i["definition"]}")
            else:
                print(f"Status code: {x.status_code}")
        except Exception as e:
            print(e)



ask = Api_request()
ask.getdefinition("weed")
