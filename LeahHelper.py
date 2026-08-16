import argparse
import os
import time
import json

import StreamReplacer
import PathLoader

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_SRC_PATH = os.path.join(SCRIPT_PATH, "FileSamples")

def copy_file(src_dir, src_name, target_dir, target_name = None, tag_lookup=None):
    if not target_name:
        target_name = src_name

    build_file_src_path = os.path.join(src_dir, src_name)
    build_file_dest_path = os.path.join(target_dir, target_name)
    StreamReplacer.stream_and_replace(build_file_src_path, build_file_dest_path, tag_lookup)

def setup_project(path):
    comps_dirpath = os.path.join(path, "comps")
    configs_dirpath = os.path.join(path, "configs")

    os.mkdir(comps_dirpath)
    os.mkdir(configs_dirpath)

    copy_file(FILE_SRC_PATH, "build.json", path)
    copy_file(FILE_SRC_PATH, "ModelFile.js", path)

def add_view(view_name, html_dir, model_dir, comp_dir):

    view_full_name = f'{view_name}View'
    model_name = f'{view_name}.js'

    html_name = f'{view_full_name}.html'
    compiled_name = f'{view_full_name}.js'

    html_view_path = os.path.join(html_dir, html_name)
    compiled_view_path = os.path.join(comp_dir, compiled_name)

    copy_file(FILE_SRC_PATH, "ModelFile.js", model_dir, compiled_name, {
        "viewName": view_full_name,
        "modelDir": model_dir,
        "modelName": view_name
    })

    copy_file(FILE_SRC_PATH, "ViewFile.html", html_dir, html_name, {
        "viewName": view_full_name
    })

def update_build_config(config_path, html_view_source, js_view_target):
    with open(config_path, 'r') as file:
        obj = json.load(file)
        
    obj["source_files"].append([html_view_source, js_view_target])

    with open(config_path, 'w') as file:       
        json.dump(obj, file, indent=4)

def scaffold_new(diri, app_name):
    ## Load or create the paths ini file
    ini_path = os.path.join(diri, PathLoader.CONFIG_NAME)

    if not os.path.isfile(ini_path):
        PathLoader.generate_ini(diri)
    
    paths = PathLoader.load_paths(ini_path)
    
    for label in paths:
        PathLoader.make_directory_tree(paths[label].CompletePath)

    ## Copy files to their appropriate diriectories
    app_js_filename = "app.js"
    app_class_name = "App"
    app_init_fname = "init.js"
    app_init_path = os.path.join(diri, app_init_fname)
    copy_file(FILE_SRC_PATH, "app.js", diri, app_js_filename, {"appName": app_class_name})
    copy_file(FILE_SRC_PATH, "init.js", diri, "init.js", {
        "appName": app_class_name,
        "appJsPath": os.path.join(diri, app_js_filename)
    })
    copy_file(FILE_SRC_PATH, "index.html", diri, "index.html",{
        "initFilePath": app_init_path
    })

def find_project_root(current_dir, max_hops = 5):
    attempted_dir = current_dir
    count = 0
    while attempted_dir != "" and count < max_hops:
        attempted_path = os.path.join(attempted_dir, PathLoader.CONFIG_NAME)
        if os.path.isfile(attempted_path):
            return attempted_dir
        attempted_dir, _ = os.path.split(attempted_dir)
        count = count + 1

    return None

def create_new_component(current_dir, component_name):
    project_root = find_project_root(current_dir)
    if not project_root:
        return
    paths = PathLoader.load_paths(os.path.join(project_root, PathLoader.CONFIG_NAME))

    view_name = f'{component_name}View'
    html_view_name = f'{view_name}.html'
    js_view_name = f'{view_name}.js'
    js_model_name = f'{component_name}.js'

    copy_file(FILE_SRC_PATH, "ViewFile.html", paths[PathLoader.HTML_VIEWS_LABEL], html_view_name, {
        "viewName": component_name
    })

    copy_file(FILE_SRC_PATH, 'ModelFile.js', paths[PathLoader.MODELS_LABEL], js_model_name, {
        "viewName": view_name,
        "viewPath": os.path.join(paths[PathLoader.COMPILED_VIEWS_LABEL], js_view_name)
    })

def main():
    scaffold_new(".", "leah")
    #create_new_component(".", "Sayu")

if __name__ == '__main__':
    main()