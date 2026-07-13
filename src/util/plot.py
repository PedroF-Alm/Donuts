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
        heuristic = element.get('heuristic') 
        move_attr = element.get("move")
        move = int(move_attr) if move_attr is not None else -1
        active = element.get('active')        
        
        if data != 'None' and data is not None:
            data_parts = data.split(':')  
            grid = ''.join(f"{mapping[v] if i != move else mapping['2']}{'<br>' if (i + 1) % 6 == 0 else ''}" for i, v in enumerate(data_parts[0].removeprefix('[').removesuffix(']').split(', ')))                
            data_str = f"Grid: <br>{grid}<br>Player Rings: {data_parts[1]}<br>Turn: {data_parts[2]}<br>End: {data_parts[3]}<br>Winner: {data_parts[4]}<br>Steps: {data_parts[5]}<br>Active: {active == 'True'}<br>Heuristic: {heuristic}"

        labels.append(data_str)
        
        if parent_index is not None:
            g.add_edge(parent_index, current_index)

        # Recursively continue down the tree branch for children matching active conditions
        for child in element:            
            # Fixed XPath syntax by adding the universal selector '*'
            if child.find('.//*[@active="True"]') is not None or child.get('active') == 'True':
                add_node(child, current_index)
                        
        possible_moves_attr = element.get('possible_moves')
        possible_moves = int(possible_moves_attr) if possible_moves_attr is not None else 0
        if possible_moves > 1:
            sibling_index = g.vcount()
            g.add_vertex()
            labels.append(f"Possible Moves: {possible_moves-(1 if element.get('active') != 'True' else 0)}")
                
            g.add_edge(current_index, sibling_index)

    add_node(root)
    return g, labels

app = None

def start_plot(xml_file_name, interval):
    global app

    if app is not None:
        return
    
    app = dash.Dash(__name__)    

    app.layout = html.Div([
        html.H1("Donuts State Tree", style={'font-family': 'Consolas, sans-serif', 'margin': '0', 'padding': '20px 0', 'text-align': 'center'}),
        
        dcc.Interval(
            id='interval-component',
            interval=interval, 
            n_intervals=0
        ),
        
        dcc.Graph(
            id='live-tree-graph',
            style={'height': '85vh', 'width': '100%'}, 
            config={'scrollZoom': True} 
        ),
    ], style={'background': 'skyblue', 'margin': '0', 'padding': '0', 'box-sizing': 'border-box', 'min-height': '100vh'})

    @app.callback(Output('live-tree-graph', 'figure'),
                  Input('interval-component', 'n_intervals'),
                  prevent_initial_call=False)
    def update_graph_live(n):
        global last_modified_time
        
        try:            
            current_mtime = os.path.getmtime(xml_file_name)
                    
            if n > 0 and current_mtime <= last_modified_time:
                raise dash.exceptions.PreventUpdate
                        
            last_modified_time = current_mtime
            
            g, v_label = build_graph_from_xml(xml_file_name)

            nr_vertices = g.vcount()
            if nr_vertices == 0:
                raise dash.exceptions.PreventUpdate

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

            node_colors = []
            border_widths = [0] * nr_vertices                    
            border_colors = ['rgba(0,0,0,0)'] * nr_vertices            
            
            for i in range(nr_vertices):             
                label = v_label[i]
                if i == 0:
                    node_colors.append('#886ce4')  # Root node default color
                else:
                    if 'End: True' in label:
                        node_colors.append('#16c60c')                    
                    elif 'Turn: 0' in label:
                        node_colors.append('#fff100')
                    elif 'Turn: 1' in label:
                        node_colors.append('#8e562e')   
                    elif 'Possible Moves' in label:
                        node_colors.append('#d3d3d3')  # Visual distinction for un-explored counts
                    else:
                        node_colors.append("#6ea7f1")
                        
                if 'Active: True' in label:
                    border_widths[i] = 3 
                    border_colors[i] = 'black'

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
                                font_size=14,             
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
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig

        except FileNotFoundError:
            raise dash.exceptions.PreventUpdate
        except Exception:            
            raise dash.exceptions.PreventUpdate

    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    # Example initialization execution loop
    # start_plot("game_tree.xml", 2000)
    pass