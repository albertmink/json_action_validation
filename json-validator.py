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
    print("Validate JSON schemata")
    for el in json_schemata:
        with open(os.path.join(el), 'r') as schema_file:
            try:
                schema = json.loads(schema_file.read())
            except json.JSONDecodeError as ex:
                print("[error] Decoding JSON has failed for " + el)
                print(ex.msg+" at line "+str(ex.lineno))
            else:
                v = Draft7Validator(schema)
                for error in Draft7Validator.iter_errors(schema):
                    print(error)
                try:
                    Draft7Validator.check_schema(schema)
                    print(el.ljust(31)+ "is valid")
                except jsonschema.exceptions.SchemaError as error_ex:
                    print("Bad JSON schema "+el)


def get_schema_example_items( json_schemata, repo_obj ):
    # build dict with key: json schema and value: json example
    dict_json = {}
    for schema in json_schemata:
        filename = os.path.basename(schema)
        dict_json[schema] = list(filter(lambda el: el.endswith(filename) and os.path.basename(el) != filename, repo_obj))
    print("Found matches of JSON schema and instances")
    pprint.pprint(dict_json)
    return dict_json.items()


def validate_json( schema, examples):
    nb_errors = 0
    with open(schema, 'r') as schema_class:
        schema_clas = json.loads(schema_class.read())
    for example in examples:
        with open(example, 'r') as file_class:
            try:
                json_clas = json.loads(file_class.read())
            except json.JSONDecodeError as ex:
                print(f"::error file={example} ::{ex.msg}")
                nb_errors += 1
            else:
                try:
                    validate( json_clas, schema_clas )
                except jsonschema.exceptions.ValidationError as exVal:
                    nb_errors += 1
                    print(f"::error file={example},line=1,col=1::{exVal.message}")
                    print(f"::error file={os.path.basename(example)},line=1,col=1::{exVal.message}")
                else:
                    print(os.path.basename(example).ljust(31) + " valid instance of schema " + os.path.basename(schema))

    if nb_errors > 0:
        sys.exit(1)


def validate_json_and_example( json_schemata, repo_obj ):
    dict_as_list = get_schema_example_items( json_schemata, repo_obj)
    print("\nValidate JSON instances")
    for schema in dict_as_list:
        validate_json( schema[0], schema[1])


repo_obj = get_all_files_from_repo()
json_schemata = gather_json_schemata( repo_obj, object_type )

#validate_json_schemata( json_schemata )
validate_json_and_example( json_schemata, repo_obj)
sys.exit(0)
