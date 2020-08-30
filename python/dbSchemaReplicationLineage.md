# Schema Replication Lineage Script

## Purpose
provides the ability to link tables/columns in a database schema that are replicated to other schemas/databases & no scanner exists to automatcially document these relationships.  (e.g. sqoop, scripts/code, goldengate ...)

## Usage
Note:  usage has changed - no settings are hard coded, all can be provided via command-line arguments

`python dbSchemaReplicationLineage.py <options>

- `-lr` or `--leftresource` - name of the resource containing the schema on the left
- `-ls` or `--leftschema` - name of the schema on the left
- `-lt` or `leftschematype` - classtype of the left schema (e.g. 'com.infa.ldm.relational.Schema') - some scanners (e.g. hana db have different class types)

- `-rr` or `rightresource` - name of the resource containing the schema on the right
- `-rs` or `rightschema` - name of the schema on the left
- `-rt` or `rightschemaType` - classtype of the right schema
- `-rtp` or `--righttableprefix` - prefix to use for target tables (remove the prefix to match on left table)

catalog connection settings (can/should be passed via .env file)

- `-c` or `--edcurl` host:port for the catalog service.  e.g. 'http://napslxapp01:9085'
- `-v` or `--envfile` reference to an environment file with settings for catalog and user id/pwd (encoded)'
- `-a` pr `--auth` - user id/password, encoded - see `encodeUser.py` or `setupConnection.py` (but just use a .env file)


csv file output settings

- `-pfx` or `--csvprefix` - prefix for the generated csv file - e.g. "schemaLineage"
- `-out` or `--outDir` - folder to write the csv file, default/example "out"

## Lineage File Generated
the file generated uses the direct lineage format, supported in EDC v10.2.1+ and available for 10.2.0 via patch, using object id's and specific relationships vs connection assignment.

when configuring the CustomLineage resource - you do not need to check "Auto Assign Connections" in the Metadata Load Settings tab

## Example

A table `OT.EMPLOYEES` exists in the resource named `ot_oracle`
A table `landing.employees` exists in the resource named `landing_hive`


after running the script - the following lineage file was generated `schemaLineage_ot_landing.csv`:-

Note:  there is need for From Connection or To Connection

actual csv generated

```
Association,From Connection,To Connection,From Object,To Object
core.DataSourceDataFlow,,,ot_oracle://informatica/OT,landing_hive://Hive Metastore/landing
core.DataSetDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES,landing_hive://Hive Metastore/landing/employees
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/LAST_NAME,landing_hive://Hive Metastore/landing/employees/last_name
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/JOB_TITLE,landing_hive://Hive Metastore/landing/employees/job_title
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/MANAGER_ID,landing_hive://Hive Metastore/landing/employees/manager_id
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/FIRST_NAME,landing_hive://Hive Metastore/landing/employees/first_name
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/PHONE,landing_hive://Hive Metastore/landing/employees/phone
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/EMAIL,landing_hive://Hive Metastore/landing/employees/email
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/HIRE_DATE,landing_hive://Hive Metastore/landing/employees/hire_date
core.DirectionalDataFlow,,,ot_oracle://informatica/OT/EMPLOYEES/EMPLOYEE_ID,landing_hive://Hive Metastore/landing/employees/employee_id

```

Table format

Association|From Connection|To Connection|From Object|To Object
---|---|---|---|---
core.DataSourceDataFlow|||ot_oracle://informatica/OT|landing_hive://Hive Metastore/landing
core.DataSetDataFlow|||ot_oracle://informatica/OT/EMPLOYEES|landing_hive://Hive Metastore/landing/employees
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/LAST_NAME|landing_hive://Hive Metastore/landing/employees/last_name
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/JOB_TITLE|landing_hive://Hive Metastore/landing/employees/job_title
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/MANAGER_ID|landing_hive://Hive Metastore/landing/employees/manager_id
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/FIRST_NAME|landing_hive://Hive Metastore/landing/employees/first_name
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/PHONE|landing_hive://Hive Metastore/landing/employees/phone
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/EMAIL|landing_hive://Hive Metastore/landing/employees/email
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/HIRE_DATE|landing_hive://Hive Metastore/landing/employees/hire_date
core.DirectionalDataFlow|||ot_oracle://informatica/OT/EMPLOYEES/EMPLOYEE_ID|landing_hive://Hive Metastore/landing/employees/employee_id


Script Output (console) - shortened

```
dbSchemaReplicationLineage:start
Catalog=http://napslxapp01:9085
left:  resource=ot_oracle
left:    schema=OT
right: resource=landing_hive
right:   schema=landing
initializing file: out/schemaLineage_ot_landing.csv
get left schema: name=OT resource=ot_oracle type=com.infa.ldm.relational.Schema
	get_schema_objects for:OT resource=ot_oracle
	query=core.resourceName:ot_oracle and core.classType:com.infa.ldm.relational.Schema and core.name_lc_exact:OT
	objects returned: 1
	found schema: OT id=ot_oracle://informatica/OT
	GET child rels for schema: http://napslxapp01:9085/access/2/catalog/data/relationships parms={'seed': 'ot_oracle://informatica/OT', 'association': 'core.ParentChild', 'depth': '2', 'direction': 'OUT', 'includeAttribute': {'core.name', 'core.classType'}, 'includeTerms': 'false', 'removeDuplicateAggregateLinks': 'false'}
	lineage resp=200
	getSchema: returning 54 columns, in 12 tables
get left schema: name=landing resource=landing_hive type=com.infa.ldm.relational.Schema
	get_schema_objects for:landing resource=landing_hive
	query=core.resourceName:landing_hive and core.classType:com.infa.ldm.relational.Schema and core.name_lc_exact:landing
	objects returned: 1
	found schema: landing id=landing_hive://Hive Metastore/landing
	GET child rels for schema: http://napslxapp01:9085/access/2/catalog/data/relationships parms={'seed': 'landing_hive://Hive Metastore/landing', 'association': 'core.ParentChild', 'depth': '2', 'direction': 'OUT', 'includeAttribute': {'core.name', 'core.classType'}, 'includeTerms': 'false', 'removeDuplicateAggregateLinks': 'false'}
	lineage resp=200
	getSchema: returning 26 columns, in 3 tables

processing: 66 objects (left side)
	 no match on right side for key=orders
	 ...
	 no match on right side for key=orders.customer_id
	 no match on right side for key=orders.status
	 no match on right side for key=orders.salesman_id
	 no match on right side for key=orders.order_id
	 no match on right side for key=orders.order_date
	 ...
dbSchemaLineageGen:finished. 9 links created, 57 missing (found in left, no match on right)
```

Note:  the orders table was not replicated - that caused the 'no match on right side for ...' messages
