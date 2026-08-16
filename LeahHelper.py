import argparse
import os
import time
import json

import StreamReplacer
import PathLoader
import LeahParser

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

def webify_path(path):
    return path.replace('{{webroot}}/', "./")

def scaffold_new(diri, app_name):
    ## Load or create the paths ini file
    ini_path = os.path.join(diri, PathLoader.CONFIG_NAME)

    if not os.path.isfile(ini_path):
        PathLoader.generate_ini(diri)
    
    paths = PathLoader.load_paths(ini_path)
    
    for label in paths:
        PathLoader.make_directory_tree(paths[label].CompletePath)

    ## Copy files to their appropriate diriectories
    index_filename = 'index.html'
    app_js_filename = "app.js"
    app_class_name = "App"
    app_init_fname = "init.js"
    copy_file(FILE_SRC_PATH, "app.js", paths.boilerplate.CompletePath, app_js_filename, {"appName": app_class_name})
    copy_file(FILE_SRC_PATH, "init.js", paths.boilerplate.CompletePath, app_init_fname, {
        "appName": app_class_name,
        "appJsPath": os.path.join('./', app_js_filename)
    })
    copy_file(FILE_SRC_PATH, index_filename, paths.webroot.CompletePath, index_filename,{
        "initFilePath": os.path.join(webify_path(paths.boilerplate.DataPath), app_init_fname)
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

    copy_file(FILE_SRC_PATH, "ViewFile.html", paths.htmlviews.CompletePath, html_view_name, {
        "viewName": component_name
    })

    copy_file(FILE_SRC_PATH, 'ModelFile.js', paths.models.CompletePath, js_model_name, {
        "viewName": view_name,
        "viewPath": os.path.join(paths.compiledviews.DataPath.replace('{{webroot}}', '..'), js_view_name)
    })

def main():
    top_parser = argparse.ArgumentParser("Leah")
    
    sub = top_parser.add_subparsers(dest='command_type')
    sub1 = sub.add_parser("new")
    sub1.add_argument("item_type", choices=['project', 'component'])
    sub1.add_argument("name")
    sub1.add_argument("-d", dest="directory", default='.')

    sub2 = sub.add_parser("generate")
    sub2.add_argument("generate_target", choices=['pathconfig'])

    sub3 = sub.add_parser("build")
    sub3.add_argument("-d", dest='directory', default='.')

    res = top_parser.parse_args()
    
    if res.command_type == 'generate':
        pass
    elif res.command_type == 'new':
        name = res.name
        directory = res.directory
        if res.item_type == 'component':
            create_new_component(directory, name)
        if res.item_type == 'project':
            scaffold_new(directory, name)
    elif res.command_type == 'build':
        directory = res.directory
        paths = PathLoader.load_paths(os.path.join(directory, PathLoader.CONFIG_NAME))
        files = os.listdir(paths.htmlviews.CompletePath)
        for file_path in files:
            _, fname = os.path.split(file_path)
            viewName = os.path.splitext(fname)[0:len('view')]
            with open(os.path.join(paths.htmlviews.CompletePath, file_path), 'r') as file:        
                html = file.read(-1)
            LeahParser.process_html(html, viewName)

if __name__ == '__main__':
    main()