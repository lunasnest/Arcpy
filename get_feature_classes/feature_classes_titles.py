# -------------------------------------------------
# Title: feature_classes_titles.py
# Author: Carlos Luna
# Date: 1/14/2026
# Purpose: The purpose of this python file is to go into local oracle server [SERVER_NAME], run arcpy function(s) ListDataSets(), and ListFeatureClasses() to obtain all feature classes. Then save the result as a csv output oracle_sde_feature_classes.csv
# Just running the ListFeatureClasses() doesn't seem to add all of the feature classes.
# How to run this code: 
#       Simply create a new project in ArcGIS Pro, then Insert -> Connections -> Database -> New Database Connection: Set up your database connection to the database you wish to run this on. Then remember where that file is located b/c you will use the path/name.sde
#       Under insert go ahead and add New Notebook 
#       Please replace all cases of [CHANGE_THIS] with your local strings
# -------------------------------------------------


import arcpy
import csv
import os

 
# -------------------------------------------------
# SETUP VARIABLES
# -------------------------------------------------
 
# Path to your Oracle SDE connection file
# Example: C:\GIS\Connections\my_oracle_db.sde

# Set the workspace 
arcpy.env.workspace = r"[CHANGE_THIS]" # Replace with your local geodatabase or project folder
    
# Path to the existing .sde connection file in your project (This changes based on the user who is running it)
# Ensure the path is fully qualified or relative to the script location. Basically create an ArcPro project then use Connect to 
sde_connection_file = r"[CHANGE_THIS]"
   
# Create an ArcSDESQLExecute object to interact with the database
egdb_conn = arcpy.ArcSDESQLExecute(sde_connection_file)
    
 
# Output CSV
output_csv = r"[CHANGE_THIS]\oracle_sde_feature_classes.csv"
 
# -------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------
 
arcpy.env.workspace = sde_connection
arcpy.env.overwriteOutput = True
 
# -------------------------------------------------
# COLLECT FEATURE CLASSES
# -------------------------------------------------
 
results = []
 
# Get all feature datasets (empty list if none exist)
feature_datasets = arcpy.ListDatasets(feature_type="feature") or [""]
 
for dataset in feature_datasets:
 
    # Set workspace to either root or feature dataset
    if dataset:
        arcpy.env.workspace = os.path.join(sde_connection, dataset)
    else:
        arcpy.env.workspace = sde_connection
 
    # List feature classes in this workspace
    feature_classes = arcpy.ListFeatureClasses()
 
    for fc in feature_classes:
        desc = arcpy.Describe(fc)
 
        results.append({
            #"Owner": desc.owner,      
            "FeatureDataset": dataset if dataset else "ROOT",
            "FeatureClass": fc,
            "GeometryType": desc.shapeType,
            "SpatialReference": desc.spatialReference.name if desc.spatialReference else "Unknown",
            "IsVersioned": desc.isVersioned,
            "CatalogPath": desc.catalogPath
        })
 
# -------------------------------------------------
# WRITE RESULTS TO CSV
# -------------------------------------------------
 
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
 
with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        #"Owner",
        "FeatureDataset",
        "FeatureClass",
        "GeometryType",
        "SpatialReference",
        "IsVersioned",
        "CatalogPath"
    ]
 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
 
print(f"Feature class inventory written to: {output_csv}")
print(f"Total feature classes found: {len(results)}")


