import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from igraph import Graph
import xml.etree.ElementTree as ET
import os

last_modified_time = 0

def build_graph_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    g = Graph(directed=True)
    labels = []
    mapping = {'-1': "⬜", '0': "🟨", '1': "🟫", '2': "🟧"}
    def add_node(element, parent_index=None):
        current_index = g.vcount()
        g.add_vertex()
        data = element.get('data')    
        heuristic_p1 = element.get('heuristic_p1') 
        heuristic_p2 = element.get('heuristic_p2') 
        move = int(element.get("move"))
        active = element.get('active')        
        if data != 'None':
            data = data.split(':')  
            grid = ''.join(f"{mapping[v] if i != move else mapping['2']}{'<br>' if (i + 1) % 6 == 0 else ''}" for i, v in enumerate(data[0].removeprefix('[').removesuffix(']').split(', ')))                        
            data = f"Grid: <br>{grid}<br>Player Rings: {data[1]}<br>Turn: {data[2]}<br>End: {data[3]}<br>Winner: {data[4]}<br>Steps: {data[5]}<br>Active: {False if active is None else True}<br>Heuristic: [{heuristic_p1}, {heuristic_p2}]"
        labels.append(data)
        if parent_index is not None:
            g.add_edge(parent_index, current_index)
        for child in element:
            add_node(child, current_index)
    add_node(root)
    return g, labels

app = None

def start_plot(xml_file_name, interval):
    global app

    if app is not None:
        return
    
    app = dash.Dash(__name__)    

    app.layout = html.Div([
        html.H1("Donuts State Tree", style={'font-family': 'Consolas, sans-serif', 'margin': '0', 'padding': '0', 'box-sizing': 'border-box', 'text-align': 'center'}),
        
        dcc.Interval(
            id='interval-component',
            interval=interval, 
            n_intervals=0
        ),
        
        dcc.Graph(
            id='live-tree-graph',
            style={'height': '90vh', 'width': '100%'}, 
            config={'scrollZoom': True} 
        ),
    ], style={'background': 'skyblue', 'margin': '0', 'padding': '0', 'box-sizing': 'border-box'})

    @app.callback(Output('live-tree-graph', 'figure'),
                Input('interval-component', 'n_intervals'),
                prevent_initial_call=False)

    def update_graph_live(n):
        global last_modified_time
        
        try:            
            # Watch xml file
            current_mtime = os.path.getmtime(xml_file_name)
                    
            if n > 0 and current_mtime <= last_modified_time:
                raise dash.exceptions.PreventUpdate
                        
            last_modified_time = current_mtime
            
            g, v_label = build_graph_from_xml(xml_file_name)

            # Layout
            nr_vertices = g.vcount()
            lay = g.layout('rt')
            position = {k: lay[k] for k in range(nr_vertices)}
            Y = [lay[k][1] for k in range(nr_vertices)]
            M = max(Y) if Y else 0

            Xn = [position[k][0] for k in range(nr_vertices)]
            Yn = [2*M - position[k][1] for k in range(nr_vertices)]

            Xe, Ye = [], []
            for edge in g.es:
                source, target = edge.tuple
                Xe += [position[source][0], position[target][0], None]
                Ye += [2*M - position[source][1], 2*M - position[target][1], None]

            node_colors = ['#886ce4']

            num_nodes = len(v_label)
            border_widths = [0] * num_nodes                    
            border_colors = ['rgba(0,0,0,0)'] * num_nodes            
            
            for i in range(0, len(v_label)):             
                label = v_label[i]
                if i > 0:
                    if 'End: True' in label:
                        node_colors.append('#16c60c')                    
                    elif 'Turn: 0' in label:
                        node_colors.append('#fff100')
                    else:
                        node_colors.append('#8e562e')   

                if 'Active: True' in label:
                    border_widths[i] = 3 
                    border_colors[i] = 'black'

            # Plotting
            fig = go.Figure()
            fig.add_scattergl(x=Xe, y=Ye, mode='lines', line=dict(color='black', width=1), hoverinfo='skip')
            fig.add_scattergl(x=Xn, 
                              y=Yn, 
                              mode='markers', 
                              marker=dict(size=20, 
                                          color=node_colors,
                                          line=dict(
                                              color=border_colors,
                                              width=border_widths
                                          )                                          
                                          ),
                              text=v_label, 
                              hoverinfo='text',
                              hoverlabel=dict(
                                bgcolor="#6175c1",          
                                font_size=16,             
                                font_color="white",       
                                bordercolor="gray"        
                              )
                             )
            
            fig.update_layout(
                dragmode='pan',
                hovermode='closest',  
                uirevision='constant', 
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            return fig

        except FileNotFoundError:
            raise dash.exceptions.PreventUpdate
        except Exception:            
            raise dash.exceptions.PreventUpdate

    # Start server
    app.run(debug=True, use_reloader=False)    