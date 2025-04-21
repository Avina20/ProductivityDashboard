import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
df = pd.read_csv('data/MTA_Monthly_2008.csv')
df['Month'] = pd.to_datetime(df['Month'])
df['Year'] = df['Month'].dt.year

# Initialize app
app = dash.Dash(__name__)
app.title = 'NYC MTA Ridership'

# Layout
app.layout = html.Div([
    html.H1("📊 NYC MTA Ridership Dashboard"),

    html.Label("Select Transit Agency:"),
    dcc.Dropdown(
        options=[{'label': agency, 'value': agency} for agency in df['Agency'].unique()],
        value=df['Agency'].unique()[0],
        id='agency-dropdown'
    ),

    html.H2("📈 Monthly Ridership for Selected Agency"),
    dcc.Graph(id='ridership-line'),

    html.H2("📊 Yearly Ridership for Selected Agency"),
    dcc.Graph(id='yearly-bar'),

    html.H2("🏙️ Total Ridership by Agency (All Time)"),
    dcc.Graph(
        figure=px.bar(
            df.groupby('Agency', as_index=False)['Ridership'].sum(),
            x='Agency',
            y='Ridership',
            title='Total Ridership by Agency',
            color='Agency'
        )
    ),

    html.H2("🗓️ Total Monthly Ridership (All Agencies Combined)"),
    dcc.Graph(
        figure=px.line(
            df.groupby('Month', as_index=False)['Ridership'].sum(),
            x='Month',
            y='Ridership',
            title='Total Monthly Ridership Across All Agencies'
        )
    )
])

# Callback for agency-specific plots
@app.callback(
    [Output('ridership-line', 'figure'),
     Output('yearly-bar', 'figure')],
    [Input('agency-dropdown', 'value')]
)
def update_graphs(selected_agency):
    filtered_df = df[df['Agency'] == selected_agency]

    # Monthly line chart
    fig_line = px.line(
        filtered_df,
        x='Month',
        y='Ridership',
        title=f'{selected_agency} - Monthly Ridership'
    )

    # Yearly bar chart
    yearly = filtered_df.groupby('Year')['Ridership'].sum().reset_index()
    fig_bar = px.bar(
        yearly,
        x='Year',
        y='Ridership',
        title=f'{selected_agency} - Yearly Ridership'
    )

    return fig_line, fig_bar

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)
