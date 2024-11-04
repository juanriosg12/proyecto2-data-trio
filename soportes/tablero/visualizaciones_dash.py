import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
# from dotenv import load_dotenv # pip install python-dotenv
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

data = pd.read_csv("../../data/bank-full.csv",sep =";")
data['y_num']=data['y'].apply(lambda x: int(x=='yes'))


app.layout = html.Div(
    [
    html.H1("Productos bancarios: Tablero para la toma de decisiones"),
    html.H3("Porcentaje de suscripcion deposito fijo"),
    dcc.Graph(id='bar-chart'),
    dcc.Markdown('''
        Este grafico le permite observar el porcenataje de subscricion al producto de depostios fijos en el banco.
        Puede interactuctuar con la categoria, para observar las categorias de usuario que desee analizar la 
        diferencia del porcentaje de subscripcion del producto.

    '''),
    html.H6("Seleccione la categoria de agrupacion:"),
    html.Div(["Categoria: ",
              dcc.Dropdown(id='categoria', value='job', 
                           options=['job','marital','education','default','housing','loan','contact','month','poutcome'])]),
    html.Br(),
    ]
)


@app.callback(
    Output(component_id='bar-chart',component_property='figure'),
    Input(component_id='categoria', component_property='value')
)




def update_graph(selected_cat):

    df_filtered=data.groupby(by=selected_cat).agg({'y_num':'mean'}).reset_index()
    df_filtered.rename(columns={"y_num":"porcentaje de suscritos"},inplace=True)

    fig = px.bar(df_filtered, x=selected_cat, y='porcentaje de suscritos', color=selected_cat)
    return fig
        

if __name__ == '__main__':
    app.run_server(debug=True, port=8040)