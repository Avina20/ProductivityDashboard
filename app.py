import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
df = pd.read_csv('data/MTA_Monthly_2008.csv')
df['Month'] = pd.to_datetime(df['Month'])
df['Year'] = df['Month'].dt.year

# Precompute static plots
total_by_agency = px.bar(
    df.groupby('Agency', as_index=False)['Ridership'].sum(),
    x='Agency',
    y='Ridership',
    title='🏙️ Total Ridership by Agency',
    color='Agency'
)

monthly_total = px.line(
    df.groupby('Month', as_index=False)['Ridership'].sum(),
    x='Month',
    y='Ridership',
    title='🗓️ Total Monthly Ridership Across All Agencies'
)

# Initialize Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "MTA Ridership Dashboard"

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'margin': '40px'}, children=[

    html.H1("🚇 NYC MTA Ridership Dashboard", style={'textAlign': 'center'}),

    dcc.Tabs(id="tabs", value='tab-agency', children=[
        dcc.Tab(label='Agency Dashboard', value='tab-agency'),
        dcc.Tab(label='Aggregate Dashboard', value='tab-aggregate'),
    ], colors={'primary': '#1f77b4', 'background': '#f7f7f7', 'border': '#d6d6d6'}),

    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-agency':
        return html.Div([
            html.Label("Select Transit Agency:", style={'marginTop': '20px'}),
            dcc.Dropdown(
                options=[{'label': agency, 'value': agency} for agency in df['Agency'].unique()],
                value=df['Agency'].unique()[0],
                id='agency-dropdown',
                style={'width': '60%', 'marginBottom': '30px'}
            ),

            dcc.Graph(id='ridership-line'),
            dcc.Graph(id='yearly-bar'),
        ])
    elif tab == 'tab-aggregate':
        return html.Div([
            html.Div([
                dcc.Graph(figure=total_by_agency, style={'width': '48%', 'display': 'inline-block'}),
                dcc.Graph(figure=monthly_total, style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
            ])
        ])

# Callback for agency-specific plots
@app.callback(
    [Output('ridership-line', 'figure'),
     Output('yearly-bar', 'figure')],
    [Input('agency-dropdown', 'value')]
)
def update_agency_charts(selected_agency):
    filtered_df = df[df['Agency'] == selected_agency]

    line_fig = px.line(
        filtered_df,
        x='Month',
        y='Ridership',
        title=f'📈 Monthly Ridership: {selected_agency}'
    )

    yearly_df = filtered_df.groupby('Year')['Ridership'].sum().reset_index()
    bar_fig = px.bar(
        yearly_df,
        x='Year',
        y='Ridership',
        title=f'📊 Yearly Ridership: {selected_agency}',
        color='Year'
    )

    return line_fig, bar_fig

if __name__ == '__main__':
    app.run(debug=True)