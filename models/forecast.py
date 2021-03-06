import os
from math import inf
import plotly.graph_objects as go

PERIODS = 30


class Forecast:

    def __init__(self, data=None, country=None, type=None):
        self.type = type
        self.country = country
        self.data = data

    def format_forecast(self):
        import pandas as pd
        forecast = {'ds': [], 'y': []}
        for res in self.data:
            if res == self.country:
                for day in self.data[res]:
                    forecast['ds'].append(day['date'])
                    forecast['y'].append(day[self.type])
        return pd.DataFrame.from_dict(forecast)

    def set_figure(self):
        if os.environ.get('FORECAST', "0") != "1":
            return {}
        from fbprophet import Prophet
        from fbprophet.plot import plot_plotly

        m = Prophet()
        m.fit(self.format_forecast())
        future = m.make_future_dataframe(periods=PERIODS)
        forecast = m.predict(future)

        fig = plot_plotly(m, forecast, uncertainty=True, plot_cap=True, trend=True, changepoints=True,
                          changepoints_threshold=0.01)

        fig['layout']['showlegend'] = True
        fig['layout']['width'] = inf
        fig['layout']['height'] = 700

        fig.update_layout(
            paper_bgcolor="#222",
            plot_bgcolor="#222",
            font=dict(
                color="#c9c9c9"
            ),
            titlefont={"color": "#c9c9c9"},
            title=f"{self.country} {self.type} cases trend forecast for the next {PERIODS} days",
            xaxis=go.layout.XAxis(
                tickformat="%Y-%m-%d",
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            ),
            yaxis=dict(showgrid=True),
        )
        return fig
