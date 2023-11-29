import pandas as pd
import plotly.express as px
import os
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import geopandas as gpd
import dataGenerator

# Load the data for the dashboard
loyers_df=dataGenerator.generate_data()
geojsondata=dataGenerator.load_geojson()

# Initialize the Dash lib
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#Define list of options for the controllers
yearOptions=loyers_df['YEAR'].unique()
regionOptions=loyers_df['NOM_REGION'].unique()

# Define the radio buttons style for the controller
radio_buttons_type=[
    {
        'label':
        [
            html.Img(src=os.path.join("assets",'appart.svg'),height=30,style={'padding':10}),
            html.Span("Appartement",style={'font-size':15, 'padding':10}),
        ],
        'value':'app',
    },
    {
        'label':
        [
            html.Img(src=os.path.join("assets",'house.svg'),height=30,style={'padding':10}),
            html.Span("Maison",style={'font-size':15, 'padding':10}),
        ],
        'value':'maison',
    },
]

# Define the layout for the controllers of the main tab
controls_main_tab=dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Type"),
                dcc.RadioItems(
                    id="type",
                    options=radio_buttons_type,
                    value='app'
                )
            ]
        ),
        html.Div(
            [
                dbc.Label("Année"),
                dcc.Dropdown(
                    id="year",
                    options=yearOptions,
                    value='2018'
                )
            ]
        ),
        html.Div(
            [
                dbc.Label("Région"),
                dcc.Dropdown(
                    id='region',
                    options=regionOptions, 
                    value='ILE-DE-FRANCE')
            ]
        )
    ],
    body=True,
)

# Define the layout for the controllers of the map tab
controls_map_tab=dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Type"),
                dcc.RadioItems(
                    id="type_map",
                    options=radio_buttons_type,
                    value='app'
                )
            ]
        ),
        html.Div(
            [
                dbc.Label("Année"),
                dcc.Dropdown(
                    id="year_map",
                    options=yearOptions,
                    value='2018'
                )
            ]
        ),
    ],
    body=True,
)

# Define the layout for the controllers of the comparison tab
controls_comparison_graph=dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Type"),
                dcc.RadioItems(
                    id="type_c",
                    options=radio_buttons_type,
                    value='app'
                )
            ]
        ),
         html.Div(
            [
                dbc.Label("Année"),
                dcc.Dropdown(
                    id="year_c",
                    options=yearOptions,
                    value='2018'
                )
            ]
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("Région 1"),
                            dcc.Dropdown(
                                id='region_1',
                                options=regionOptions, 
                                value='ILE-DE-FRANCE')
                        ]),
                        dbc.Col([
                            dbc.Label("Région 2"),
                            dcc.Dropdown(
                                id='region_2',
                                options=regionOptions, 
                                value='ILE-DE-FRANCE')
                        ])
                    ]
                ),
                
            ]
        ),
    ],
    body=True,
)

#Define the general layout of the dashboard
app.layout = dbc.Container([
    html.H1("Loyers"),
    html.Hr(),
    
    dbc.Tabs(
            [
                dbc.Tab(label="Main", tab_id="main"),
                dbc.Tab(label="Carte de loyers", tab_id="carte"),
                dbc.Tab(label="Comparateur", tab_id="comparateur"),
            ],
            id="tabs",
            active_tab="main",
        ),
    html.Div(id="tab-content", className="p-4")
])

# This section will provide the implementation of the functions to buils the interaction of the dashboard
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='type', component_property='value'),
    Input(component_id='year', component_property='value'),
    Input(component_id='region', component_property='value')
)
def update_graph(type,year,region):
    """
    This callback takes the 'type','year', and 'region' property as input, 
    and renders the box plot graph for each department in the region selected
    """
    filter_df=loyers_df[(loyers_df['TYPE']==type)&(loyers_df['YEAR']==year)&(loyers_df['NOM_REGION']==region)]
    fig=px.box(filter_df, y="DEP", x="LOYER_EUROM2",
               points='all', # Show all the points to know the Insee code of each point
               hover_data=['INSEE','NOM'], # Displaying this as part of the hover data to identify each point
               labels={
                   "DEP":"Département",
                   "LOYER_EUROM2":"Loyer par m2 (euros)"
               }
    )
    return fig

@callback(
    Output(component_id='principal-table', component_property='data'),
    Input(component_id='type', component_property='value'),
    Input(component_id='year', component_property='value'),
    Input(component_id='region', component_property='value')
)
def update_table(type,year,region):
    """
    This callback takes the 'type','year', and 'region' property as input, 
    and renders the table with the actual data if the user needs to see in depth each commune
    """
    filter_df=loyers_df[(loyers_df['TYPE']==type)&(loyers_df['YEAR']==year)&(loyers_df['NOM_REGION']==region)]
    return filter_df.to_dict('records')

@callback(
    Output(component_id='histogram', component_property='figure'),
    Input(component_id='type', component_property='value'),
    Input(component_id='year', component_property='value'),
    Input(component_id='region', component_property='value')
)
def update_histogram(type,year,region):
    """
    This callback takes the 'type','year', and 'region' property as input, 
    and renders the histogram with the applied filters
    """
    filter_df=loyers_df[(loyers_df['TYPE']==type)&(loyers_df['YEAR']==year)&(loyers_df['NOM_REGION']==region)]
    fig = px.histogram(filter_df, x='LOYER_EUROM2',marginal="box")
    return fig


@callback(
    Output(component_id='comparison-graph', component_property='figure'),
    Input(component_id='type_c', component_property='value'),
    Input(component_id='region_1', component_property='value'),
    Input(component_id='region_2', component_property='value'),
    Input(component_id='year_c', component_property='value'),
)
def update_comp_graph(type_c,region_1,region_2,year_c):
    """
    This callback takes the 'type','year', and two 'region' properties as input, 
    and renders the boxplot of each two regions accordingly, in order to visualize and compare them
    """
    filter_df1=loyers_df[(loyers_df['TYPE']==type_c)&(loyers_df['YEAR']==year_c)&((loyers_df['NOM_REGION']==region_1))]
    filter_df2=loyers_df[(loyers_df['TYPE']==type_c)&(loyers_df['YEAR']==year_c)&((loyers_df['NOM_REGION']==region_2))]
    fig = go.Figure()
    fig.add_trace(go.Box(y=filter_df1['LOYER_EUROM2'],name=region_1)
               )
    fig.add_trace(go.Box(y=filter_df2['LOYER_EUROM2'],name=region_2)
               )
    return fig

# TODO: it takes a lot of time to load, find a solution to that
@callback(
    Output(component_id='cloro-map', component_property='figure'),
    Input(component_id='year_map', component_property='value'),
    Input(component_id='type_map', component_property='value'),
)
def update_map(year_map,type_map):
    """
    This callback takes the 'type'and 'year' properties as input, 
    and renders the clorophleth accordingly, in order to visualize the data geographically by commune
    """
    subset=loyers_df[(loyers_df['YEAR']==year_map)&(loyers_df['TYPE']==type_map)]
    fig = px.choropleth(data_frame=subset, geojson=geojsondata,locations='INSEE',color='LOYER_EUROM2',
                     featureidkey="properties.insee_com",
                   )
    fig.update_layout(
        width=1000, height=1000,
        geo = dict(
            projection_scale=18,
            center=dict(lat=46.227638, lon=2.213749),
        ))
    return fig

@callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab  is not None:
        if active_tab == "main":
            return html.Div(
                [dbc.Row([
                dbc.Col(controls_main_tab,md=4),
                dbc.Col(dcc.Graph(figure={}, id='controls-and-graph'))
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                dbc.Row(dash_table.DataTable(id='principal-table' ,data=loyers_df[(loyers_df['TYPE']=='app')&(loyers_df['YEAR']=='2018')].to_dict('records'), page_size=10)),
                dbc.Row(dcc.Graph(figure={},id='histogram'))
                ])
        elif active_tab == "carte":
            return html.Div(
                [dbc.Col([
                dbc.Row(controls_map_tab),
                dbc.Row(dcc.Graph(figure={}, id='cloro-map'))
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                ])
        elif active_tab=="comparateur":
            fig=go.Figure()
            fig.add_box()
            graph=[
                dbc.Row(controls_comparison_graph),
                dbc.Row([dbc.Col(dcc.Graph(figure={}, id='comparison-graph'))]),
                ]
            return dbc.Col(graph)
    return "No tab selected"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)