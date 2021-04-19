import json
import jsonschema
from jsonschema import validate
from jsonschema import Draft7Validator
from jsonschema import exceptions
import os
import sys
from git import Repo
import pprint

# provide ABAP objects as list
# only schema for this objects are validated
object_type = ['clas', 'intf', 'nrob', 'chko', 'fugr', 'enho', 'enhs']


def get_all_files_from_repo():
    repo = Repo('./')
    git = repo.git
    return git.ls_tree('-r', '--name-only', 'HEAD').split('\n')


def gather_json_schemata( objects, object_type ):
    json_schemata = []
    # find json schema of type <ABAB_object>.json
    for object_with_path in objects:
        obj = os.path.basename(object_with_path)
        if obj.startswith(tuple(object_type)) and obj.endswith('json'):
            json_schemata.append(object_with_path)
    return json_schemata


def validate_json_schemata( json_schemata ):
    print(f"::group::Validate JSON schemata")
    for el in json_schemata:
        with open(os.path.join(el), 'r') as schema_file:
            schema = json.loads(schema_file.read())
            Draft7Validator.check_schema(schema)



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


def validate_json( schema, examples):
    with open(schema, 'r') as schema_class:
        schema_clas = json.loads(schema_class.read())
    for example in examples:
        with open(example, 'r') as file_class:
            json_clas = json.loads(file_class.read())
            validate( json_clas, schema_clas )


def validate_json_and_example( json_schemata, repo_obj ):
    dict_as_list = get_schema_example_items( json_schemata, repo_obj)
    print(f"::group::Validate JSON instances")
    for schema in dict_as_list:
        validate_json( schema[0], schema[1])
    print(f"::endgroup::")


repo_obj = get_all_files_from_repo()
json_schemata = gather_json_schemata( repo_obj, object_type )

#validate_json_schemata( json_schemata )
validate_json_and_example( json_schemata, repo_obj)
