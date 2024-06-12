import arcpy
import os

# Define the root directory where VDC folders are located
root_directory = r'path_to_MDBs\Load_MDBs'

# Initialize ArcMap document
mxd = arcpy.mapping.MapDocument(r"path_to_mxd\Load_mdbs.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

def add_layer_to_map(df, mdb_path, dataset, vdc_name, ward_name):
    """Add a dataset as a layer to the map document."""
    try:
        layer_path = os.path.join(mdb_path, dataset)
        if arcpy.Exists(layer_path):
            layer_name = "{}_{}_{}_{}".format(vdc_name, ward_name, os.path.basename(mdb_path).split('.')[0], dataset.split('.')[0])
            layer = arcpy.mapping.Layer(layer_path)
            layer.name = layer_name  # Set the layer name
            arcpy.mapping.AddLayer(df, layer, "BOTTOM")
            print("Added {} from {}".format(layer_name, mdb_path))
            return layer
        else:
            print("Dataset {} does not exist in {}".format(dataset, mdb_path))
            return None
    except Exception as e:
        print("Failed to add {} from {}: {}".format(dataset, mdb_path, str(e)))
        return None

# Traverse the directory to find .mdb files and add them to the map
for vdc_folder in os.listdir(root_directory):
    vdc_path = os.path.join(root_directory, vdc_folder)
    if os.path.isdir(vdc_path):
        for ward_folder in os.listdir(vdc_path):
            ward_path = os.path.join(vdc_path, ward_folder)
            if os.path.isdir(ward_path):
                for file in os.listdir(ward_path):
                    if file.endswith('.mdb'):
                        mdb_path = os.path.join(ward_path, file)
                        vdc_name = vdc_folder
                        ward_name = ward_folder

                        # List all datasets in the .mdb file
                        arcpy.env.workspace = mdb_path
                        datasets = arcpy.ListFeatureClasses()
                        if datasets:
                            for dataset in datasets:
                                if 'parcel' in dataset.lower() or 'construction' in dataset.lower():
                                    add_layer_to_map(df, mdb_path, dataset, vdc_name, ward_name)
                        else:
                            print("No datasets found in {}".format(mdb_path))

# Save the MXD document if needed
mxd.saveACopy(r'path_to_mxd\Load_mdbs_saved.mxd')

print("Process Completed")
