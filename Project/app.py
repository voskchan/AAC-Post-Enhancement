# Setup the Jupyter version of Dash
from jupyter_dash import JupyterDash

# Configure the necessary Python module imports
import dash_leaflet as dl
from dash import dcc
from dash import html
from dash import ctx
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output

# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#### FIX ME #####
# change animal_shelter and AnimalShelter to match your CRUD Python module file name and class name
from animal_shelter import AnimalShelter

###########################
# Data Manipulation / Model
###########################
# FIX ME update with your username and password and CRUD Python module name. NOTE: You will
# likely need more variables for your constructor to handle the hostname and port of the MongoDB
# server, and the database and collection names

username = "aacuser"
password = "cs340"
shelter = AnimalShelter(username, password)

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(shelter.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an
# invlaid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will return a new dataframe that does not contain the dropped column(s)
df.drop(columns=['_id'], inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)


#########################
# Dashboard Layout / View
#########################
app = JupyterDash('SimpleExample')

app.layout = html.Div([
    html.Div(id='hidden-div', style={'display': 'none'}),
    html.Center(html.B(html.H1('SNHU CS-340 Dashboard'))),
    html.H1("Chance Vosk"),
    html.Div(
        dcc.RadioItems(id='filter_type',
                       options=[{'label': 'Water rescue', 'value': 'water'},
                                {'label': 'Mountain rescue', 'value': 'mount'},
                                {'label': 'Disaster', 'value': 'disa'},
                                {'label': 'Reset', 'value': 'reset'}],
                       value='reset'),
    ),
    html.Hr(),
    dash_table.DataTable(
        id='datatable-id',
        selected_rows=[0],
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        # FIXME: Set up the features for your interactive data table to make it user-friendly for your client
        row_selectable="single",
        page_size=10

    ),
    html.Br(),
    html.Hr(),
    html.Hr(),
    html.Div(id='map-id',
             className='col s12 m6'),
    html.Div(id='graph-id',
             className='col s12 m6'),
    html.Img(src=app.get_asset_url('logo.png')),
])


#############################################
# Interaction Between Components / Controller
#############################################
# This callback will highlight a row on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback([Output('datatable-id', 'data'),
               Output('datatable-id', 'columns')],
              [Input('filter_type', 'value')])
def update_output(filter_type):
    if filter_type == 'water':
        df = pd.DataFrame.from_records(shelter.read({'animal_type': 'Dog',
                                                     'breed': {'$in': ['Labrador Retriever Mix',
                                                                       'Chesapeake Bay Retriever',
                                                                       'Newfoundland/Labrador Retriever',
                                                                       'Newfoundland Mix',
                                                                       'Newfoundland/Great Pyrenees']},
                                                     'sex_upon_outcome': 'Intact Female',
                                                     'age_upon_outcome_in_weeks': {'$gte': 26.0, '$lte': 156.0}}))
        df.drop(columns=['_id'], inplace=True)

    elif filter_type == 'mount':
        df = pd.DataFrame.from_records(shelter.read({'animal_type': 'Dog',
                                                     'breed': {'$in': ['German Shepard',
                                                                       'Alaskan Malamute',
                                                                       'Old English Sheepdog']},
                                                     'sex_upon_outcome': 'Intact Male',
                                                     'age_upon_outcome_in_weeks': {'$gte': 26.0, '$lte': 156.0}}))
        df.drop(columns=['_id'], inplace=True)

    elif filter_type == 'disa':
        df = pd.DataFrame.from_records(shelter.read({'animal_type': 'Dog',
                                                     'breed': {'$in': ['Doberman Pinscher',
                                                                       'German Shepard',
                                                                       'Golden Retriever',
                                                                       'Bloodhound',
                                                                       'Rottweiler']},
                                                     'sex_upon_outcome': 'Intact Male',
                                                     'age_upon_outcome_in_weeks': {'$gte': 20.0, '$lte': 300.0}}))
        df.drop(columns=['_id'], inplace=True)

    elif filter_type == 'reset':
        df = pd.DataFrame.from_records(shelter.read({}))
        df.drop(columns=['_id'], inplace=True)

    columns = [
        {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
    ]
    data = df.to_dict('records')
    return (data, columns)


@app.callback(
    Output('graph-id', 'children'),
    [Input('datatable-id', 'derived_viewport_data')])
def update_graphs(viewData):
    dff = pd.DataFrame.from_dict(viewData)
    return [dcc.Graph(
        figure=px.histogram(dff, x='breed'))
    ]


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):
    # FIXME Add in the code for your geolocation chart
    dff = pd.DataFrame.from_dict(viewData)
    # Because we only allow single row selection, the list can
    # be converted to a row index here
    if index is None:
        row = 0
    else:
        row = index[0]

    #assignment of variables is used to enhance readability
    lat = dff.loc[row,'location_lat']
    long = dff.loc[row,'location_long']
    name = dff.loc[row,'name']
    breed = dff.loc[row,'breed']
    animal = dff.loc[row, 'animal_type']
    age = dff.loc[row, 'age_upon_outcome']

    # Austin TX is at [30.75,-97.48]
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'},
               center=[lat, long], zoom=10, children=[
                dl.TileLayer(id="base-layer-id"),
                # Marker with tool tip and popup
                # Column 13 and 14 define the grid-coordinates for
                # the map
                # Column 4 defines the breed for the animal
                # Column 9 defines the name of the animal
                #dl.Marker(position=[dff.iloc[row, 13], dff.iloc[row, 14]],
                 #         children=[
                  #            dl.Tooltip(dff.iloc[row, 4]),
                   #           dl.Popup([
                    #              html.H1("Animal Name"),
                     #             html.P(dff.iloc[row, 9])
                      #        ])
                       #   ])
                dl.Marker(
                    position=[lat, long],
                    children=[
                        dl.Tooltip("({:.3f}, {:.3f})".format(lat, long)),
                        dl.Popup([
                            html.H2(name),
                            html.P([
                                html.Strong("{} | Age: {}".format(animal, age)),
                                html.Br(),
                                breed])
                            ])
                        ]
                )
            ])
    ]


app.run_server(debug=True)