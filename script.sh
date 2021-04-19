ajv compile --spec=draft2020 --strict=false -s clas/clas.json
ajv compile --strict=false -s clas/clas.json
ajv compile -s clas/clas.json
ajv validate --spec=draft2020 --strict=false -s clas/clas.json -d clas/examples/zcl_aff_example.clas.json
ajv validate --spec=draft2020 --strict=false -s clas/clas.json -d clas/examples/zcl_aff_example.bad.clas.json
