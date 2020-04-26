import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd


def summary_card(title, text="0"):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H6(title, className="card-subtitle"),
                html.H2(text, className="card-text mt-2")
            ])
        )
    )


def time_series(df):
    dates = pd.concat([df['Confirmed On'], df['Recovered On'], df['Deceased On']])
    dates = dates[dates.notnull()].sort_values().unique()
    fig = go.Figure(layout={
            # todo: fix ticks
        }
    )

    # add Cumulative
    fig.add_trace(go.Scatter(
            x=dates, 
            y=[ df[df['Confirmed On']<=i]['Confirmed On'].count() for i in dates ],
            name="Cumilative",
            line=dict(dash='dash')
        )
    )

    # add Confirmed
    fig.add_trace(go.Scatter(
            x=dates, 
            y=[ df[df['Confirmed On']==i]['Confirmed On'].count() for i in dates ],
            name="Confirmed Cases"
        )
    )

    # add Recovered
    fig.add_trace(go.Scatter(
            x=dates, 
            y=[ df[df['Recovered On']==i]['Recovered On'].count() for i in dates ],
            name="Recovered"
        )
    )

    # add Deceased
    fig.add_trace(go.Scatter(
            x=dates, 
            y=[ df[df['Deceased On']==i]['Deceased On'].count() for i in dates ],
            name="Deaths"
        )
    )

    return dcc.Graph(figure=fig)


def doughnut_nationalities(df):
    fig = go.Figure(data=[
        go.Pie(
            labels=df['Nationality'].unique(), 
            values=[df[df['Nationality']==i]['Nationality'].count() for i in  df['Nationality'].unique()], 
            hole=.3
            )
        ]
    )
    return dcc.Graph(figure=fig)