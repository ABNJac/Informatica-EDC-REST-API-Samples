Module metadata_utilities.load_json_metadata
============================================

Classes
-------

`ConvertJSONtoEDCLineage()`
:   Converts JSON file to a JSON payload that can be send to Informatica EDC using its APIs

    ### Class variables

    `code_version`
    :

    ### Methods

    `create_metafile(self, filename, attributes)`
    :   A metafile is created for Informatica EDC to scan. This way no real data is needed.

    `generate_file_structure(self)`
    :   Generate the metadata file for the data. The result is a file with only a header. No real data is needed.

    `main(self)`
    :

    `process_files(self)`
    :   Process files in the configued json directory (check config.json)
        For each file: Validate its schema and generate the metadata definition file or lineage file
            (depends on the meta_type of the file found)

    `process_lineage_request(self)`
    :

    `send_metadata(self)`
    :

    `send_metadata_to_metadata_lake(self)`
    :