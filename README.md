# Engagement Metrics Pipeline
This is a pipeline dedicated to supporting engagement entries and metrics

# Workflow


1. Support Teams upload data via CSV into the Honeycode Workbook named "Workbook".
2. Amazon EventBridge triggers a Lambda function daily at 12:00 UTC.
3. The Lambda function invokes various APIs:

```
list_table_columns: Retrieves columns of tables in Honeycode.
list_table_rows: Fetches rows of tables in Honeycode.
resource.Object().put: Stores the data as JSON files in Amazon S3.
```

 4. EventBridge passes the following variables to the Lambda function:

```
{ 
"workbookid": "workbook-id",
"bucket": "honeycodeexport",
"tablename": "input-data" 
}
```
1. *Lambda deposits data to S3 bucket designated for Vendor Engagement using the variables defined in EventBridge*

3. *Glue uses S3 file as input*
    1. Link to Glue job (joblink)
 
3. *Glue Publishes to EDX Subject/Dataset ‘subject’, 'dataset’*
    1. Link to EDX Subject/Dataset (link to dataset)
    
4. *Glue is scheduled to Load ouput manifest into Redshift table*
    1. Database = dbname
    2. Schema = engagement
    3. records
    4. Link to Load job (link)
    
5. *Data can be consumed via QS or other analytical functions*


For Honeycode workbook access, request permissions via (link)

1. Please bear in mind, users come at a cost of $7 per and access will be approved based on business need to read/write the data in Honeycode.

