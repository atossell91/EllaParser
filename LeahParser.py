from os import path
import json
from HtmlToTree import HtmlNode, HtmlToTree

class ParseData:
    def __init__(self):
        self.js = None
        self.css_links = []
        self.elem_refs = []
    
    def __add__(self, other):
        output = ParseData()
        output.html = self.html + other.html
        output.css_links = self.css_links.extend(other.css_links)
        output.elem_refs = self.elem_refs.extend(other.elem_refs)
        return output

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
        self.elem_refs = []
        self.css_links = []

    def is_id_attribute(self, name, value):
        return name == self.id_tag_name and value[0:len(self.id_tag_prefix)] == self.id_tag_prefix

    def apply_attributes(self, elem_index, attributes):

        ## Should this be extracting the reference keys here? Seems a bit weird...
        for attribute in attributes:
            name = attribute[0]
            value = attribute[1]

            if self.is_id_attribute(name, value):
                key = value[len(self.id_tag_prefix):]
                self.elem_refs.append(key)
                statement = f'{self.map_name}.set("{key}",{self.elems_arr_name}[{elem_index}]);'
                self.statements.append(statement)
            else:
                if not value:
                    statement = f'{self.elems_arr_name}[{elem_index}].{name}=true;'
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

    ## Should the walk functions directly return the reference keys? A different pattern should be used
    def start_walk(self, tree): 
        self.create_element(tree.tag_name)
        self.apply_attributes(self.index_counter.get_current_num(), tree.attributes)
        for child in tree.children:
            self.walk(child, 0)

    def walk(self, tree, parent_index):
        if tree.type == "text":
            self.create_text_element(tree.text)
            self.index_counter.increment_ticker()
            self.append_element(parent_index, self.index_counter.get_current_num())
        else:
            self.create_element(tree.tag_name)
            self.index_counter.increment_ticker()
            current_level = self.index_counter.get_current_num()
            self.apply_attributes(self.index_counter.get_current_num(), tree.attributes)
            self.append_element(parent_index, self.index_counter.get_current_num())

            for child in tree.children:
                self.walk(child, current_level)

    def get_pretty_str(self):
        ## TODO: Add indices to createElements in pretty mode
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

def process_html(html, comp_name):
    tree = tree_from_html(html)

    builder = JsBuilder(comp_name)

    # find any css links
    css_links = []
    start_index = 0
    if tree[start_index].tag_name == 'head':
        head_elem = tree[start_index]
        for child in head_elem.children:
            if child.tag_name == 'link':
                for attribute in child.attributes:
                    if attribute[0] == 'href':
                        css_links.append(attribute[1])
        
        start_index = start_index+1

    builder.start_walk(tree[start_index])

    parseRes = ParseData()
    parseRes.js = builder.get_ugly_str()
    #output = builder.get_pretty_str()
    parseRes.css_links = css_links
    parseRes.elem_refs = builder.elem_refs

    return parseRes

def main():
    html = '<head>    <link rel="stylesheet" href="./kira.css"/></head><div class="kiraView">    <div>        <button data-name="id-clickyButton">Clicky</button>    </div>    <input type="text" data-name="id-happyText"/></div>'
    res = process_html(html, "Kira")
    print(res.js)
    print(res.elem_refs)

if __name__ == '__main__':
    main()