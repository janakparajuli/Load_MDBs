import arcpy
import os

# Define the root directory where VDC folders are located
root_directory = r'E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan'

# Initialize ArcMap document
mxd = arcpy.mapping.MapDocument(r"E:\PROFESSION\GO\Chitawan_SO\BharatpurMetropolitan\Load_mdbs.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

def add_layer_to_map(df, mdb_path, dataset):
    """Add a dataset as a layer to the map document."""
    try:
        layer_path = os.path.join(mdb_path, dataset)
        layer_name = "{}_{}".format(os.path.basename(mdb_path).split('.')[0], dataset)
        # Create a feature layer from the dataset
        arcpy.MakeFeatureLayer_management(layer_path, layer_name)
        layer = arcpy.mapping.Layer(layer_name)
        arcpy.mapping.AddLayer(df, layer, "BOTTOM")
        print("Added {} from {}".format(dataset, mdb_path))
        return layer
    except Exception as e:
        print("Failed to add {} from {}: {}".format(dataset, mdb_path, str(e)))
        return None

def organize_layers_into_groups(df):
    """Organize layers into group layers based on VDC."""
    layers = arcpy.mapping.ListLayers(mxd, "", df)
    vdc_groups = {}

    for layer in layers:
        if not layer.isGroupLayer:
            vdc_name = layer.name.split('_')[0]
            if vdc_name not in vdc_groups:
                # Create a new group layer
                group_layer = arcpy.mapping.Layer()
                group_layer.name = vdc_name + "_Group"
                arcpy.mapping.AddLayer(df, group_layer, "BOTTOM")
                vdc_groups[vdc_name] = group_layer
            # Move the layer to the respective group layer
            arcpy.mapping.MoveLayer(vdc_groups[vdc_name], layer, "BOTTOM")

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

                        # List all datasets in the .mdb file
                        arcpy.env.workspace = mdb_path
                        datasets = arcpy.ListFeatureClasses()
                        for dataset in datasets:
                            if 'parcel' in dataset.lower() or 'construction' in dataset.lower():
                                add_layer_to_map(df, mdb_path, dataset)

# Organize added