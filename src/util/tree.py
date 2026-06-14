import xml.etree.ElementTree as ET
from xml.dom import minidom

class Node():

    def __init__(self, data: str):
        self.data = data
        self.children = []
        self.parent = None  
        self.node_index = {}    
        self.heuristic_p1 = -float('inf')
        self.heuristic_p2 = -float('inf')
        self.move = -1           

    def load_from_xml(self, xml_file_name: str) -> None:
        try:
            context = ET.iterparse(xml_file_name, events=('start', 'end'))
            
            stack = [self]
            
            for event, elem in context:
                if event == 'start':
                    if elem.get('data') == 'None': 
                        continue
                    
                    data = elem.get('data')                
                    new_node = Node(data)                    
                    new_node.heuristic_p1 = int(elem.get('heuristic_p1'))
                    new_node.heuristic_p2 = int(elem.get('heuristic_p2'))
                    new_node.move = int(elem.get('move'))
                    stack[-1].add_child(new_node)
                    stack.append(new_node)
                    
                elif event == 'end':
                    elem.clear()
                    if len(stack) > 1:
                        stack.pop()

        except FileNotFoundError:
            #print(f"Error: file '{xml_file_name}' not found.")
            pass
        except ET.ParseError:
            print(f"Error: Malformed XML.")    

    def add_child(self, child):        
        root = self.get_root()      

        known = root.node_index.get(child.data)          
        if known is not None:            
            return known           
        
        child.parent = self
        self.children.append(child)
        root.node_index[child.data] = child

        return child
    
    def get_root(self):
        root = self
        while root.parent is not None:
            root = root.parent            
        return root
    
    def to_xml_element(self, active_node=None) -> ET.Element:
        element = ET.Element("node", data=str(self.data))
        element.set('heuristic_p1', str(self.heuristic_p1))
        element.set('heuristic_p2', str(self.heuristic_p2))
        element.set('move', str(self.move))
        
        if self == active_node:
            element.set('active', 'True')
            
        for idx, child in enumerate(self.children):
            child_element = child.to_xml_element(active_node)
            child_element.set('id', str(idx))
            element.append(child_element)
            
        return element

    def save_to_xml(self, xml_file_name: str = 'tree.xml', active_node=None) -> None:
        root_element = self.to_xml_element(active_node)
        xml_string = ET.tostring(root_element, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
        
        with open(xml_file_name, 'w', encoding="utf-8") as f:
            f.write(pretty_xml)