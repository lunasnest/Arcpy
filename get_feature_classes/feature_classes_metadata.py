# -------------------------------------------------
# Title: feature_classes_metadata.py
# Author: Carlos Luna
# Date: 1/14/2026
# Purpose: The purpose of this python file is to go into a csv file that contains a list of ALL feature classes (title). Then traverse it and get some metadata (like summary, description) and then output a csv file 
# -------------------------------------------------

import pandas as pd
import arcpy
from arcpy import metadata as md
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Set the workspace environment (update this path to your geodatabase or folder)
#arcpy.env.workspace = r"[CHANGE_THIS]"



# Function to convert the metadata date
def convert_date_format(yyyymmdd_string):
  """
  Converts a date string from 'yyyymmdd' to 'mm/dd/yyyy' format.

  Args:
    yyyymmdd_string: The input date string in 'yyyymmdd' format.

  Returns:
    The date string in 'mm/dd/yyyy' format.
  """
  try:
    # Step 2: Parse the input string into a datetime object
    date_object = datetime.strptime(yyyymmdd_string, '%Y%m%d')

    # Step 3: Format the datetime object into the desired output string
    mm_dd_yyyy_string = date_object.strftime('%m/%d/%Y')

    return mm_dd_yyyy_string

  except ValueError as e:
    return f"Error: {e}. Please ensure the input is in 'yyyymmdd' format."


# Function that takes opens and reads the csv file containing the feature classes title, on a column called feature_classes
def get_feature_class_list(csv_file_path, column_name='feature_classes'):
    """
    Reads a single CSV file and returns a list of feature class names from a specific column.

    Args:
        csv_file_path (str): Path to the input CSV file.
        column_name (str): The name of the column containing feature classes.

    Returns:
        list: A list of feature class names.
    """
    try:
        df = pd.read_csv(csv_file_path, usecols=[column_name])
        # Convert the column data to a Python list
        feature_class_list = df[column_name].tolist()
        return feature_class_list
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        return []
    except ValueError:
        print(f"Error: Column '{column_name}' not found in the CSV file.")
        return []


# --- Main execution ---
if __name__ == "__main__":
    
    
    # -------------------------------------------------
    # SETUP VARIABLES
    # -------------------------------------------------
    
    # Define file paths and column name
    # input_csv = r'[CHANGE_THIS]\partial_feature_classes.csv'  # Partial feature classes to test code
    input_csv = r'[CHANGE_THIS]\all_feature_classes.csv'
    output_csv = r'[CHANGE_THIS]\ArcGIS\outputs\results.csv'
    feature_column_name = 'FEATURE_CLASS_NAME' # Ensure this matches your CSV column name

    # Store everything in a list of dictionaries
    rows = []

    print("Program has started...")
   
    # We will use this to Get the list of feature classes from the input CSV
    fc_list = []

    # Temp XML directory - I separated directory and file in case you want to save all the XML files. ArcGIS saves the metadata as an XML
    temp_xml_dir = r"[CHANGE_THIS]" # Directory path where XML file will be saved
    xmlfile = temp_xml_dir+r'\xml_output.xml'
    xml_file = ''


    # Set the workspace 
    arcpy.env.workspace = r"[CHANGE_THIS]" # Replace with your local geodatabase or project folder
    
    # Path to the existing .sde connection file in your project (This changes based on the user who is running it)
    # Ensure the path is fully qualified or relative to the script location
    sde_connection_file = r"[CHANGE_THIS]"
    
    # Create an ArcSDESQLExecute object to interact with the database
    egdb_conn = arcpy.ArcSDESQLExecute(sde_connection_file)
    

# --------------------BEGIN


    # --- Step 1: Check if the file exists on disk ---
    if arcpy.Exists(sde_connection_file):
        #print(f"Connection file found: {sde_connection_file}")
    
        # --- Step 2: Attempt to use the connection to verify validity ---
        try:
            # Set the workspace to the connection file
            arcpy.env.workspace = sde_connection_file
      
            # Get feature Classes from input excel
            #feature_classes = arcpy.ListFeatureClasses() # This function doesnt return all feature_classes, hence i wrote a different program, saved it into csv and using that instead
            
            fc_list = get_feature_class_list(input_csv, feature_column_name)
            fc_list.sort()
            print(f"Found {len(fc_list)} Feature Classes")    

            # --- Step 3: Traverse the list
            for fc in fc_list:
                #print(f"Feature class: {fc}")

                # Load metadata
                set_metadata = md.Metadata(fc)
     
                # Build XML file path, if you want to save all the XML files for each feature class do this, and comment the code after this
                #xml_file = os.path.join(
                #    temp_xml_dir,
                #    f"{os.path.basename(fc).replace('.', '_')}.xml"
                #)
                # Save metadata as XML
                #set_metadata.saveAsXML(xml_file)

                # If you dont care about saving each feature_class metadata and wanna just re-write into one XML file do this instead
                set_metadata.saveAsXML(xmlfile)
     
                # Parse XML
                tree = ET.parse(xmlfile)
                #root = tree.getroot()
                row = {
                     "Feature Set" : fc
                    , "create_date": "N/A" if tree.find("Esri/CreaDate") is None else convert_date_format(tree.find("Esri/CreaDate").text)
                    , "Summary": "N/A" if tree.find("idinfo/descript/purpose") == None else tree.find("idinfo/descript/purpose").text
                    , "Description" : "N/A" if tree.find("idinfo/descript/abstract") == None else tree.find("idinfo/descript/abstract").text
                    , "create_time" : "N/A" if tree.find("Esri/CreaTime") is None else tree.find("Esri/CreaTime").text
                    , "arcgis_format" : "N/A" if tree.find("Esri/ArcGISFormat") is None else tree.find("Esri/ArcGISFormat").text
                    , "sync_once" : "N/A" if tree.find("Esri/SyncOnce") is None else tree.find("Esri/SyncOnce").text
                    , "item_name" : "N/A" if tree.find("Esri/DataProperties/itemProps/itemName") is None else tree.find("Esri/DataProperties/itemProps/itemName").text
                    , "sync_date" : "N/A" if tree.find("Esri/SyncDate") is None else convert_date_format(tree.find("Esri/SyncDate").text)
                    , "sync_time" : "N/A" if tree.find("Esri/SyncTime") is None else tree.find("Esri/SyncTime").text
                    , "mod_date" : "N/A" if tree.find("Esri/ModDate") is None else convert_date_format(tree.find("Esri/ModDate").text)
                    , "mod_time" : "N/A" if tree.find("Esri/ModTime") is None else tree.find("Esri/ModTime").text
                    , "envir_desc" : "N/A" if tree.find("dataIdInfo/envirDesc") is None else tree.find("dataIdInfo/envirDesc").text
                    , "format_name" : "N/A" if tree.find("distInfo/distFormat/formatName") is None else tree.find("distInfo/distFormat/formatName").text
                    , "mdhrlvname" : "N/A" if tree.find("mdHrLvName") is None else tree.find("mdHrLvName").text
                    , "mdDateSt" : "N/A" if tree.find("mdDateSt") is None else convert_date_format(tree.find("mdDateSt").text)
                    , "enttypl" : "N/A" if tree.find("eainfo/detailed/enttyp/enttypl") is None else tree.find("eainfo/detailed/enttyp/enttypl").text
                    , "enttypt" : "N/A" if tree.find("eainfo/detailed/enttyp/enttypt") is None else tree.find("eainfo/detailed/enttyp/enttypt").text
                }
                #print(row)
                rows.append(row)
                    

            # This line is outside the for loop
            print("Finished building the dictionary")
            print("Now writing into csv...")
            #print(rows)

            df = pd.DataFrame(rows)
            df.to_csv(output_csv)
        
      
            print(f"\nSuccessfully saved results to {output_csv}")

            print("program end.")

        except arcpy.ExecuteError:
            # Catch specific ArcGIS errors (e.g., bad credentials, network issues)
            print("ArcPy ExecuteError: Could not connect to the database.")
            print(arcpy.GetMessages(2)) # Print geoprocessing error messages


    else:
        print(f"Connection file not found at: {sde_connection_file}")



#---------------------END


