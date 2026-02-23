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
            self.resp = requests.get(f"{self.api}{self.word}")
            if self.resp.status_code == 200:
                defs_text = "\n".join(
                    f"{idx + 1}: {meaning['definition']}"
                    for idx, meaning in enumerate(self.resp.json()[0]["meanings"][0]["definitions"])
                )
                self.resp_list = defs_text
                self.choices = len(self.resp.json()[0]["meanings"][0]["definitions"])
                return self.resp_list
            elif self.resp.status_code == 404:
                print("Word is not in API database")
                return None
            else:
                print(f"Status code: {self.resp.status_code}")
        except Exception as e:
            print(e)

    def choosedefinition(self, chosen_def):
        self.chosen_def = int(chosen_def)

        definition_str = self.resp.json()[0]["meanings"][0]["definitions"][self.chosen_def - 1]["definition"]

        return definition_str

    def getsentence(self, sentence):
        self.sentence = sentence
        if self.sentence.lower() == "skip":
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
                            properties={"Word / Phrase": {"title": [{"text": {"content": self.word.capitalize()}}]},
                                        "Definition": {"rich_text": [{"text": {"content": self.definition}}]},
                                        "Example Sentence": {"rich_text": [{"text": {"content": self.sentence}}]},
                                        "Source": {"select": {"name": "Telegram Bot"}}, })

        return f"""Word: {self.word.capitalize()}
definition: {self.definition}, 
example: {self.sentence}"""
