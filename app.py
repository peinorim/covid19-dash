import locale
import os
from datetime import datetime

import dash
import dash_html_components as html
import dash_core_components as dcc

import dash_bootstrap_components as dbc
import redis
from dash.dependencies import Input, Output
from flask_caching import Cache

from models.bar import Bar
from models.data import Data, FranceData
from models.forecast import Forecast
from models.map import Map
from models.pie import Pie
from models.timeline import Timeline

external_stylesheets = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_external_path='assets')
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_cache():
    rs = redis.StrictRedis(
        host=os.environ.get('REDIS_HOST', '127.0.0.1'),
        port=os.environ.get('REDIS_PORT', '6379'),
        db=os.environ.get('REDIS_DB', '0'),
        password=os.environ.get('REDIS_PASSWORD', '')
    )
    rs.ping()
    return Cache(app.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST', '127.0.0.1'),
        'CACHE_REDIS_PORT': os.environ.get('REDIS_PORT', '6379'),
        'CACHE_REDIS_DB': os.environ.get('REDIS_DB', '0'),
        'CACHE_REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD', '')
    })


cache = get_cache()
TIMEOUT_STANDARD = 3600

DEFAULT_TYPE = 'confirmed'
DEFAULT_COUNTRY = "France"
DEFAULT_COUNTRIES = ["France", "United Kingdom", "Spain", "Italy", "Germany"]


@cache.memoize(timeout=TIMEOUT_STANDARD)
def init_data():
    data = Data().data

    countries = []
    types = [
        {'label': "Confirmed", 'value': "confirmed"},
        {'label': "Deaths", 'value': "deaths"},
        {'label': "Recovered", 'value': "recovered"},
    ]

    tots = {
        'last_date': None,
        'confirmed': 0,
        'deaths': 0,
        'recovered': 0
    }

    for country in data:
        if len(data[country]) > 0:
            countries.append({'label': country, 'value': country})
            tots['confirmed'] += data[country][-1].get('confirmed', 0)
            tots['deaths'] += data[country][-1].get('deaths', 0)
            tots['recovered'] += data[country][-1].get('recovered', 0)
            tots['last_date'] = datetime.strptime(data[country][-1].get('date'), '%Y-%m-%d')
    return data, countries, types, tots


@cache.memoize(timeout=TIMEOUT_STANDARD)
def vaccine_data():
    json_data = FranceData().vaccine_data()
    if json_data:
        vaccine_france_data = {
            'date': [],
            'n_cum_dose1': [],
            'n_cum_dose2': [],
        }
        for data in json_data:
            vaccine_france_data.get('date').append(datetime.strptime(data.get('jour'), '%Y-%m-%d'))
            vaccine_france_data.get('n_cum_dose1').append(data.get('n_cum_dose1'))
            vaccine_france_data.get('n_cum_dose2').append(data.get('n_cum_dose2'))

        return vaccine_france_data


@cache.memoize(timeout=TIMEOUT_STANDARD)
def hosp_data():
    list_data = FranceData().hosp_data()
    hosp_france_data = {
        'date': [],
        'hosp': [],
        'rea': []
    }
    for data in list_data:
        raw_data = data.split(';')
        if int(raw_data[1].replace('"', '')) == 0:
            if raw_data[2].replace('"', '') not in hosp_france_data.get('date'):
                hosp_france_data.get('date').append(raw_data[2].replace('"', ''))

            index = hosp_france_data.get('date').index(raw_data[2].replace('"', ''))

            if len(hosp_france_data.get('hosp')) == index:
                hosp_france_data.get('hosp').append(int(raw_data[3]))
            else:
                hosp_france_data.get('hosp')[index] += int(raw_data[3])

            if len(hosp_france_data.get('rea')) == index:
                hosp_france_data.get('rea').append(int(raw_data[4]))
            else:
                hosp_france_data.get('rea')[index] += int(raw_data[4])
    return hosp_france_data


data, countries, types, tots = init_data()
vaccine_data = vaccine_data()
hosp_data = hosp_data()

timeline_all_start = Timeline(data=data, countries=DEFAULT_COUNTRIES, type=DEFAULT_TYPE)
timeline_one_start = Timeline(data=data, countries=[DEFAULT_COUNTRY], type=DEFAULT_TYPE)
timeline_dayone_start = Timeline(data=data, countries=DEFAULT_COUNTRIES, type=DEFAULT_TYPE, dayone_mode=True)
forecast_start = Forecast(data=data, country=DEFAULT_COUNTRY, type=DEFAULT_TYPE)
map_start = Map(data=data, countries=DEFAULT_COUNTRIES, type=DEFAULT_TYPE, tots=tots)
pie_start = Pie(data=data[DEFAULT_COUNTRY], country=DEFAULT_COUNTRY)
bar = Bar(data=data[DEFAULT_COUNTRY], type=DEFAULT_TYPE, country=DEFAULT_COUNTRY)
timeline_france_vaccine = Timeline(data=vaccine_data, type=DEFAULT_TYPE)
bar_france_hosp = Bar(data=hosp_data, type=DEFAULT_TYPE)

hidden = ''
if os.environ.get('FORECAST', "0") != "1":
    hidden = 'hidden'

app.layout = html.Div(children=[
    html.H1(f"COVID-19 Worldwide data", style={"textAlign": "center", "padding": "20px 0 10px 0"}),
    html.H6(f"Last update on : {tots['last_date']:%Y-%m-%d}", style={"textAlign": "center", "paddingBottom": "20px"}),
    html.Header([
        dbc.Row(
            [
                html.Div(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4('{0:n}'.format(tots['confirmed']), className="card-title"),
                                html.H6("Confirmed", className="card-subtitle")
                            ]
                        )
                    ), className="col-md-4"
                ),
                html.Div(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4(
                                    f"{'{0:n}'.format(tots['deaths'])} ({round((tots['deaths'] / tots['confirmed']) * 100, 1)}%)",
                                    className="card-title"),
                                html.H6("Deaths", className="card-subtitle")
                            ]
                        )
                    ), className="col-md-4"
                ),
                html.Div(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4(
                                    f"{'{0:n}'.format(tots['recovered'])} ({round((tots['recovered'] / tots['confirmed']) * 100, 1)}%)",
                                    className="card-title"),
                                html.H6("Recovered", className="card-subtitle")
                            ]
                        )
                    ), className="col-md-4"
                )
            ], className="col-md-12", style={"paddingBottom": "20px"}
        ),
        html.Div([
            html.Div(
                dcc.Dropdown(
                    id='countries-dropdown',
                    options=countries,
                    multi=True,
                    placeholder="Select one or several countries",
                    value=DEFAULT_COUNTRIES
                ), className="col-md-3"
            ),
            html.Div(
                dcc.Dropdown(
                    id='types-dropdown',
                    options=types,
                    multi=False,
                    clearable=False,
                    value=DEFAULT_TYPE,
                    placeholder="Select a type of data",
                ), className="col-md-3"
            )
        ], className="col-md-12 row")
    ], className="row"),
    dbc.Row([
        html.Div([dcc.Graph(id='timeline-all-graph', figure=timeline_all_start.set_figure())], className="col-md-6"),
        html.Div([dcc.Graph(id='map-graph', figure=map_start.set_figure())], className="col-md-6"),
        html.Div([dcc.Graph(id='timeline-dayone-graph', figure=timeline_dayone_start.set_figure())],
                 className="col-md-12"),
        html.Div(
            html.Div(
                dcc.Dropdown(
                    id='country-dropdown',
                    options=countries,
                    clearable=False,
                    value='France',
                    multi=False,
                    placeholder="Select one country",
                ), className="col-md-3"
            ), className="col-md-12 row"
        ),
        html.Div([dcc.Graph(id='timeline-one-graph', figure=timeline_one_start.set_figure())], className="col-md-7"),
        html.Div([dcc.Graph(id='pie-one-graph', figure=pie_start.set_figure())], className="col-md-5"),
        html.Div([dcc.Graph(id='bar-graph', figure=bar.set_figure())], className="col-md-12"),
        html.Div([dcc.Graph(id='forecast-graph', figure=forecast_start.set_figure())], className=f"col-md-12 {hidden}"),
        html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            f"{'{0:n}'.format(vaccine_data.get('n_cum_dose1')[-1])} (+{'{0:n}'.format(vaccine_data.get('n_cum_dose1')[-1] - vaccine_data.get('n_cum_dose1')[-2])})",
                            className="card-title"),
                        html.H6(f"Nb of 1st dose given on {vaccine_data.get('date')[-1]:%Y-%m-%d }", className="card-subtitle")
                    ]
                )
            ), className="col-md-4"
        ),
        html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            f"{'{0:n}'.format(hosp_data.get('hosp')[-1])} ({'+' if hosp_data.get('hosp')[-1] - hosp_data.get('hosp')[-2] > 0 else ''}{'{0:n}'.format(hosp_data.get('hosp')[-1] - hosp_data.get('hosp')[-2])})",
                            className="card-title"),
                        html.H6(f"People hospitalized on {hosp_data.get('date')[-1]}", className="card-subtitle")
                    ]
                )
            ), className="col-md-4"
        ),
        html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            f"{'{0:n}'.format(hosp_data.get('rea')[-1])} ({'+' if hosp_data.get('rea')[-1] - hosp_data.get('rea')[-2] > 0 else ''}{'{0:n}'.format(hosp_data.get('rea')[-1] - hosp_data.get('rea')[-2])})",
                            className="card-title"),
                        html.H6(f"People in intensive care (rea) on {hosp_data.get('date')[-1]}", className="card-subtitle")
                    ]
                )
            ), className="col-md-4"
        ),
        html.Div([dcc.Graph(id='timeline-france-vaccines',
                            figure=timeline_france_vaccine.set_vaccine_figure(title='France vaccines'))],
                 className="col-md-6"),
        html.Div(
            [dcc.Graph(id='bar-france-hosp', figure=bar_france_hosp.set_hosp_data(title="France hospitalisation"))],
            className="col-md-6"),
    ]
    ),
    html.Footer([
        html.A("Data provided by CSSEGISandData", href="https://github.com/CSSEGISandData/COVID-19", target="_blank"),
    ], className="footer")

], className="container-fluid")


@app.callback([
    Output(component_id='timeline-all-graph', component_property='figure'),
    Output(component_id='map-graph', component_property='figure'),
    Output(component_id='timeline-dayone-graph', component_property='figure'),
],
    [
        Input(component_id='countries-dropdown', component_property='value'),
        Input(component_id='types-dropdown', component_property='value'),
    ]
)
def update_countries(countries, type):
    new_timeline_all = Timeline(data=data, countries=countries, type=type)
    new_map_all = Map(data=data, countries=countries, type=type, tots=tots)
    new_timeline_dayone = Timeline(data=data, countries=countries, type=type, dayone_mode=True)

    return new_timeline_all.set_figure(), new_map_all.set_figure(), new_timeline_dayone.set_figure()


@app.callback([
    Output(component_id='timeline-one-graph', component_property='figure'),
    Output(component_id='forecast-graph', component_property='figure'),
    Output(component_id='pie-one-graph', component_property='figure'),
    Output(component_id='bar-graph', component_property='figure'),
],
    [
        Input(component_id='country-dropdown', component_property='value'),
        Input(component_id='types-dropdown', component_property='value'),
    ]
)
def update_country(country, type):
    new_timeline_one = Timeline(data=data, countries=[country], type=type)
    new_forecast = Forecast(data=data, country=country, type=type)
    new_pie = Pie(data=data[country], country=country)
    new_bar = Bar(data=data[country], country=country, type=type)

    return new_timeline_one.set_figure(), new_forecast.set_figure(), new_pie.set_figure(), new_bar.set_figure()


if __name__ == '__main__':
    app.run_server(debug=True)
