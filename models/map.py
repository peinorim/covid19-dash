import plotly.graph_objects as go


class Map:

    def __init__(self, data=None, countries=None, type=None, tots=None):
        self.type = type
        self.data = data
        self.tots = tots
        self.countries = countries if countries else []

    def set_figure(self):
        fig = go.Figure()

        iteration = self.countries if len(self.countries) > 0 else self.data

        for country in iteration:
            if not self.data[country]:
                continue
            if self.type not in self.data[country][-1]:
                self.data[country][-1].update({self.type: 0})

            if self.data[country] and self.data[country][-1][self.type] and self.data[country][-1].get('long') and \
                    self.data[country][-1].get('lat'):
                fig.add_trace(go.Scattergeo(
                    lon=[self.data[country][-1]['long']],
                    lat=[self.data[country][-1]['lat']],
                    text=f'{country} : {self.data[country][-1][self.type]} {self.type}',
                    marker=dict(
                        size=round(self.data[country][-1][self.type] / (self.tots[self.type] / 400), 0),
                        line_color='rgb(40,40,40,0.6)',
                        line_width=0.5,
                        sizemode='area'
                    ),
                    name=country
                ))
        fig.update_layout(
            paper_bgcolor="#222",
            plot_bgcolor="#222",
            font=dict(
                color="#c9c9c9"
            ),
            title=f'World {self.type} cases map',
            titlefont={"color": "#c9c9c9"},
            height=700,
            showlegend=False,
            geo=dict(
                scope='world',
                landcolor='#c9c9c9',
                lakecolor="#222",
                bgcolor="#222"
            )
        )

        return fig
