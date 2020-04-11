from datetime import datetime

import plotly.graph_objects as go


class Bar:

    def __init__(self, data=None, country=None, type=None):

        self.type = type
        self.country = country
        self.data = data

    def set_figure(self):
        fig = go.Figure()
        data = {
            "dates": [],
            "cases": [],
        }

        for index, day in enumerate(self.data):
            if day.get(self.type) >= 100 and self.data[index - 1]:
                previous = 0 if index == 0 else index - 1
                data['dates'].append(datetime.strptime(day['date'], '%m/%d/%y'))
                data['cases'].append(day.get(self.type) - self.data[previous].get(self.type))

        graph_title = f'{self.country} {self.type} cases evolution over time'
        fig.add_trace(go.Bar(
            x=data['dates'],
            y=data['cases'],
            name=self.country,
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
                autorange=True,
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
