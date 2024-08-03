import pandas as pd

def parse_grid_positions(grid_position_str, cols):
    positions = list(map(int, grid_position_str.split(',')))
    rows = [(pos - 1) // cols + 1 for pos in positions]
    cols = [(pos - 1) % cols + 1 for pos in positions]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)
    row_span = max_row - min_row + 1
    col_span = max_col - min_col + 1
    return min_row, min_col, row_span, col_span

def generate_plotly_code(widgets, grid_size):
    rows, cols = map(int, grid_size.split('x'))
    has_filter = any(widget['type'] == 'Filter Box' for widget in widgets)

    function_definitions = []
    layout_components = []
    widget_counter = 1

    # Prepare data and imports
    code_header = [
        "from dash import Dash, dcc, html, Input, Output",
        "import dash_bootstrap_components as dbc",
        "import plotly.express as px",
        "import pandas as pd",
        "import warnings",
        "",
        "warnings.filterwarnings('ignore', category=FutureWarning)",
        "# Example table data",
        "table_data = {",
        "    'Spalte 1': [1, 2, 3, 4],",
        "    'Spalte 2': ['A', 'B', 'C', 'D'],",
        "    'Spalte 3': [10.1, 20.2, 30.3, 40.4]",
        "}",
        "table_df = pd.DataFrame(table_data)",
        "",
        "# Load data",
        "df = px.data.iris()",
        "# Initialize app with external stylesheets",
        "app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])",
        ""
    ]

    # Generate unique functions
    for widget in widgets:
        min_row, min_col, row_span, col_span = parse_grid_positions(widget['gridPosition']['gridPosition'], cols)
        widget_type = widget['type'].replace(' ', '')
        widget_name = widget.get('name', f'{widget_type}{widget_counter}')
        function_name = f'draw{widget_type}_{widget_name}'
        widget_counter += 1

        # Dynamically generate functions based on widget type
        if widget['type'] == 'Chart':
            function_definitions.append(f"""
def {function_name}():
    fig = px.bar(df, x='sepal_width', y='sepal_length', color='species').update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    id='graph',
                    figure=fig,
                    config={{'displayModeBar': False}},
                    style={{'height': '100%', 'width': '100%'}},
                    responsive=True
                )
            ]), style={{'height': '100%'}}
        )
    ], style={{'height': '100%', 'padding': '2px'}})
""")
        elif widget['type'] == 'Table':
            function_definitions.append(f"""
def {function_name}():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Table.from_dataframe(table_df, striped=True, bordered=True, hover=True, dark=True, responsive=True, style={{'width': '100%', 'overflowY': 'auto'}})
                ], style={{'height': '100%', 'overflowY': 'auto'}})
            ]), style={{'height': '100%', 'overflow': 'hidden'}}
        )
    ], style={{'height': '100%', 'padding': '2px'}})
""")
        elif widget['type'] == 'Text Block':
            function_definitions.append(f"""
def {function_name}(text='Text'):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H4(text),
                ], style={{'textAlign': 'center', 'color': 'white', 'height': '100%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}})
            ]), style={{'height': '100%'}}
        )
    ], style={{'height': '100%', 'padding': '2px'}})
""")
        elif widget['type'] == 'Filter Box':
            function_definitions.append(f"""
def {function_name}():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dcc.Dropdown(
                        id='filter-dropdown',
                        options=[
                            {{'label': 'Setosa', 'value': 'setosa'}},
                            {{'label': 'Versicolor', 'value': 'versicolor'}},
                            {{'label': 'Virginica', 'value': 'virginica'}}
                        ],
                        value=['setosa', 'versicolor', 'virginica'],
                        multi=True,
                        style={{'color': '#000'}}
                    )
                ], style={{'textAlign': 'center', 'padding': '10px'}})
            ]), style={{'height': '100%'}}
        )
    ], style={{'height': '100%', 'padding': '2px'}})
""")
        layout_components.append(f"            html.Div({function_name}(), style={{'gridColumn': '{min_col} / span {col_span}', 'gridRow': '{min_row} / span {row_span}', 'padding': '0px'}}),")

    # Layout definition
    layout_definition = [
        "# Define layout",
        "app.layout = html.Div([",
        "    dbc.Container([",
        "        html.Div(style={",
        "            'display': 'grid',",
        f"           'gridTemplateColumns': 'repeat({cols}, 1fr)',",
        f"           'gridTemplateRows': 'repeat({rows}, 1fr)',",
        "            'gap': '10px',",
        "            'height': '99vh'",
        "        }, children=[",
        f"{''.join(layout_components)}",
        "        ])",
        "    ], fluid=True, style={'height': '100vh', 'padding': '0', 'margin': '0', 'width': '100vw', 'overflow': 'hidden'})",
        "])",
        ""
    ]

    # Filter functionality (if applicable)
    if has_filter:
        filter_functionality = [
            "@app.callback(",
            "    Output('graph', 'figure'),",
            "    [Input('filter-dropdown', 'value')]",
            ")",
            "def update_graph(selected_values):",
            "    filtered_df = df[df['species'].isin(selected_values)]",
            "    fig = px.bar(",
            "        filtered_df, x='sepal_width', y='sepal_length', color='species'",
            "    ).update_layout(",
            "        template='plotly_dark',",
            "        plot_bgcolor='rgba(0, 0, 0, 0)',",
            "        paper_bgcolor='rgba(0, 0, 0, 0)',",
            "        margin=dict(l=20, r=20, t=20, b=20)",
            "    )",
            "    return fig",
            ""
        ]
    else:
        filter_functionality = []

    # Server start
    server_start = [
        "if __name__ == '__main__':",
        "    app.run_server(debug=True)"
    ]

    # Combine all parts
    full_code = "\n".join(code_header + function_definitions + layout_definition + filter_functionality + server_start)
    return full_code