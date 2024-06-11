import arcpy
import os

# Define the root directory where VDC folders are located
root_directory = r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan'

# Initialize ArcMap document
mxd = arcpy.mapping.MapDocument(r"E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\Load_mdbs.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

def add_layer_to_group(df, group_layer, mdb_path, dataset):
    """Add a dataset as a layer to the specified group layer."""
    try:
        layer_path = os.path.join(mdb_path, dataset)
        # Create a feature layer from the dataset
        arcpy.MakeFeatureLayer_management(layer_path, dataset)
        layer_obj = arcpy.mapping.Layer(dataset)
        arcpy.mapping.AddLayerToGroup(df, group_layer, layer_obj)
        print("Added {dataset} from {mdb_path} to {group_layer}".format(dataset=dataset, mdb_path=mdb_path, group_layer=group_layer.name))
    except Exception as e:
        print("Failed to add {dataset} from {mdb_path}: {error}".format(dataset=dataset, mdb_path=mdb_path, error=str(e)))

# Print all layers to debug
print("Listing all layers in the MXD:")
for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    print("Layer name: {}".format(lyr.name))
    if lyr.isGroupLayer:
        print("This is a group layer.")

# Find the existing group layer in the MXD
vdc_group_layer = None
for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    if lyr.isGroupLayer and lyr.name == "VDC_Group":
        vdc_group_layer = lyr
        break

if not vdc_group_layer:
    print("Error: Group layer 'VDC_Group' not found in the MXD.")
else:
    # Traverse the directory to find .mdb files
    for vdc_folder in os.listdir(root_directory):
        vdc_path = os.path.join(root_directory, vdc_folder)
        if os.path.isdir(vdc_path):
            # Create a new group layer for the VDC within the main group layer
            group_layer_name = vdc_folder + "_GroupLayer"
            group_layer = arcpy.mapping.Layer()
            group_layer.name = group_layer_name
            arcpy.mapping.AddLayerToGroup(df, vdc_group_layer, group_layer)
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            for ward_folder in os.listdir(vdc_path):
                ward_path = os.path.join(vdc_path, ward_folder)
                if os.path.isdir(ward_path):
                    for file in os.listdir(ward_path):
                        if file.endswith('.mdb'):
                            mdb_path = os.path.join(ward_path, file)

                            # List all datasets in the .mdb file
                            arcpy.env.workspace = mdb_path
                            datasets = arcpy.ListFeatureClasses()
                            for dataset in datasets:
                                if 'parcel' in dataset.lower() or 'construction' in dataset.lower():
                                    add_layer_to_group(df, group_layer, mdb_path, dataset)

    # Save the MXD document if needed
    mxd.saveACopy(r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\Load_mdbs_saved.mxd')

    print("Process Completed")
