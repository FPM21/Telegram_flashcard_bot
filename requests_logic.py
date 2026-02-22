import requests
from dotenv import load_dotenv
from notion_client import Client
import os


class Dictionary:
    def __init__(self, word, api="https://api.dictionaryapi.dev/api/v2/entries/en/"):
        self.sentence = None
        self.word = word
        self.resp = None
        self.api = api

    def getdefinition(self):
        try:
            resp = requests.get(f"{self.api}{self.word}")
            if resp.status_code == 200:
                for idx, i in enumerate(resp.json()[0]["meanings"][0]["definitions"]):
                    print(f"{idx + 1}: {i["definition"]}")
                self.resp = resp
                return self.word, self.resp
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
                self.chosen_def = int(chosen_def)
                if 1 <= self.chosen_def <= choices + 1:
                    break
            print(f"Choose numerical value between 1 and {choices + 1}")
        if self.chosen_def == choices + 1:
            definition_str = input("Provide your definition: ")
        else:
            definition_str = self.resp.json()[0]["meanings"][0]["definitions"][self.chosen_def - 1]["definition"]

        return definition_str

    def getsentence(self):
        self.sentence = input("Provide an example of use (or use generic one - leave blank): ")
        if self.sentence == "":
            try:
                self.sentence = (self.resp.json()[0]["meanings"][0]["definitions"][self.chosen_def - 1]["example"])
            except:
                self.sentence = ""

        return self.sentence


class Notion_edit:
    def __init__(self, word, definition, sentence):
        load_dotenv("APIs.env")
        self.API = os.getenv("NOTION_API")
        self.word = word
        self.definition = definition
        self.sentence = sentence

    def loadwordtonotion(self):
        client = Client(auth=self.API)
        client.pages.create(parent={"database_id": "97acee34534e45d2ba39c9b93f9777ca"},
                            properties={"Word / Phrase": {"title": [{"text": {"content": self.word}}]},
                                        "Definition": {"rich_text": [{"text": {"content": self.definition}}]},
                                        "Example Sentence": {"rich_text": [{"text": {"content": self.sentence}}]},
                                        "Source": {"select": {"name": "Telegram Bot"}}, })
