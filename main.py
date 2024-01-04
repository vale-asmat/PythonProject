import pandas as pd
import plotly.express as px
import os
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dataGenerator
from dash.exceptions import PreventUpdate
from dash import callback_context

# Load the data for the dashboard
loyers_df = dataGenerator.generate_data()
geojsondata = dataGenerator.load_geojson(loyers_df)
geojsondatacommune = dataGenerator.load_geojsoncommune(loyers_df)
wellbeing_df=dataGenerator.load_wellbeing_data()

# Initialize the Dash lib
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)

#Define list of options for the controllers
yearOptions=loyers_df['YEAR'].unique()
regionOptions=loyers_df['NOM_REGION'].unique()
depOptions=[]
for d in loyers_df['DEP'].unique():
    depOptions.append({'label':d+' - '+loyers_df[loyers_df['DEP']==d]['NOM_DEP'].unique()[0],'value':d})
depOptions = sorted(depOptions, key=lambda x: x['label'])

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
        html.Div(
            [
                dbc.Label("Département"),
                dcc.Dropdown(
                    id="dep_map",
                    options=depOptions,
                    value=''
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
                dbc.Tab(label="Accueil 	\U00002B50", tab_id="main"),
                dbc.Tab(label="Carte de loyers \U0001F30D", tab_id="carte"),
                dbc.Tab(label="Histogramme \U0001F4CA", tab_id="histogram"),
                dbc.Tab(label="Comparateur \U0001F50D", tab_id="comparateur"),
            ],
            id="tabs",
            active_tab="main",
        ),
    html.Div(id="tab-content", className="p-4")
])

# This section will provide the implementation of the functions to build the interaction of the dashboard
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
               #points='all', # Show all the points to know the Insee code of each point
               hover_data=['INSEE','NOM'], # Displaying this as part of the hover data to identify each point
               labels={
                   "DEP":"Département",
                   "LOYER_EUROM2":"Loyer par m2 (euros)",
                   "INSEE":"Code Postal",
                   "NOM":"Nom"
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
    filter_df=filter_df[['NOM','INSEE','LOYER_EUROM2']]
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
    fig = px.histogram(filter_df, x='LOYER_EUROM2',marginal="box", labels={"LOYER_EUROM2":"Loyer x m2 en euros"})
    fig.update_yaxes(title_text = "Nombre de communes", row=1, col=1)
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
    fig.add_trace(go.Box(x=filter_df1['LOYER_EUROM2'],name=region_1, hovertemplate='Loyer x m2 en euros : %{x}<extra></extra>'))
    fig.add_trace(go.Box(x=filter_df2['LOYER_EUROM2'],name=region_2, hovertemplate='Loyer x m2 en euros : %{x}<extra></extra>'))
    fig.update_xaxes(title_text = "Loyer x m2 en euros")
    return fig

@callback(
    Output(component_id='comparison-oecd', component_property='figure'),
    Input(component_id='region_1', component_property='value'),
    Input(component_id='region_2', component_property='value'),
)
def update_comp_oecd(region_1,region_2):
    """
    This callback takes two 'region' properties as input, 
    and renders the boxplot of each two regions accordingly, in order to visualize and compare them
    taking into account the oecd regional notes (quality of life)
    """
    selected1_df=wellbeing_df[(wellbeing_df['NOM_REGION']==region_1)|(wellbeing_df['NOM_REGION']==region_2)]
    fig=px.bar(selected1_df,x='NOM_REGION',
               barmode='group',
               y=['EDUCATION','TRAVAIL','REVENUS','SECURITE','SANTE','COMMUNAUTE','QUALITE DE VIE'],
               labels={"NOM_REGION":"Region","value":"Note","variable":"Critère"},)
    
    return fig

@callback(
    Output(component_id='cloro-map', component_property='figure'),
    Input(component_id='year_map', component_property='value'),
    Input(component_id='type_map', component_property='value'),
    Input(component_id='dep_map', component_property='value'),
)
def update_map(year_map,type_map,dep_map):
    """
    This callback takes the 'type'and 'year' properties as input, 
    and renders the clorophleth accordingly, in order to visualize the data geographically by department
    If any department is selected, it displays the whole map and the prices by department, if one department is
    selected, it will only highlight the selected department
    """
    dep_list=[]
    if (dep_map=='' or dep_map==None):
        subset=loyers_df[(loyers_df['YEAR']==year_map)&(loyers_df['TYPE']==type_map)]
    else:
        subset=loyers_df[(loyers_df['YEAR']==year_map)&(loyers_df['TYPE']==type_map)&(loyers_df['DEP']==dep_map)]
    
    for dep in subset['DEP'].unique():
            row=[dep,subset[subset['DEP']==dep]['LOYER_EUROM2'].mean(),subset[subset['DEP']==dep]['NOM_REGION'].unique()[0]]
            dep_list.append(row)
    #Center of france
    lat=46.227638
    lon=2.213749
    #Center of DOM
    if ((dep_map=='971') | (dep_map=='972') | (dep_map=='973') | (dep_map=='974') | (dep_map=='976')):
        lat=subset['LAT_CENTRE'].mean()
        lon=subset['LON_CENTRE'].mean()
    
    dep_df=pd.DataFrame(dep_list,columns=['DEP','LOYER_EUROM2','NOM_REGION'])
    fig = px.choropleth_mapbox(dep_df
                                , geojson=geojsondata, color='LOYER_EUROM2',
                            locations='DEP', featureidkey="properties.code",
                            center={"lat": lat, "lon": lon},
                            range_color=(0,20),
                            hover_data=['LOYER_EUROM2','DEP','NOM_REGION'],
                            labels={"LOYER_EUROM2":"Loyer x m2 en euros","DEP":"Département","NOM_REGION":"Région"},
                            mapbox_style="carto-positron", zoom=4)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

@callback(
    Output(component_id='cloro-map-dep', component_property='figure'),
    Input(component_id='year_map', component_property='value'),
    Input(component_id='type_map', component_property='value'),
    Input(component_id='dep_map', component_property='value'),
)     
def update_map_dep(year_map,type_map,dep_map):
    """
    This callback takes the 'type'and 'year' and 'department' properties as input, 
    and renders the clorophleth accordingly, in order to visualize the data geographically by commune in 
    an specific department
    If any department is selected, it displays a blank map, if one department is
    selected, it will only zoom to the deparment and display the prices by each commune
    """
    if (dep_map!='' or dep_map!=None):
        subset=loyers_df[(loyers_df['YEAR']==year_map)&(loyers_df['TYPE']==type_map)&(loyers_df['DEP']==dep_map)]
    fig = px.choropleth(subset
                            , geojson=geojsondatacommune, color='LOYER_EUROM2',
                            locations='INSEE', featureidkey="properties.insee_com",
                            center={"lat": 46.227638, "lon": 2.213749},
                            range_color=(0,20),
                            hover_data=['LOYER_EUROM2','INSEE','NOM'],
                            labels={"LOYER_EUROM2":"Loyer x m2 en euros","INSEE":"Code INSEE","NOM":"Commune"},
                            projection="natural earth",
                            scope='europe'
                            )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
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
                dbc.Col(
                    dcc.Loading(
                            id="loading-1",
                            type="default",
                            children=dcc.Graph(figure={}, id='controls-and-graph')
                        ),
                    )
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                dbc.Row(dash_table.DataTable(id='principal-table' ,data=loyers_df[(loyers_df['TYPE']=='app')&(loyers_df['YEAR']=='2018')].to_dict('records'), page_size=10,
                                             filter_action='native',
                                             sort_action='native',
                                             columns=[
                                                    {'name': 'Nom de Commune', 'id': 'NOM', 'type': 'text'},
                                                    {'name': 'Code Postal', 'id': 'INSEE', 'type': 'text'},
                                                    {'name': 'Loyer par m2 en euros', 'id': 'LOYER_EUROM2', 'type': 'numeric'},
                                                ],
                                             )),
                ])
        elif active_tab == "carte":
            return html.Div(
                [dbc.Col([
                dbc.Row(controls_map_tab),
                dbc.Row(
                    [dbc.Col([
                        html.Br(),
                        dbc.Row(html.H3("Map des loyers par département")),
                        html.Br(),
                        dcc.Loading(
                            id="loading-1",
                            type="default",
                            children=dcc.Graph(figure={}, id='cloro-map')
                        ),
                    ],md=7),
                    dbc.Col([
                        html.Br(),
                        dbc.Row(html.H3("Map des loyers par commune")),
                        html.Br(),
                        dcc.Loading(
                            id="loading-1",
                            type="default",
                            children=dcc.Graph(figure={}, id='cloro-map-dep')
                        ),
                    ])])
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                ])
        elif active_tab == "histogram":
            return html.Div(
                [dbc.Col([
                dbc.Col(controls_main_tab),
                dbc.Row(dcc.Graph(figure={}, id='histogram'))
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
                dbc.Row([
                    dbc.Col([
                        html.Div("Chaque région est mesurée sur des sujets importants pour le bien-être selon l'OECD. Les valeurs des indicateurs sont exprimées sous forme de score compris entre 0 et 10. Un score élevé indique une meilleure performance par rapport aux autres régions."),
                        dcc.Graph(figure={},id='comparison-oecd')]),
                ])
                ]
            return dbc.Col(graph)
    return "No tab selected"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)