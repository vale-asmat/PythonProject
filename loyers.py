import pandas as pd
import plotly.express as px
import os
import sys
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import geopandas as gpd
import json

root_path = sys.path[0]

fichiers=['app_2018.csv','app_2022_3.csv','app_2022_12.csv','app_2022.csv','maison_2018.csv','maison_2022.csv']

frames=[]

for f in fichiers:
    partial_df=pd.read_csv(os.path.join(root_path,"fichierscsv",f),encoding='latin1',delimiter=';',decimal=',')
    partial_df['type']=f[0:f.index('_')]
    partial_df['annee']=f[f.index('_')+1:f.index('_')+5]
    frames.append(partial_df)


loyers_df=pd.concat(frames,ignore_index=True)

loyers_df=loyers_df[['id_zone','INSEE','DEP','REG','loypredm2','TYPPRED','type','annee']]
loyers_df['INSEE']=loyers_df['INSEE'].astype(str)
loyers_df['INSEE']=loyers_df['INSEE'].str.zfill(5)
    

index_region_df=pd.read_csv(os.path.join(root_path,"fichierscsv",'indexvieregionsfr.csv'),encoding='latin1',delimiter=';',decimal=',')

loyers_df=loyers_df.merge(index_region_df.rename(columns={"code":"REG"}),on=["REG"])

with open(os.path.join(root_path,"geojsonfiles",'correspondance-code-insee-code-postal.geojson')) as f:
    geojsondata = json.load(f)



#app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


#Radio buttons style
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

controls_general_graph=dbc.Card(
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
                    id="annee",
                    options=loyers_df['annee'].unique(),
                    value='2018'
                )
            ]
        ),
        html.Div(
            [
                dbc.Label("Région"),
                dcc.Dropdown(
                    id='REG',
                    options=loyers_df['REG'].unique(), 
                    value=11)
            ]
        )
    ],
    body=True,
)

controls_map=dbc.Card(
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
                    id="annee_map",
                    options=loyers_df['annee'].unique(),
                    value='2018'
                )
            ]
        ),
    ],
    body=True,
)

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
                    id="annee_c",
                    options=loyers_df['annee'].unique(),
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
                                id='REG_1',
                                options=loyers_df['REG'].unique(), 
                                value=11)
                        ]),
                        dbc.Col([
                            dbc.Label("Région 2"),
                            dcc.Dropdown(
                                id='REG_2',
                                options=loyers_df['REG'].unique(), 
                                value=11)
                        ])
                    ]
                ),
                
            ]
        ),
    ],
    body=True,
)




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

# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='type', component_property='value'),
    Input(component_id='annee', component_property='value'),
    Input(component_id='REG', component_property='value')
)
def update_graph(type,annee,REG):
    filter_df=loyers_df[(loyers_df['type']==type)&(loyers_df['annee']==annee)&(loyers_df['REG']==REG)]
    fig=px.box(filter_df, y="DEP", x="loypredm2",
               points='all', # can also be outliers, or suspectedoutliers, or False
               hover_data=['INSEE'],
               labels={
                   "DEP":"Département",
                   "loypredm2":"Loyer par m2 (euros)"
               }
    )
    return fig

@callback(
    Output(component_id='principal-table', component_property='data'),
    Input(component_id='type', component_property='value'),
    Input(component_id='annee', component_property='value'),
    Input(component_id='REG', component_property='value')
)
def update_table(type,annee,REG):
    filter_df=loyers_df[(loyers_df['type']==type)&(loyers_df['annee']==annee)&(loyers_df['REG']==REG)]
    return filter_df.to_dict('records')

@callback(
    Output(component_id='histogram', component_property='figure'),
    Input(component_id='type', component_property='value'),
    Input(component_id='annee', component_property='value'),
    Input(component_id='REG', component_property='value')
)
def update_histogram(type,annee,REG):
    filter_df=loyers_df[(loyers_df['type']==type)&(loyers_df['annee']==annee)&(loyers_df['REG']==REG)]
    fig = px.histogram(filter_df, x='loypredm2',marginal="box")
    return fig


@callback(
    Output(component_id='comparison-graph', component_property='figure'),
    Input(component_id='type_c', component_property='value'),
    Input(component_id='REG_1', component_property='value'),
    Input(component_id='REG_2', component_property='value'),
    Input(component_id='annee_c', component_property='value'),
)
def update_comp_graph(type_c,REG_1,REG_2,annee_c):
    filter_df1=loyers_df[(loyers_df['type']==type_c)&(loyers_df['annee']==annee_c)&((loyers_df['REG']==REG_1))]
    filter_df2=loyers_df[(loyers_df['type']==type_c)&(loyers_df['annee']==annee_c)&((loyers_df['REG']==REG_2))]
    fig = go.Figure()
    fig.add_trace(go.Box(y=filter_df1['loypredm2'],name=REG_1)
               )
    fig.add_trace(go.Box(y=filter_df2['loypredm2'],name=REG_2)
               )
    return fig

# TODO: show two tables displaying the environment, population and another notes to compare two regions
@callback(
    Output(component_id='comparison-table1', component_property='data'),
    Input(component_id='REG_1', component_property='value'),
)
def update_comparison_table1(REG_1):
    filter_df=index_region_df[(index_region_df['code']==REG_1)]
    return filter_df.to_dict('records')

@callback(
    Output(component_id='comparison-table2', component_property='data'),
    Input(component_id='REG_2', component_property='value'),
)
def update_comparison_table2(REG_2):
    filter_df=index_region_df[(index_region_df['code']==REG_2)]
    dict={}
    for col in filter_df:
        dict[col][REG_2]=list(filter_df[col]).pop()
    # return filter_df.to_dict('records')
    return dict


# TODO: it takes a lot of time to load, find a solution to that
@callback(
    Output(component_id='cloro-map', component_property='figure'),
    Input(component_id='annee_map', component_property='value'),
    Input(component_id='type_map', component_property='value'),
)
def update_map(annee_map,type_map):
    subset=loyers_df[(loyers_df['annee']==annee_map)&(loyers_df['type']==type_map)]
    fig = px.choropleth(data_frame=subset, geojson=geojsondata,locations='INSEE',color='loypredm2',
                     featureidkey="properties.insee_com",
                   )
    fig.update_layout(
        width=1000, height=800,
        geo = dict(
            projection_scale=17, #this is kind of like zoom
            center=dict(lat=46.227638, lon=2.213749), # this will center on the point
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
                dbc.Col(controls_general_graph,md=4),
                dbc.Col(dcc.Graph(figure={}, id='controls-and-graph'))
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                dbc.Row(dash_table.DataTable(id='principal-table' ,data=loyers_df[(loyers_df['type']=='app')&(loyers_df['annee']=='2018')].to_dict('records'), page_size=10)),
                dbc.Row(dcc.Graph(figure={},id='histogram'))
                ])
        elif active_tab == "carte":
            return html.Div(
                [dbc.Col([
                dbc.Row(controls_map),
                dbc.Row(dcc.Graph(figure={}, id='cloro-map'))
                    ],style={
                        "align-items":"center"
                    }),
                html.Hr(),
                ])
        elif active_tab=="comparateur":
            d=index_region_df[(index_region_df['code']==11)]
            fig=go.Figure()
            fig.add_box()
            graph=[
                dbc.Row(controls_comparison_graph),
                dbc.Row([dbc.Col(dcc.Graph(figure={}, id='comparison-graph'))]),
                dbc.Row([dbc.Col(dash_table.DataTable(id='comparison-table1' ,data=d.to_dict('records'))),
                            dbc.Col(dash_table.DataTable(id='comparison-table2' ,data=d.to_dict('records')))])]
            return dbc.Col(graph)
    return "No tab selected"







# Run the app
if __name__ == '__main__':
    app.run(debug=True)