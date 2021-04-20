import json
import jsonschema
from jsonschema import Draft7Validator
from jsonschema import exceptions
import os
import sys
from git import Repo
import pprint

# provide ABAP objects as list
# only schema for this objects are validated
object_type = ['clas', 'intf', 'nrob', 'chko', 'fugr', 'enho', 'enhs']
nb_errors = 0


def get_all_files_from_repo():
    repo = Repo('./')
    git = repo.git
    return git.ls_tree('-r', '--name-only', 'HEAD').split('\n')


def gather_json_schemata( objects ):
    json_schemata = []
    # find json schema of type <ABAB_object>.json
    for object_with_path in objects:
        obj = os.path.basename(object_with_path)
        if obj.startswith(tuple(object_type)) and obj.endswith('json'):
            json_schemata.append(object_with_path)
    return json_schemata


def get_schema_example_items( json_schemata, repo_obj ):
    # build dict with key: json schema and value: json example
    dict_json = {}
    for schema in json_schemata:
        filename = os.path.basename(schema)
        dict_json[schema] = list(filter(lambda el: el.endswith(filename) and os.path.basename(el) != filename, repo_obj))
    print(f"::group::Print schema/instance matches")
    pprint.pprint(dict_json)
    print(f"::endgroup::")
    return dict_json.items()

def decode_json( json_file ):
    global nb_errors
    with open(json_file, 'r') as schema_f:
        try:
            schema = json.loads(schema_f.read())
        except json.JSONDecodeError as ex:
            print(f"::error file={json_file},line=1,col=1::{ex.msg}")
            nb_errors += 1
        else:
            return schema

def validate_json( schema, examples):
    global nb_errors
    json_schema = decode_json( schema )
    for example in examples:
        json_instance = decode_json( example )
        try:
            Draft7Validator(json_schema).validate(json_instance)
        except jsonschema.exceptions.ValidationError as exVal:
            nb_errors += 1
            print(f"::error file={example},line=1,col=1::{exVal.message}")
        except jsonschema.exceptions.SchemaError as error_ex:
            nb_errors += 1
            print(f"::error file={example},line=1,col=1::{error_ex.message}")
        else:
            #print(f"::set-output name={os.path.basename(example).ljust(31)} valid instance of schema {os.path.basename(schema)}" )
            print(os.path.basename(example).ljust(31) + " valid instance of schema " + os.path.basename(schema))


def validate_json_and_example( json_schemata, repo_obj ):
    dict_as_list = get_schema_example_items( json_schemata, repo_obj)
    print(f"::group::Validate JSON")
    for schema in dict_as_list:
        validate_json( schema[0], schema[1])
    print(f"::endgroup::")


repo_obj = get_all_files_from_repo()
json_schemata = gather_json_schemata( repo_obj )

validate_json_and_example( json_schemata, repo_obj)
if nb_errors > 0:
    sys.exit(1)
