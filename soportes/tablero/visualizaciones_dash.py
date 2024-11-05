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

data = pd.read_csv("bank-full.csv", sep=";")
data['y_num'] = data['y'].apply(lambda x: int(x == 'yes'))

bins = [0, 25, 35, 45, 55, 65, 75, 100]
labels = ['<25', '25-35', '35-45', '45-55', '55-65', '65-75','75+']
months=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels, right=False)
data['age_group'] = pd.Categorical(data['age_group'],categories=labels, ordered=True)
data['month'] = pd.Categorical(data['month'],categories=months, ordered=True)



cat_feats=['job','marital','education','default','housing','loan','contact','month','poutcome','age_group']
cat_feats_pie=['marital','education','default','housing','loan','contact','poutcome','age_group']


# Define a standard figure width and height
figure_width = 1200
figure_height = 400


def calculate_metrics(data):
    total_records = len(data)
    total_subscription = data['y_num'].sum()
    general_subscription_rate = total_subscription / total_records
    return total_records, total_subscription, general_subscription_rate

# Calculate initial metrics
total_records, total_subscription, general_subscription_rate = calculate_metrics(data)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1("Productos bancarios: Tablero para la toma de decisiones",
            style={'textAlign': 'center', 'color': colors['text']}),     
    html.P("""Este tablero ayuda al equipo comercial a analizar rápidamente las tasas de suscripción y los segmentos de clientes con mayor probabilidad de suscripción a depósitos a plazo fijo.
            \nSección 1: Métricas generales de clientes y suscripciones, incluyendo el porcentaje general de suscripción.
            \nSección 2: Detalle interactivo por categoría (ej. edad, empleo) para ver tasas de suscripción específicas.
            \nSección 3: Métricas solo para clientes suscritos, con desglose por características.
            \nSección 4: Modelo de clasificación para ingresar características de un cliente específico y ver su probabilidad de suscripción.""",
                style={
                    "font-size": "14px",
                    "line-height": "0.5",
                    "white-space": "pre-line"
                }
            ),
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 20}, children=[
        html.Div(children=[
            html.H3(f"Total de Registros: {total_records:,}", style={'color': colors['text']}),
        ], style={'textAlign': 'center', 'width': '38%', 'border': '1px solid lightgray', 'padding': 10, 'borderRadius': 5}),
        html.Div(children=[
            html.H3(f"Total de Suscripciones: {total_subscription:,}", style={'color': colors['text']}),
        ], style={'textAlign': 'center', 'width': '38%', 'border': '1px solid lightgray', 'padding': 10, 'borderRadius': 5}),
        html.Div(children=[
            html.H3(f"Porcentaje de suscripcion: {general_subscription_rate:.2%}", style={'color': colors['text']}),
        ], style={'textAlign': 'center', 'width': '38%', 'border': '1px solid lightgray', 'padding': 10, 'borderRadius': 5}),
        
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
    dcc.Graph(id='pie-chart', style={'width': f'{figure_width}px', 'height': f'{figure_height}px'}),
    dcc.Markdown('''
        Este grafico le permite observar los clientes inscritos a un producto de depositos fijos en el banco, 
        como se distributyen dentro de las categoria seleccionada.
    ''', style={'color': colors['text']}),
    html.Div([
        html.Span("Filtrar por categoria:", style={'color': colors['text']}),
        dcc.Dropdown(id='categoria_2', value='marital',
                     options=[{'label': col, 'value': col}
                              for col in cat_feats_pie])
    ]),

    html.H3("Test Your Client", style={'color': colors['text']}),
    html.Div([
        html.Span("Ingrese la probabilidad estimada de suscripción:", style={'color': colors['text']}),
        dcc.Input(id='user-probability', type='number', value=0.15, min=0, max=1, step=0.01),
        dcc.Graph(id='comparison-bar-chart', style={'width': f'{figure_width}px', 'height': f'{figure_height}px'}),
        dcc.Markdown('''
        En azul se encuentra la probabilidad de suscripcion a el producto. Dadas las caracteristicas brindadas de el cliente en evaluacion, 
        podemos observar la probabilidad esperadas de suscripcion de este cleinte en rojo.

    ''', style={'color': colors['text']}),
    ])
])

@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='categoria_2', component_property='value')
)
def update_pie_chart(col_for_group):
    filtered_data = data[data['y_num'] == 1]
    fig = px.pie(filtered_data, names=col_for_group)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title=f'Distribución de {col_for_group.capitalize()} de Clientes que Suscribieron',
        title_x=0.5  # Center the chart title
    )
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

@app.callback(
    Output(component_id='comparison-bar-chart', component_property='figure'),
    Input(component_id='user-probability', component_property='value')
)
def update_comparison_chart(user_probability):
    comparison_data = pd.DataFrame({'Metric': ['Probabilidad de suscripcion general', 'Probabilidad de cliente especifico'],
                                    'Value': [general_subscription_rate, user_probability]})
    fig = px.bar(comparison_data, x='Metric', y='Value', color='Metric')
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        title='Comparison of Subscription Rates',
        title_x=0.5  # Center the chart title
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8040)