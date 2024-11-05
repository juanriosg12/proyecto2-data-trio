import dash
from dash import dcc  # dash core components
from dash import html  # dash html components
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Define a color palette for consistency
colors = {'background': '#f5f5f5',
          'text': '#333333',
          'primary': '#4CAF50',
          'accent': '#FF9800'}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

data = pd.read_csv("../../data/bank-full.csv", sep=";")
data['y_num'] = data['y'].apply(lambda x: int(x == 'yes'))

bins = [0, 25, 35, 45, 55, 65, 75, 100] 
labels = ['<25', '25-35', '35-45', '45-55', '55-65', '65-75','75+']
months=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels, right=False)
data['age_group'] = pd.Categorical(data['age_group'],categories=labels, ordered=True)
data['month'] = pd.Categorical(data['month'],categories=months, ordered=True)



cat_feats=['job','marital','education','default','housing','loan','contact','month','poutcome','age_group']


# Define a standard figure width and height
figure_width = 800
figure_height = 400



def calculate_metrics(data):
    total_records = len(data)

    total_subscription = data['y_num'].sum()
    return total_records, total_subscription

# Calculate initial metrics
total_records, total_subscription = calculate_metrics(data)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1("Productos bancarios: Tablero para la toma de decisiones",
            style={'textAlign': 'center', 'color': colors['text']}),


    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 20}, children=[
    html.Div(children=[
        html.H3(f"Total de Registros: {total_records:,}", style={'color': colors['text']}),
    ], style={'textAlign': 'center', 'width': '48%', 'border': '1px solid lightgray', 'padding': 10, 'borderRadius': 5}),
    html.Div(children=[
        html.H3(f"Total de Suscripciones: {total_subscription:,}", style={'color': colors['text']}),
    ], style={'textAlign': 'center', 'width': '48%', 'border': '1px solid lightgray', 'padding': 10, 'borderRadius': 5}),
    ]),

    html.H3("Porcentaje de suscripcion deposito fijo", style={'color': colors['text']}),
    dcc.Graph(id='bar-chart', style={'width': f'{figure_width}px', 'height': f'{figure_height}px'}),
    dcc.Markdown('''
        Este grafico le permite observar el porcenataje de subscricion al producto de depostios fijos en el banco.
        Puede interactuctuar con la categoria, para observar las categorias de usuario que desee analizar la 
        diferencia del porcentaje de subscripcion del producto.

    ''', style={'color': colors['text']}),
    html.H6("Seleccione la categoria de agrupacion:", style={'color': colors['text']}),
    html.Div([
        html.Span("Categoria: ", style={'color': colors['text']}),
        dcc.Dropdown(id='categoria', value='job',
                     options=[{'label': col, 'value': col}
                              for col in cat_feats])
    ]),
    html.Br(),
    html.H3("Comportamiento de usuarios suscritos", style={'color': colors['text']}),
    dcc.Graph(id='pie-chart', style={'width': '50%', 'height': '300px'}),
    html.Div([
            html.Span("Filtrar por categoria:", style={'color': colors['text']}),
            dcc.Dropdown(id='categoria_2', value='marital',
                        options=[{'label': col, 'value': col}
                              for col in cat_feats])
        ])
])


@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='categoria_2', component_property='value')
)
def update_pie_chart(col_for_group):
    filtered_data = data[data['y_num'] == 1]
    fig = px.pie(filtered_data, names=col_for_group, title='Distribución de Ocupaciones de Clientes que Suscribieron')
    return fig

@app.callback(
    Output(component_id='bar-chart', component_property='figure'),
    Input(component_id='categoria', component_property='value')
)
def update_graph(selected_cat):

    df_filtered = data.groupby(by=selected_cat).agg({'y_num': 'mean'}).reset_index()
    if selected_cat in ['age_group','month']:
        df_filtered=df_filtered.sort_values(by=selected_cat)
    else:
        df_filtered=df_filtered.sort_values(by='y_num')
    df_filtered.rename(columns={"y_num": "porcentaje de suscritos"}, inplace=True)
    

    fig = px.bar(df_filtered, x=selected_cat, y='porcentaje de suscritos', color=selected_cat)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title_text=f"Porcentaje de Suscritos por {selected_cat.capitalize()}",  # Capitalize category for better readability
        title_x=0.5  # Center the chart title
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8040)