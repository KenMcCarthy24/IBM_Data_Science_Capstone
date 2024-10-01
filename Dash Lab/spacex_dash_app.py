# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# import warnings
# warnings.filterwarnings("ignore")

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_data.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create dictionary of launch sites
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}]
unique_sites = spacex_df["Launch Site"].unique()
for site in unique_sites:
    launch_sites.append({'label': site, 'value': site})


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=launch_sites, value='ALL',
                                             placeholder='Select a Launch Site Here', searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       10000: '10000'},
                                                value=[spacex_df["Payload Mass (kg)"].min(),
                                                       spacex_df["Payload Mass (kg)"].max()]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        filtered_df['class'] = filtered_df['class'].map({1: 'Success', 0: 'Failure'})
        value_counts = filtered_df['class'].value_counts()

        fig = px.pie(values=value_counts.values, names=value_counts.index, color=value_counts.index,
                     title=f"Total Successful Launches for site {entered_site}",
                     color_discrete_map={'Success': 'lightgreen', "Failure": 'red'})

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, entered_payload):
    if entered_site == 'ALL':
        filtered_df = spacex_df
        title = "Correlation between Payload and Success for All Sites"
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        title = f"Correlation between Payload and Success for Site {entered_site}"

    filtered_df = filtered_df[filtered_df["Payload Mass (kg)"].between(*entered_payload)]

    return px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=title)


# Run the app
if __name__ == '__main__':
    app.run_server()
