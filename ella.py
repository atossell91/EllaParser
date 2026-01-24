from os import path
import json
from HtmlToTree import HtmlNode, HtmlToTree

class TickerCounter:
    def __init__(self, start=0, increment = 1):
        self.current_num = start
        self.increment = increment
    
    def get_current_num(self):
        return self.current_num

    def increment_ticker(self):
        self.current_num = self.current_num + self.increment

class JsBuilder:
    def __init__(self, name):
        self.root = None
        self.statements = []
        self.index_counter = TickerCounter(0, 1)
        self.component_name = name
        self.elems_arr_name = 'e'
        self.id_tag_name = 'data-name'
        self.id_tag_prefix = "id-"
        self.map_name = "map"
        self.initial_statements = [
            f'function {self.component_name}(){{',
            f'const {self.elems_arr_name}=[];',
            f'const {self.map_name}=new Map();'
        ]
        self.final_statements = [
            f'return{{elems:{self.elems_arr_name}[0],refs:{self.map_name}}}}}',
            f'export{{{self.component_name}}}'
        ]
        self.pretty_indent = "    "

    def is_id_attribute(self, name, value):
        return name == self.id_tag_name and value[0:len(self.id_tag_prefix)] == self.id_tag_prefix

    def apply_attributes(self, elem_index, attributes):
        for attribute in attributes:
            name = attribute[0]
            value = attribute[1]

            if self.is_id_attribute(name, value):
                key = value[len(self.id_tag_prefix):]
                statement = f'{self.map_name}.set("{key}",{self.elems_arr_name}[{elem_index}]);'
                self.statements.append(statement)
            else:
                statement = f'{self.elems_arr_name}[{elem_index}].setAttribute("{name}","{value}");'
                self.statements.append(statement)
    
    def apply_data(self, elem_index, data):
        statement = f'{self.elems_arr_name}[{elem_index}].innerHTML="{data.replace("\n", "<br>")}";'
        self.statements.append(statement)

    def create_element(self, tag):
        self.statements.append(f'{self.elems_arr_name}.push(document.createElement("{tag}"));')

    def create_text_element(self, data):
        self.statements.append(f'{self.elems_arr_name}.push(document.createTextNode("{data}"));')

    def append_element(self, parent_index, child_index):
        parent = f'{self.elems_arr_name}[{parent_index}]'
        child = f'{self.elems_arr_name}[{child_index}]'
        statement = f'{parent}.appendChild({child});'
        self.statements.append(statement)

    def start_walk(self, tree): 
        self.create_element(tree.tag_name)
        self.apply_attributes(self.index_counter.get_current_num(), tree.attributes)
        for child in tree.children:
            if child.type == "text":
                self.create_text_element(child.text)
                self.index_counter.increment_ticker()
                self.append_element(0, self.index_counter.get_current_num())
            else:
                self.walk(child, 0)

    def walk(self, tree, parent_index):
        self.create_element(tree.tag_name)
        self.index_counter.increment_ticker()
        self.apply_attributes(self.index_counter.get_current_num(), tree.attributes)
        self.append_element(parent_index, self.index_counter.get_current_num())

        for child in tree.children:
            if child.type == "text":
                new_parent = self.index_counter.get_current_num()
                self.create_text_element(child.text)
                self.index_counter.increment_ticker()
                self.append_element(new_parent, self.index_counter.get_current_num())
            else:
                self.walk(child, self.index_counter.get_current_num())

    def get_pretty_str(self):
        output = ''
        for statement in self.initial_statements:
            output = output + statement + '\n'

        for statement in self.statements:
            output = output + self.pretty_indent + statement + '\n'

        for statement in self.final_statements:
            output = output + statement + '\n'
        
        return output

    def get_ugly_str(self):
        output = ''
        for statement in self.initial_statements:
            output = output + statement

        for statement in self.statements:
            output = output + statement

        for statement in self.final_statements:
            output = output + statement
        
        return output

def tree_from_html(html):
    parser = HtmlToTree()
    parser.feed(html)
    tree = parser.get_tree()
    return tree

def process(file_path, output_dir):
    file = path.split(file_path)[1]
    name = file.split(".")[0]

    with open(file_path, 'r') as file:
        html = file.read(-1)
    tree = tree_from_html(html)

    builder = JsBuilder(name)
    builder.start_walk(tree[0])
    output = builder.get_ugly_str()

    outpath = path.join(output_dir, f'{name}.js')
    with open(outpath, 'w') as file:
        file.write(output)

def process_multiple(files, output_dir):
    for file in files:
        process(file, output_dir)

def main():
    conf_path = "./build.json"
    with open(conf_path,'r') as f:
        conf = json.load(f)
    process_multiple(conf["source_files"], conf["out_dir"])

if __name__ == '__main__':
    main()