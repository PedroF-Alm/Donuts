import xml.etree.ElementTree as ET
from xml.dom import minidom

class Node():

    def __init__(self, data):
        self.data = data
        self.children = []  # List to store child nodes
        self.parent = None
        self.root = ET.Element("node", id="0")
        ET.indent(self.root, space="  ")        

    def add_child(self, child):
        child.parent = self
        self.children.append(child)        
        child_true_root = child.root
        child_root = ET.SubElement(self.root, "node", id=str(len(self.children)))
        for _ in child_true_root.findall('node'):
            ET.SubElement(child_root, "node", id=str(_.get('id')))
    

    def get_level(self):
        """Calculates the depth of the node in the tree."""
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        """Prints the tree structure with indentation."""
        xml_string = ET.tostring(self.root, encoding='utf-8')
        pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

        print(pretty_xml)