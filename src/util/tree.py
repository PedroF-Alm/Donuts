import xml.etree.ElementTree as ET
from xml.dom import minidom

class Node():

    def __init__(self, data: str):
        self.data = data
        self.children = []
        self.parent = None
        self.xml_element = ET.Element("node", id="0")
        self.xml_element.set('data', str(data))                

    def set_xml_attribute(self, attr, value):
        self.xml_element.set(attr, value)
    
    def remove_xml_attribute(self, attr):
        self.xml_element.attrib.pop(attr, None)

    def load_from_xml(self, xml_file_name: str) -> None:
        try:
            tree = ET.parse(xml_file_name)
            xml_root = tree.getroot()
            
            raw_data = xml_root.get('data')
            self.data = None if raw_data == "None" else raw_data            
            self.xml_element.set('data', str(self.data))
            self.children = []
            
            for child in list(self.xml_element):
                self.xml_element.remove(child)
            
            def build_tree_recursive(current_node, current_xml_element):
                for xml_child in current_xml_element:                               
                    child_data = xml_child.get('data')                                    
                    new_node = Node(child_data)                                        
                    added_node = current_node.add_child(new_node)                                        
                    build_tree_recursive(added_node, xml_child)
            
            build_tree_recursive(self, xml_root)
            
            print(f"Success: tree loaded from {xml_file_name}")

        except FileNotFoundError:
            print(f"Error: file '{xml_file_name}' not found.")
        except ET.ParseError:
            print(f"Error: Malformed XML.")

    def add_child(self, child):         
        known = self.find(child.data)
        if known:            
            return known
        
        child.parent = self
        child.xml_element.set('id', str(len(self.children)))
        self.children.append(child)        
        self.xml_element.append(child.xml_element)

        return child
    
    def find(self, data: str):
        if self.data == data:            
            return self
        
        for c in self.children:
            res = c.find(data) 
            if res:
                return res
            
        return None

    def print_tree(self, xml_file_name: str = 'tree.xml') -> None:        
        xml_string = ET.tostring(self.xml_element, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

        with open(xml_file_name, 'w', encoding="utf-8") as f:
            f.write(pretty_xml)