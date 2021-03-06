from datetime import datetime

import plotly.graph_objects as go


class Timeline:

    def __init__(self, data=None, countries=None, type=None, dayone_mode=False):

        self.type = type
        self.countries = countries if countries else []
        self.data = data
        self.dayone_mode = dayone_mode

    def set_figure(self):
        fig = go.Figure()
        graph_title = ''

        iteration = self.countries if len(self.countries) > 0 else self.data

        for country in iteration:
            data = {
                "dates": [],
                "confirmed": [],
                "deaths": [],
                "recovered": []
            }
            day_str = 0
            for index, day in enumerate(self.data[country]):
                if (self.dayone_mode and day.get(self.type) >= 100) or self.dayone_mode is False:
                    if self.dayone_mode:
                        data['dates'].append(f"Day {day_str}")
                        day_str += 1
                    else:
                        data['dates'].append(datetime.strptime(day['date'], '%Y-%m-%d'))
                    data['confirmed'].append(day.get('confirmed'))
                    data['deaths'].append(day.get('deaths'))
                    if day.get('recovered') is None:
                        data['recovered'].append(self.data[country][index - 1].get('recovered'))
                    else:
                        data['recovered'].append(day.get('recovered'))

            if len(self.countries) != 1:
                graph_title = f'{self.type} cases' if self.dayone_mode is False else f'{self.type} cases from day 0'
                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data[self.type],
                    name=country,
                    opacity=0.8))
            else:
                graph_title = f'{self.countries[0]} cases' if self.dayone_mode is False else f'{self.countries[0]} {self.type} cases from day 0'
                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['confirmed'],
                    name="confirmed",
                    opacity=0.8))

                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['deaths'],
                    name="deaths",
                    opacity=0.8))

                fig.add_trace(go.Scatter(
                    x=data['dates'],
                    y=data['recovered'],
                    name="recovered",
                    opacity=0.8))

        # Use date string to set xaxis range
        fig['layout']['showlegend'] = True
        fig['layout']['height'] = 700

        fig.update_layout(
            paper_bgcolor="#222",
            plot_bgcolor="#222",
            title=graph_title,
            titlefont={"color": "#c9c9c9"},
            font=dict(
                color="#c9c9c9"
            ),
            xaxis=go.layout.XAxis(
                range=[datetime.strptime("2020-02-23", '%Y-%m-%d'), datetime.now()],
                autorange=self.dayone_mode,
                tickformat="%Y-%m-%d",
                gridcolor="#6F6F6F",
                linecolor='#6F6F6F',
                rangeslider=dict(
                    visible=True
                )
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#6F6F6F",
                tickfont={"color": "#c9c9c9"},
                linecolor='#6F6F6F'
            ),
        )
        return fig
