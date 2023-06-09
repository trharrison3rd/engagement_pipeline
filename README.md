# engagement_pipeline
This is a pipeline dedicated to supporting engagement entries and metrics


1. *Support Teams import data via csv upload into Honeycode Workbook “Workbook”*
2. *Amazon EventBridge Invokes Lambda function daily @1200 UTC*
3. *Lambda is triggered by EventBridge and invokes the following APIs:*
    1. ‘list_table_columns’: Retrieves columns of tables in Honeycode
    2. ‘list_table_rows’: Fetches rows of tables in Honeycode
    3. ‘resource.Object().put’: Stores the data as JSON files in Amazon S3
    4. EventBridge passes the following variables:

{
  "workbookid": "workbook-id",
  "bucket": "honeycodeexport",
  "tablename": "input-data"
}

1. *Lambda deposits data to S3 bucket designated for Vendor Engagement using the variables defined in EventBridge*

3. *Cradle Job uses S3 file as input*
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

