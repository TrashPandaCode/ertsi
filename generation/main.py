from treble_tsdk.tsdk import TSDK, TSDKCredentials
from treble_tsdk import display_data as dd
from treble_tsdk import treble
import random

def main():
    tsdk = TSDK(TSDKCredentials.from_file("./creds/tsdk.cred"))

    projects = tsdk.list_my_projects()
    dd.display(projects)

    project = tsdk.get_or_create_project("ertsi")

    desk = tsdk.geometry_component_library.query(group="desk")[0]

    edge_points_hexagon= [[0, 0], [0, 6], [4, 6], [4, 0]]
    room = treble.GeometryDefinitionGenerator.create_polygon_room(
        points_xy=edge_points_hexagon,
        height_z=3,
        join_wall_layers=False
    )

    room.clear_geometry_components()
    placement = treble.GeometryComponentPlacement(
        components=tsdk.geometry_component_library.query(group="desk"),
        preferred_count=3,
        rotation_settings=treble.ComponentAnglePool([0])
    )
    room.populate_with_geometry_components(
        components=[placement],
        selection_algorithm=treble.ComponentSelectionAlgorithm.random,
    )
    
    #room.plot()

    # this only needs to be done once
    # model = project.add_model("room1", room)
    model = project.get_model_by_name("room1")

    dd.display(project.get_models())

    all_materials = tsdk.material_library.get()
    database_materials = [material for material in all_materials if material["organizationId"] == None]
    layers = {
        "polygon_room_wall_0": "windows",
        "polygon_room_wall_1": "smooth painted concrete",
        "polygon_room_wall_2": "smooth painted concrete",
        "polygon_room_wall_3": "smooth painted concrete",
        "polygon_room_floor": "vinyl on concrete",
        "polygon_room_ceiling": "perforated panels",
        "Furniture/Desk": "wood",
    }
    material_assignment = []

    for layer in model.layer_names:
        if layer in layers:
            search_string = layers[layer]
            matches = [
                m for m in database_materials
                if search_string.lower() in m.name.lower()
            ]
            if matches:
                material_assignment.append(
                    treble.MaterialAssignment(layer, random.choice(matches))
                )

    # show the material assignment
    dd.display(material_assignment)















if __name__ == "__main__":
    main()
