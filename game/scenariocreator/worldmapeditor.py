import pygame
import pbge
import gears
from game.content.ghplots import campfeatures
from game.content import gharchitecture


def world_map_id(wm_blueprint):
    return "'WORLDMAP_{}'".format(wm_blueprint.uid)


def get_all_connections(all_blueprints, wmid):
    # Returns a dictionary of entrance_uid:blueprint items
    node_dict = dict()
    for blueprint in all_blueprints:
        if "entrance_world_map" in blueprint.raw_vars and wmid == blueprint.raw_vars["entrance_world_map"]:
            node_elements = blueprint.get_elements()
            print(node_elements)
            node_dict[node_elements["ENTRANCE"].uid] = blueprint
    return node_dict


class WorldMapEditor(pbge.widgets.Widget):
    def __init__(self, sc_editor, wm_blueprint):
        super().__init__(0, 0, 0, 0)
        self.sc_editor = sc_editor
        self.wm_blueprint = wm_blueprint
        self.finished = False

        # Step One: Build the world map that we will be editing.
        self.world_map = campfeatures.WorldMap(self.wm_blueprint.raw_vars["image_file"].strip('"'))

        # Step Two: Add nodes from each of the gates that link to this world map.
        self.node_dict = dict()
        self.entrance_to_node = dict()
        all_connections = get_all_connections(list(self.sc_editor.get_all_nodes()), world_map_id(wm_blueprint))
        for entrance_uid, blueprint in all_connections.items():
            # Check the errors now, so we can trust the values we're going to be sending to the node/edge constructors.
            if blueprint.get_errors():
                print("Blueprint {} has errors".format(blueprint))
                self.finished = True
            else:
                node_vars = blueprint.get_ultra_vars()
                node_elements = blueprint.get_elements(node_vars)
                node_data = node_vars["entrance_world_map_data"]
                mynode = campfeatures.WorldMapNode(destination=node_elements["LOCALE"], entrance=entrance_uid,
                                                   **node_data["node"])
                mynode.visible = True
                mynode.blueprint = blueprint
                self.node_dict[blueprint] = mynode
                self.world_map.add_node(mynode, *node_data["node"]["pos"])
                self.entrance_to_node[entrance_uid] = mynode

        for blueprint, node in self.node_dict.items():
            node_vars = blueprint.get_ultra_vars()
            for ed_dict in node_vars["entrance_world_map_data"]["edges"]:
                dest_uid = ed_dict["end_node"]
                end_node = self.entrance_to_node[dest_uid]
                self.world_map.connect_nodes(node, end_node, campfeatures.WorldMapEdge(
                    node, end_node, visible=True,
                    style=ed_dict.get("style", 1)
                ))

        self.world_map_viewer = campfeatures.WorldMapViewer(self.world_map)

    def render(self, flash=False):
        self.world_map_viewer.render(None, None)

    @classmethod
    def create_and_invoke(cls, redraw, sc_editor, wm_blueprint):
        # Create the UI. Run the UI. Clean up after you leave.
        myui = cls(sc_editor, wm_blueprint)
        sc_editor.active = False
        pbge.my_state.widgets.append(myui)
        pbge.my_state.view = redraw
        keepgoing = True
        while keepgoing and not myui.finished and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                redraw()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if pbge.my_state.is_key_for_action(ev, "exit"):
                    keepgoing = False

        pbge.my_state.widgets.remove(myui)
        sc_editor.active = True
