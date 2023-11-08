import csv
import json

# Step 1: Read the TSV file and parse its contents
tsv_file = '../../metadata/customPSRI.tsv'
properties_file = "output.properties"

# Create dictionaries to store metadata block, dataset fields, and controlled vocabulary data
metadata_block = {}
dataset_fields = {}
controlled_vocabulary = {}

with open(tsv_file, mode='r', newline='', encoding='utf-8') as tsv:
    reader = csv.reader(tsv, delimiter='\t')
    section = None
    rows_datasetFields = 0
    rows_controlledVocabulary = 0
    for row in reader:
        if not row:
            continue
        if row[0].startswith("#"):
            section = row[0].strip("#").strip()
        else:
            if section == "metadataBlock":
                metadata_block["name"] = row[1]
                metadata_block["dataverseAlias"] = row[2]
                metadata_block["displayName"] = row[3]
            elif section == "datasetField":
                rows_datasetFields = rows_datasetFields + 1
                dataset_fields[rows_datasetFields] = {
                    "name": row[1],
                    "title": row[2],
                    "description": row[3],
                    "watermark": row[4],
                    "fieldType": row[5],
                    "displayOrder": row[6],
                    "displayFormat": row[7],
                    "advancedSearchField": row[8],
                    "allowControlledVocabulary": row[9],
                    "allowmultiples": row[10],
                    "facetable": row[11],
                    "displayoncreate": row[12],
                    "required": row[13],
                    "parent": row[14],
                    "metadatablock_id": row[15]
                }
            elif section == "controlledVocabulary":
                rows_controlledVocabulary = rows_controlledVocabulary + 1
                controlled_vocabulary [rows_controlledVocabulary] = {
                    "DatasetField": row[1],
                    "Value": row[2],
                    "identifier": row[3],
                    "displayOrder": row[4]
                }

# Create a dictionary to store the properties
properties = {}

# Add metadatablock.name and metadatablock.displayName
properties['metadatablock.name'] = metadata_block['name']
properties['metadatablock.displayName'] = metadata_block['displayName']

# Add metadatablock.displayFacet if displayName is not empty
if metadata_block['displayName']:
    properties['metadatablock.displayFacet'] = metadata_block['displayName']

# Generate the .properties file
with open('output.properties', 'w', encoding='utf-8') as prop_file:
    for key, value in properties.items():
        prop_file.write(f'{key}={value}\n')

    for item in dataset_fields:
        for entry in dataset_fields[item]:
            if entry == "title" or entry == "description" or entry == "watermark":
                prop_file.write(f'datasetfieldtype.{dataset_fields[item]["name"]}.{entry}={dataset_fields[item][entry]}\n')

    for item in controlled_vocabulary:
        for entry in controlled_vocabulary[item]:
            if entry == "Value":
                prop_file.write(f'datasetfieldtype.{controlled_vocabulary[item]["DatasetField"]}.{controlled_vocabulary[item][entry].lower()}={controlled_vocabulary[item][entry]}\n')

