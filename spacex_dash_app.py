# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Collect all launch sites to be given as options in a drop down menu
launch_sites = list(set(spacex_df["Launch Site"].to_list()))
site_options = [{"label": "All sites", "value": "ALL"}]
for site in launch_sites:
    temp_dict = {}
    temp_dict["label"] = site
    temp_dict["value"] = site
    site_options.append(temp_dict)

print(spacex_df.head())


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # The default select value is for ALL sites
                                html.Div(dcc.Dropdown(id='site-dropdown',
                                             options=site_options,
                                             value="ALL",
                                             placeholder="Select launch site",
                                             searchable=True
                                            )),
                                html.Br(),

                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),

                                html.Div(dcc.RangeSlider(id='payload-slider',
                                                         min=0, max=10000, step=1000,
                                                         marks={0: "0",
                                                                2500: "2500",
                                                                5000: "5000",
                                                                7500: "7500",
                                                                10000: "10000"},
                                                          value=[min_payload, max_payload])),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total successful launches by site')
        return fig

    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

        fig = px.pie(filtered_df, 
                 names='class', 
                 title=f'Launch successes from {entered_site}')
        return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload_range):
    low_payload, high_payload = payload_range
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= low_payload) & (spacex_df["Payload Mass (kg)"] <= high_payload)]
    if entered_site == 'ALL':
        title_string = "Correlation between payload and success for all sites"
    else:
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        title_string = f"Correlation between payload and success at {entered_site}"

    fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=title_string)
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
