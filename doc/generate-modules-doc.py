

#!/usr/bin/env python3

import argparse
from jinja2 import Template, FileSystemLoader, Environment
import json
from os import listdir
from os.path import isfile, join
import subprocess

TEMPLATE_FILE = "MODULES.md.j2"

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--path", default="./library", help="The ansible module path.")
parser.add_argument("--destination", default="MODULES.md", help="The destination filename")

args = parser.parse_args()
path = args.path
destination = args.destination

def yesno(input):
    return str(input).lower().replace('true', 'yes').replace('false', 'no')

modules = map(lambda module_file: module_file.split('.')[0], listdir(path)) 

modules_doc = []

for module in filter(lambda module_file: module_file != 'qem_fragment', modules):
    result = subprocess.run(['ansible-doc', '--module-path', path, '--json', module], stdout=subprocess.PIPE)
    output = result.stdout
    module_json = json.loads(output)
    modules_doc.append(module_json[module])

loader = FileSystemLoader(searchpath="./doc")
templateEnvironment = Environment(loader=loader)
templateEnvironment.filters['yesno'] = yesno

template = templateEnvironment.get_template(TEMPLATE_FILE)
rendered = template.render(modules=modules_doc)
f = open(destination, "w")
f.write(rendered)
f.close()