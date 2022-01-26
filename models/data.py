from datetime import datetime
import pandas as pd
import requests


class FranceData:

    def hosp_data(self):

        hosp_data = pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7")
        lines = list()
        for index, line in enumerate(hosp_data.values):
            line_data = list(line)[0]
            lines.append(line_data)
        return lines

    def vaccine_data(self):
        resp = requests.get('https://www.data.gouv.fr/fr/datasets/r/3c8e4999-df8f-4683-a2a8-6bae13813c39', verify=False)
        try:
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise Exception(f'Unable to get vaccine data : {e}')


class Data:
    data = {}

    def __init__(self):
        self.init_data()

    def init_data(self):
        df_conf = pd.read_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

        for index, line in enumerate(df_conf.values):
            country = line[1]
            lat = line[2]
            long = line[3]
            if pd.notnull(line[0]):
                country = line[0]
            self.data.update({country: []})

            for i in range(4, len(df_conf.columns.values)):
                date = datetime.strptime(df_conf.columns.values[i], '%m/%d/%y')
                val = int(line[i])
                self.data[country].append(
                    {'date': date.strftime("%Y-%m-%d"), 'confirmed': val, 'lat': lat, 'long': long})

        df_deat = pd.read_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

        for index, line in enumerate(df_deat.values):
            country = line[1]
            if pd.notnull(line[0]):
                country = line[0]
            if country not in self.data:
                self.data.update({country: []})

            for i in range(4, len(df_deat.columns.values)):
                val = int(line[i]) if pd.notnull(line[i]) else None
                self.data[country][i - 4].update({'deaths': val})

        self.data = dict(sorted(self.data.items()))
