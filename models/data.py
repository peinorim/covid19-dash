import requests


class Data:
    data = {}

    def __init__(self):
        self.init_data()

    def init_data(self):
        r = requests.get("https://peinorim.github.io/python_sandbox/data/covid-19/data.json")
        if r.status_code != 200:
            r = requests.get("https://raw.githubusercontent.com/peinorim/python_sandbox/master/data/covid-19/data.json")
        self.data = r.json()
