import json
import os

from models.covid_data import NetData


class Data:
    data = {}

    def __init__(self):
        self.init_data()

    def init_data(self):
        NetData()
        with open(f"{os.getcwd()}/models/data.json", 'r+') as json_file:
            self.data = json.load(json_file)
