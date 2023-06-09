import csv
import io
import json
import boto3
from datetime import date

#blame to: thomas harrison

class HoneycodeBackupBuilder:
    def __init__(self, workbookid, bucket):
        self.workbookid = workbookid
        self.bucketName = bucket
        self.honeycode_client = self.getClient()

    def doBackup(self, table_name):
        table = self.getTableByName(table_name)

        if table is None:
            raise ValueError(f"Table '{table_name}' not found in the workbook.")

        columnNames = []
        
        # Get all the columns in the table
        allColumnsInTable = self.honeycode_client.list_table_columns(
            workbookId=self.workbookid,
            tableId=table["tableId"]
        )

        # Convert column names to lowercase and replace spaces with underscores
        columnNames = [column["tableColumnName"].replace(' ', '_').lower() for column in allColumnsInTable["tableColumns"] if column["tableColumnName"] != "rowId"]

        rowRet = []
        nextToken2 = ""
        
        # Retrieve the rows of the table
        response = self.honeycode_client.list_table_rows(
            workbookId=self.workbookid,
            tableId=table["tableId"],
            maxResults=100
        )

        if "nextToken" in response:
            nextToken2 = response["nextToken"]

        # Process the rows
        for row in response["rows"]:
            rowRet.append(self.convertRowToDict(row, columnNames))
            
        # Handle pagination if there are more rows
        while nextToken2:
            response = self.honeycode_client.list_table_rows(
                workbookId=self.workbookid,
                tableId=table["tableId"],
                maxResults=100,
                nextToken=nextToken2
            )

            nextToken2 = ""

            if "nextToken" in response:
                nextToken2 = response["nextToken"]

            for row in response["rows"]:
                rowRet.append(self.convertRowToDict(row, columnNames))

        if len(rowRet) > 0:
            json_data = json.dumps(rowRet)
            
            session = boto3.session.Session()
            resource = session.resource("s3")

            todays_date = date.today()

            # Upload the data as a JSON file to the specified S3 bucket and key
            key = self.workbookid + "/" + table["tableName"] + "/" + table["tableName"] + ".json"
            resource.Object(self.bucketName, key).put(Body=json_data)
            
            # Upload the data as a JSON file with a timestamped key for backup purposes
            key = (
                self.workbookid + "/backup/" + table["tableName"] + "/"
                + str(todays_date.year) + str(todays_date.month) + str(todays_date.day)
                + "_" + table["tableName"] + "_data.json"
            )
            resource.Object(self.bucketName, key).put(Body=json_data)

    def convertRowToDict(self, row, columns):
        rowDict = {}

        # Convert a row to a dictionary with column names as keys
        for i, item in enumerate(row["cells"]):
         # Determine the field type and format of the cell value
            fieldtype = ""
            pformat = ""
            clean = ""

            if item.get("fieldtype"):
                fieldtype = item.get("fieldtype")

            if item.get("format"):
                pformat = item.get("format")

            if pformat == "ROWLINK":
                fieldtype = "formattedValue"
            elif pformat == "ROWSET":
                fieldtype = "rawValue"
            elif pformat == "CONTACT":
                fieldtype = "rawValue"
            elif pformat == "DATE":
                fieldtype = "formattedValue"
            elif pformat == "DATE_TIME":
                fieldtype = "formattedValue"
            else:
                fieldtype = "rawValue"

            if fieldtype == "formattedValues":
                rowDict[columns[i]] = str(item)
            elif item.get(fieldtype):
                clean = item.get(fieldtype).strip()

                if fieldtype == "rawValue" and clean.find("row:") > -1:
                    clean = clean.split("/")[1]

                clean = clean.replace("\n", "<br>")
                clean = clean.replace(",", "&#44;")
                clean = clean.replace("\"", "&quot;")

                rowDict[columns[i]] = None if clean == "<blank>" else clean
            else:
                rowDict[columns[i]] = None

        return rowDict

    def getTableByName(self, table_name):
        allTablesInWorkbook = self.honeycode_client.list_tables(workbookId=self.workbookid)
        for table in allTablesInWorkbook['tables']:
            if table['tableName'] == table_name:
                return table
        return None

    def getClient(self):
        honeycode_client = boto3.client('honeycode', region_name='us-west-2')
        return honeycode_client
        
def lambda_handler(event, context):
    workbook_id = event['workbookid']
    bucket_name = event['bucket']
    table_name = event['tablename']

    hcb = HoneycodeBackupBuilder(workbook_id, bucket_name)
    hcb.doBackup(table_name)

    return {
        'statusCode': 200,
        'body': 'Backed Up!'
    }


