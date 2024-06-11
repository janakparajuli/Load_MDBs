import arcpy
import os

# Define the root directory where VDC folders are located
root_directory = r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan'

# Path to the group layer template
group_layer_template = r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\GroupLayerTemplate.lyr'

# Initialize ArcMap document
mxd = arcpy.mapping.MapDocument(r"E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\Load_mdbs.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

def add_layer_to_map(df, layer_path, layer_name):
    """Add a layer to the map document."""
    try:
        layer = arcpy.mapping.Layer(layer_path)
        arcpy.mapping.AddLayer(df, layer, "BOTTOM")
        print("Added {} to the map".format(layer_name))
    except Exception as e:
        print("Failed to add {}: {}".format(layer_name, str(e)))

def create_and_add_group_layer(df, group_layer_name):
    """Create and add a group layer to the map document."""
    try:
        group_layer = arcpy.mapping.Layer(group_layer_template)
        group_layer.name = group_layer_name
        arcpy.mapping.AddLayer(df, group_layer, "BOTTOM")
        return group_layer
    except Exception as e:
        print("Failed to create group layer {}: {}".format(group_layer_name, str(e)))
        return None

# Traverse the directory to find .mdb files and add them to the map
for vdc_folder in os.listdir(root_directory):
    vdc_path = os.path.join(root_directory, vdc_folder)
    if os.path.isdir(vdc_path):
        group_layer_name = vdc_folder + "_GroupLayer"
        group_layer = create_and_add_group_layer(df, group_layer_name)

        if group_layer:
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
                                    layer_path = os.path.join(mdb_path, dataset)
                                    add_layer_to_map(df, layer_path, dataset)
                                    # Move the added layer to the group layer
                                    layer = arcpy.mapping.ListLayers(mxd, dataset, df)[0]
                                    arcpy.mapping.MoveLayer(group_layer, layer, "TOP")

# Save the MXD document if needed
mxd.saveACopy(r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\Load_mdbs_saved.mxd')

print("Process Completed")
