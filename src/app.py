import dash
from graphs import *
import pandas as pd

app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
df = pd.read_csv("../nodes_official.csv", parse_dates=['Confirmed On', 'Recovered On', 'Deceased On'])


app.layout = dbc.Container([
        # header
        dbc.Row(
            className="mt-md-5",
            children = dbc.Col([
                html.H3("MV Covid19 Dash", ),
                html.H4("A Simple dashboard for shits and giggles"),
            ])
        ),

        # summary row
        dbc.Row(
            className="mt-md-4",
            children=[
                summary_card("Total", text=df['Case'].count()),
                summary_card("Active", text=df[df['Deceased On'].isnull() & df['Recovered On'].isnull()]['ID'].count()),
                summary_card("Recovered", text=df[df['Recovered On'].notnull()]['ID'].count()),
                summary_card("Deaths", text=df[df['Deceased On'].notnull()]['ID'].count())
            ]
        ), 

        # graph row 1
        dbc.Row(
            className="mt-md-4",
            children = [
                dbc.Col(time_series(df), className="col-md-8"),
                dbc.Col(doughnut_nationalities(df), className="col-md-4")
            ]
        )

    ])




if __name__ == "__main__":
    app.run_server(debug=True)