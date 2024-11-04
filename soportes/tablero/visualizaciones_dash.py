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

# Define a standard figure width and height
figure_width = 800
figure_height = 400

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1("Productos bancarios: Tablero para la toma de decisiones",
            style={'textAlign': 'center', 'color': colors['text']}),
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
                              for col in data.select_dtypes(include=[object]).columns])
    ]),
    html.Br(),
])


@app.callback(
    Output(component_id='bar-chart', component_property='figure'),
    Input(component_id='categoria', component_property='value')
)
def update_graph(selected_cat):

    df_filtered = data.groupby(by=selected_cat).agg({'y_num': 'mean'}).reset_index()
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