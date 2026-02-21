import requests


class Api_request:
    def __init__(self, api="https://api.dictionaryapi.dev/api/v2/entries/en/"):
        self.word = None
        self.resp = None
        self.api = api

    def getdefinition(self, word):
        self.word = word
        try:
            resp = requests.get(f"{self.api}{self.word}")
            if resp.status_code == 200:
                for idx, i in enumerate(resp.json()[0]["meanings"][0]["definitions"]):
                    print(f"{idx + 1}: {i["definition"]}")
                self.resp = resp
                return resp
            elif resp.status_code == 404:
                print("Word is not in API database")
            else:
                print(f"Status code: {resp.status_code}")
        except Exception as e:
            print(e)

    def choosedefinition(self):
        choices = len(self.resp.json()[0]["meanings"][0]["definitions"])

        while True:
            chosen_def = input(f"Choose defintion 1 - {choices} or provide your own - choose {choices + 1}: ")
            if chosen_def.isdigit():
                chosen_def = int(chosen_def)
                if 1 <= chosen_def <= choices + 1:
                    break
            print(f"Choose numerical value between 1 and {choices + 1}")
        if chosen_def == choices + 1:
            definition_str = input("Provide your definition: ")
        else:
            definition_str = self.resp.json()[0]["meanings"][0]["definitions"][chosen_def - 1]["definition"]

        return definition_str


ask = Api_request()
ask.getdefinition("car")
print(ask.choosedefinition())
