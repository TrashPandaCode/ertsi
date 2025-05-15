from treble_tsdk.tsdk import TSDK, TSDKCredentials
from treble_tsdk import display_data as dd
from treble_tsdk import treble
import random
import json


def main():
    data = json.load(open("data.json"))

    tsdk = TSDK(TSDKCredentials.from_file("./creds/tsdk.cred"))

    projects = tsdk.list_my_projects()
    dd.display(projects)

    project = tsdk.get_or_create_project("ertsi")

    edge_points_hexagon = data["room_verts"]
    room = treble.GeometryDefinitionGenerator.create_polygon_room(
        points_xy=edge_points_hexagon, height_z=3, join_wall_layers=False
    )

    room.clear_geometry_components()
    placement = treble.GeometryComponentPlacement(
        components=tsdk.geometry_component_library.query(group="desk"),
        preferred_count=3,
        rotation_settings=treble.ComponentAnglePool([0]),
    )
    room.populate_with_geometry_components(
        components=[placement],
        selection_algorithm=treble.ComponentSelectionAlgorithm.random,
    )

    # room.plot()

    # this only needs to be done once
    # model = project.add_model("room1", room)
    model = project.get_model_by_name("room1")
    assert model, "Model not found in project"

    dd.display(project.get_models())

    all_materials = tsdk.material_library.get()
    database_materials = [
        material for material in all_materials if material["organizationId"] == None
    ]
    layers = {
        "polygon_room_wall_0": data["wall_0_material"],
        "polygon_room_wall_1": data["wall_1_material"],
        "polygon_room_wall_2": data["wall_2_material"],
        "polygon_room_wall_3": data["wall_3_material"],
        "polygon_room_floor": data["floor_material"],
        "polygon_room_ceiling": data["ceiling_material"],
        "Furniture/Desk": "wood",
    }
    material_assignment = []

    assert model.layer_names, "No layers found in model"
    for layer in model.layer_names:
        if layer in layers:
            search_string = layers[layer]
            matches = [
                m for m in database_materials if search_string.lower() in m.name.lower()
            ]
            if matches:
                material_assignment.append(
                    treble.MaterialAssignment(layer, random.choice(matches))
                )

    # show the material assignment
    dd.display(material_assignment)

    source = treble.Source.make_omni(
        position=treble.Point3d(0.25, 0.5, 1.5), label="source_1"
    )
    receiver = treble.Receiver.make_mono(
        position=treble.Point3d(1, 1, 1.2), label="receiver_1"
    )
    sim_def = treble.SimulationDefinition(
        name="Simulation_1",  # unique name of the simulation
        simulation_type=treble.SimulationType.ga,  # the type of simulation
        model=model,  # the model we created in an earlier step
        energy_decay_threshold=60,  # simulation termination criteria - the simulation stops running after -40 dB of energy decay
        receiver_list=[receiver],
        source_list=[source],
        material_assignment=material_assignment,
    )

    sim_def.plot()


if __name__ == "__main__":
    main()
