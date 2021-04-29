import os
from math import inf
import numpy as np
import plotly.graph_objects as go

PERIODS = 100


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

        m = Prophet()
        m.fit(self.format_forecast())
        future = m.make_future_dataframe(periods=PERIODS)
        forecast = m.predict(future)

        fig = self.plot_plotly(m, forecast, uncertainty=True, plot_cap=True, trend=True, changepoints=True,
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

    def plot_plotly(self, m, fcst, uncertainty=True, plot_cap=True, trend=False, changepoints=False,
                    changepoints_threshold=0.01, xlabel='ds', ylabel='y', figsize=(900, 600)):
        prediction_color = 'yellow'
        error_color = 'grey'  # '#0072B2' with 0.2 opacity
        actual_color = 'white'
        cap_color = 'black'
        trend_color = '#B23B00'
        line_width = 3
        marker_size = 6

        data = []
        # Add actual
        data.append(go.Scatter(
            name='Actual',
            x=m.history['ds'],
            y=m.history['y'],
            marker=dict(color=actual_color, size=marker_size),
            mode='markers'
        ))
        # Add lower bound
        if uncertainty and m.uncertainty_samples:
            data.append(go.Scatter(
                x=fcst['ds'],
                y=fcst['yhat_lower'],
                mode='lines',
                line=dict(width=0),
                hoverinfo='skip'
            ))
        # Add prediction
        data.append(go.Scatter(
            name='Predicted',
            x=fcst['ds'],
            y=fcst['yhat'],
            mode='lines',
            line=dict(color=prediction_color, width=line_width),
            fillcolor=error_color,
            fill='tonexty' if uncertainty and m.uncertainty_samples else 'none'
        ))
        # Add upper bound
        if uncertainty and m.uncertainty_samples:
            data.append(go.Scatter(
                x=fcst['ds'],
                y=fcst['yhat_upper'],
                mode='lines',
                line=dict(width=0),
                fillcolor=error_color,
                fill='tonexty',
                hoverinfo='skip'
            ))
        # Add caps
        if 'cap' in fcst and plot_cap:
            data.append(go.Scatter(
                name='Cap',
                x=fcst['ds'],
                y=fcst['cap'],
                mode='lines',
                line=dict(color=cap_color, dash='dash', width=line_width),
            ))
        if m.logistic_floor and 'floor' in fcst and plot_cap:
            data.append(go.Scatter(
                name='Floor',
                x=fcst['ds'],
                y=fcst['floor'],
                mode='lines',
                line=dict(color=cap_color, dash='dash', width=line_width),
            ))
        # Add trend
        if trend:
            data.append(go.Scatter(
                name='Trend',
                x=fcst['ds'],
                y=fcst['trend'],
                mode='lines',
                line=dict(color=trend_color, width=line_width),
            ))
        # Add changepoints
        if changepoints and len(m.changepoints) > 0:
            signif_changepoints = m.changepoints[
                np.abs(np.nanmean(m.params['delta'], axis=0)) >= changepoints_threshold
                ]
            data.append(go.Scatter(
                x=signif_changepoints,
                y=fcst.loc[fcst['ds'].isin(signif_changepoints), 'trend'],
                marker=dict(size=50, symbol='line-ns-open', color=trend_color,
                            line=dict(width=line_width)),
                mode='markers',
                hoverinfo='skip'
            ))

        layout = dict(
            showlegend=False,
            width=figsize[0],
            height=figsize[1],
            yaxis=dict(
                title=ylabel
            ),
            xaxis=dict(
                title=xlabel,
                type='date',
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label='1w',
                             step='day',
                             stepmode='backward'),
                        dict(count=1,
                             label='1m',
                             step='month',
                             stepmode='backward'),
                        dict(count=6,
                             label='6m',
                             step='month',
                             stepmode='backward'),
                        dict(count=1,
                             label='1y',
                             step='year',
                             stepmode='backward'),
                        dict(step='all')
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
            ),
        )
        fig = go.Figure(data=data, layout=layout)
        return fig
