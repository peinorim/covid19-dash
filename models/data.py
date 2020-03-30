import requests


class Data:
    data = {}

    def __init__(self):
        self.init_data()

    def init_data(self):
        r = requests.get("https://peinorim.github.io/python_sandbox/data/covid-19/data.json")
        self.data = r.json()
