import configparser
import os
from dataclasses import dataclass
import io
import StreamReplacer

CONFIG_NAME = "paths.ini"
ROOT_INDICATOR = '{{root}}'

DIRECTORY_SECTION_NAME = 'Directories'

class FileItem:

    def __init__(self, data_path, complete_path):
        self.DataPath = data_path
        self.CompletePath = complete_path

class FilePaths:
    @staticmethod
    def get_default_paths():
        paths = FilePaths()
        paths.add_path('Root', '.')
        paths.add_path('WebRoot', '{{root}}/web')
        paths.add_path('LocalRoot', '{{root}}/local')
        paths.add_path('CompiledViews', '{{webroot}}/compiled-views')
        paths.add_path('Models', '{{webroot}}/models')
        paths.add_path('Boilerplate', '{{webroot}}/indexjs')
        paths.add_path('HtmlViews', '{{localroot}}/html-views')
    
        return paths

    def __init__(self):
        self.paths = {}

    def add_path(self, label, data_path):
        complete = self.complete_path(data_path)
        self.paths[label] = FileItem(data_path, complete)

    def handle_label(self, label, args):
        if label in self.paths:
            return self.paths[label].CompletePath.encode('utf-8')
        else:
            return None

    def complete_path(self, datapath):
        in_text = io.BytesIO(datapath.encode('UTF-8'))
        out_text = io.BytesIO()
        StreamReplacer.replace_text(in_text, out_text, self.handle_label)
        path = out_text.getvalue().decode('utf-8')
        return path

    def __iter__(self):
        return self.paths.__iter__()

    def __next__(self):
        return self.paths.__next__()

    def __getattr__(self, name):
        if name in self.paths:
            return self.paths[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __getitem__(self, key):
        return self.paths[key]

def generate_ini(root_dir, paths = None):
    if not paths:
        paths = FilePaths.get_default_paths()

    ini = configparser.ConfigParser()

    ini.add_section(DIRECTORY_SECTION_NAME)
    section = ini[DIRECTORY_SECTION_NAME]

    for item in paths:
        section[item] = paths[item].DataPath

    output_path = os.path.join(root_dir, CONFIG_NAME)
    with open(output_path, 'w') as file:
        ini.write(file)

def create_path(path_in_config, root_path):
    return path_in_config.replace(ROOT_INDICATOR, root_path)

def load_paths(config_path):
    full_path = config_path
    paths = FilePaths()

    parser = configparser.ConfigParser()
    parser.read(full_path)

    section = parser[DIRECTORY_SECTION_NAME]

    for item in section:
        paths.add_path(item, section[item])
    
    return paths

def make_directory_tree(dir_path):
    parent, current = os.path.split(dir_path)

    if dir_path is None or parent =="":
        return

    if not os.path.isdir(parent):
        make_directory_tree(parent)
    
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

def test():
    generate_ini(".")
    paths = load_paths('./paths.ini')
    for item in paths:
        print(paths[item].DataPath)
        print(paths[item].CompletePath)
        print()

if __name__ == '__main__':
    test()
