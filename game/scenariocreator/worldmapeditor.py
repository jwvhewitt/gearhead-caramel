import pygame
import pbge
import gears
from game.content.ghplots import campfeatures
from game.content import gharchitecture
from . import statefinders


CLICK_WORLD_MAP_TILE_EVENT = pygame.event.custom_type()


def world_map_id(wm_blueprint):
    return "'WORLDMAP_{}'".format(wm_blueprint.uid)


def get_all_connections(all_blueprints, wmid):
    # Returns a dictionary of entrance_uid:blueprint items
    node_dict = dict()
    for blueprint in all_blueprints:
        if "entrance_world_map" in blueprint.raw_vars and wmid == blueprint.raw_vars["entrance_world_map"]:
            node_elements = blueprint.get_elements()
            node_dict[node_elements["ENTRANCE"].uid] = blueprint
    return node_dict


class CheckboxWidget(pbge.widgets.RowWidget):
    CHECK_FRAME = {True: 0, False: 1}
    def __init__(self, w, caption, is_checked, on_change, **kwargs):
        # on_change is a callback function that takes a bool value as its parameter.
        super().__init__(0, 0, w, 20, padding=5, **kwargs)
        self.state_indicator = pbge.widgets.ButtonWidget(0,0,20,20,pbge.image.Image("sys_checkbox.png", 20, 20),
                                                         frame=self.CHECK_FRAME[bool(is_checked)],
                                                         on_click=self._toggle_state)
        self.add_left(self.state_indicator)
        self.add_left(pbge.widgets.LabelWidget(0,0,w-25,0,caption, on_click=self._toggle_state))
        self.is_checked = is_checked
        self.on_change = on_change

    def _toggle_state(self, wid, ev):
        self.is_checked = not self.is_checked
        self.state_indicator.frame = self.CHECK_FRAME[bool(self.is_checked)]
        if self.on_change:
            self.on_change(self.is_checked)


class LegendWidget(pbge.widgets.RowWidget):
    def __init__(self, world_map_viewer: campfeatures.WorldMapViewer, map_node: campfeatures.WorldMapNode, show_on_frame, on_change, **kwargs):
        # on_change is a callback function that takes the new frame value as its parameter.
        super().__init__(0, 0, 64, 20, padding=0, **kwargs)
        mybuttons = pbge.image.Image("sys_tinyleftrightbuttons.png", 20, 20)
        self.add_left(pbge.widgets.ButtonWidget(0,0,20,20,mybuttons,0, data=-1, on_click=self._change_frame))
        self.add_right(pbge.widgets.ButtonWidget(0,0,20,20,mybuttons,1, data=1, on_click=self._change_frame))

        self.world_map_viewer = world_map_viewer
        self.map_node = map_node
        self.show_on_frame = show_on_frame

        self.on_change = on_change

    def render(self, flash=False):
        super().render(flash)
        mydest = self.get_rect()
        mydest.x += 22
        if self.show_on_frame:
            self.world_map_viewer.legend_sprites[self.map_node].render(mydest, self.map_node.on_frame)
        else:
            self.world_map_viewer.legend_sprites[self.map_node].render(mydest, self.map_node.off_frame)

    def _change_frame(self, wid, ev):
        if self.show_on_frame:
            cframe = self.map_node.on_frame
        else:
            cframe = self.map_node.off_frame
        cframe += wid.data
        if cframe < 0:
            cframe = self.world_map_viewer.legend_sprites[self.map_node].num_frames() - 1
        elif cframe >= self.world_map_viewer.legend_sprites[self.map_node].num_frames():
            cframe = 0
        if self.show_on_frame:
            self.map_node.on_frame = cframe
        else:
            self.map_node.off_frame = cframe
        if self.on_change:
            self.on_change(cframe)


class WMNodeEditorWidget(pbge.widgets.RowWidget):
    def __init__(self, editor, node: campfeatures.WorldMapNode):
        super().__init__(0, 0, 760, 30, padding=10, draw_border=True)
        self.editor = editor
        self.world_map = editor.world_map
        self.node = node
        self.wm_data = node.wm_data
        self.add_left(pbge.widgets.LabelWidget(0,0,200,20,str(node), on_click=self._set_active_waypoint_uid, font=pbge.BIGFONT))

        my_image_menu = pbge.widgets.DropdownWidget(0, 0, 180, 20, on_select=self._set_image)
        for image_name in self.editor.legend_image_list:
            my_image_menu.add_item(image_name, image_name)
        my_image_menu.menu.set_item_by_value(node.image_file)
        self.add_left(my_image_menu)

        self.add_left(CheckboxWidget(70, "Visible", self.wm_data["node"].get("visible", False), self._change_visibility))
        self.add_left(CheckboxWidget(105, "Discoverable", self.wm_data["node"].get("discoverable", True), self._change_discoverability))

        self.frames_locked = True

        self.add_left(LegendWidget(self.editor.world_map_viewer, node, True, self._change_on_frame))
        self.lock_button = pbge.widgets.ButtonWidget(
            0,0,20,20, pbge.image.Image("sys_lockicon.png", 20, 20), on_click=self._toggle_lock
        )
        self.add_left(self.lock_button)
        self.add_left(LegendWidget(self.editor.world_map_viewer, node, False, self._change_off_frame))

    def _toggle_lock(self, *args):
        self.frames_locked = not self.frames_locked
        self.lock_button.frame = 1 - self.lock_button.frame

    def _change_on_frame(self, new_value):
        self.wm_data["node"]["on_frame"] = new_value
        if self.frames_locked:
            num_frames = self.editor.world_map_viewer.legend_sprites[self.node].num_frames()
            self.node.off_frame = (new_value + num_frames//2) % num_frames
            self.wm_data["node"]["off_frame"] = self.node.off_frame

    def _change_off_frame(self, new_value):
        self.wm_data["node"]["off_frame"] = new_value
        if self.frames_locked:
            num_frames = self.editor.world_map_viewer.legend_sprites[self.node].num_frames()
            self.node.on_frame = (new_value + num_frames//2) % num_frames
            self.wm_data["node"]["on_frame"] = self.node.on_frame

    def _change_visibility(self, new_value):
        self.wm_data["node"]["visible"] = new_value

    def _change_discoverability(self, new_value):
        self.wm_data["node"]["discoverable"] = new_value

    def _set_active_waypoint_uid(self, *args):
        self.editor.active_entrance_uid = self.node.entrance
        self.editor.active_edge = None

    def _set_image(self, result):
        if result != self.node.image_file:
            self.node.image_file = result
            self.wm_data["node"]["image_file"] = result
            self.editor.world_map_viewer.refresh_node_images()

    def render(self, flash=False):
        if self.editor.active_entrance_uid == self.node.entrance:
            self.border = pbge.widgets.widget_border_on
        else:
            self.border = pbge.widgets.widget_border_off
        super().render(flash)

    def _builtin_responder(self, ev):
        if self.editor.active_entrance_uid == self.node.entrance and ev.type == CLICK_WORLD_MAP_TILE_EVENT:
            self.wm_data["node"]["pos"] = ev.pos
            self.world_map.move_node(self.node, ev.pos)


class NodesEditor(pbge.widgets.Widget):
    def __init__(self, editor):
        super().__init__(0, 0, 0, 0)
        up_arrow = pbge.widgets.ButtonWidget(197, 122, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                             on_frame=0, off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(197, 280, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                               on_frame=2, off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(-380, 151, 760, 117, up_arrow, down_arrow, padding=19)
        self.children.append(up_arrow)
        self.children.append(down_arrow)
        self.children.append(self.scroll_column)

        self.editor = editor

        for node in editor.world_map.nodes:
            self.scroll_column.add_interior(WMNodeEditorWidget(editor, node))


class WMEdgeEditorWidget(pbge.widgets.RowWidget):
    def __init__(self, editor, edge: campfeatures.WorldMapEdge):
        super().__init__(0, 0, 760, 20, padding=10, draw_border=True)
        self.editor = editor
        self.world_map = editor.world_map
        self.edge = edge
        self.wm_data = edge.start_node.wm_data
        self.edge_data = None
        for edgedat in self.wm_data["edges"]:
            if edgedat.get("end_node") == self.edge.end_node.entrance:
                self.edge_data = edgedat
        if not self.edge_data:
            print("Oops...")
        self.add_left(pbge.widgets.LabelWidget(0,0,300,20,"{} to {}".format(edge.start_node, edge.end_node),
                                               on_click=self._set_active_edge))
        self.add_left(CheckboxWidget(70, "Visible", self.edge_data.get("visible", False), self._change_visibility))
        self.add_left(CheckboxWidget(105, "Discoverable", self.edge_data.get("discoverable", True), self._change_discoverability))
        self.add_left(pbge.widgets.LabelWidget(0,0,80,20,"Delete Edge", on_click=self._delete_edge))

    def _delete_edge(self, *args):
        self.wm_data["edges"].remove(self.edge_data)
        self.world_map.edges.remove(self.edge)
        self.editor.edges_editor.scroll_column.remove(self)

    def _set_active_edge(self, *args):
        self.editor.active_entrance_uid = None
        self.editor.active_edge = self.edge

    def _change_visibility(self, new_value):
        self.edge_data["visible"] = new_value

    def _change_discoverability(self, new_value):
        self.edge_data["discoverable"] = new_value

    def render(self, flash=False):
        if self.editor.active_edge == self.edge:
            self.border = pbge.widgets.widget_border_on
        else:
            self.border = pbge.widgets.widget_border_off
        super().render(flash)


class EdgesEditor(pbge.widgets.Widget):
    def __init__(self, editor):
        super().__init__(0, 0, 0, 0)
        up_arrow = pbge.widgets.ButtonWidget(197, 122, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                             on_frame=0, off_frame=1)
        down_arrow = pbge.widgets.ButtonWidget(197, 280, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16),
                                               on_frame=2, off_frame=3)
        self.scroll_column = pbge.widgets.ScrollColumnWidget(-380, 151, 760, 117, up_arrow, down_arrow, padding=19)
        self.children.append(up_arrow)
        self.children.append(down_arrow)
        self.children.append(self.scroll_column)

        self.editor = editor

        for edge in editor.world_map.edges:
            self.scroll_column.add_interior(WMEdgeEditorWidget(editor, edge))

        self.adding_edge = False
        self.start_node = None
        self.end_node = None
        self.add_edge_button = pbge.widgets.LabelWidget(
            -150, 120, 90, 16, "Add Edge", draw_border=True, border=pbge.widgets.widget_border_off, justify=0,
            on_click=self._add_edge, tooltip="Activate this button, then click two nodes on the map to make an edge."
        )
        self.children.append(self.add_edge_button)

    def _add_edge(self, *args):
        if self.adding_edge:
            self.adding_edge = False
            self.start_node = None
            self.end_node = None
            self.add_edge_button.border = pbge.widgets.widget_border_off
        else:
            self.adding_edge = True
            self.start_node = None
            self.end_node = None
            self.add_edge_button.border = pbge.widgets.widget_border_on

    def _builtin_responder(self, ev):
        if self.adding_edge and ev.type == CLICK_WORLD_MAP_TILE_EVENT:
            mynode = self.editor.world_map.get_node_at_pos(ev.pos)
            if mynode:
                if not self.start_node:
                    self.start_node = mynode
                    self.editor.active_entrance_uid = mynode.entrance
                elif mynode != self.start_node:
                    if not any([(edge.connects_to_node(self.start_node) and edge.connects_to_node(mynode)) for edge in self.editor.world_map.edges]):
                        my_edge = campfeatures.WorldMapEdge(self.start_node, mynode, visible=True)
                        self.editor.world_map.connect_nodes(self.start_node, mynode, my_edge)
                        self.start_node.wm_data["edges"].append({"end_node": mynode.entrance})
                        self.scroll_column.add_interior(WMEdgeEditorWidget(self.editor, my_edge))
                        self.start_node = None
                    else:
                        pbge.BasicNotification("A connection between {} and {} already exists.".format(self.start_node, mynode), count=150)
                else:
                    pbge.BasicNotification("You cannot connect a node to itself.", count=150)



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
            myerrors = blueprint.get_errors()
            if myerrors:
                print("Blueprint {} has errors".format(blueprint))
                self.finished = True
                node_vars = blueprint.get_ultra_vars()
                print(myerrors)
            else:
                node_vars = blueprint.get_ultra_vars()
                node_elements = blueprint.get_elements(node_vars)
                node_data = node_vars["entrance_world_map_data"]
                mynode = campfeatures.WorldMapNode(destination=node_elements["LOCALE"], entrance=entrance_uid,
                                                   **node_data["node"])
                mynode.visible = True
                mynode.blueprint = blueprint
                mynode.wm_data = node_data
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

        # Add the invisible buttons
        for x in range(self.world_map.width):
            for y in range(self.world_map.height):
                self.children.append(pbge.widgets.Widget(
                    x*32, y*32, 32, 32, data=(x,y), on_click=self._click_world_map,
                    anchor=pbge.frects.ANCHOR_UPPERLEFT, parent=self.world_map_viewer.map_area
                ))

        self.active_entrance_uid = None
        self.active_edge = None

        my_names_and_states = statefinders.get_possible_states(None, "wm_legend_*.png")
        mystates = [a[1] for a in my_names_and_states]

        self.legend_image_list = pbge.image.glob_images("wm_legend_*.png")

        self.node_editor = NodesEditor(self)
        self.children.append(self.node_editor)

        self.edges_editor = EdgesEditor(self)
        self.edges_editor.active = False
        self.children.append(self.edges_editor)

        self.node_button = pbge.widgets.LabelWidget(
            -350, 120, 80, 16, "Nodes", draw_border=True, border=pbge.widgets.widget_border_on,
            on_click=self._switch_to_nodes, justify=0
        )
        self.children.append(self.node_button)

        self.edge_button = pbge.widgets.LabelWidget(
            -250, 120, 80, 16, "Edges", draw_border=True, border=pbge.widgets.widget_border_off,
            on_click=self._switch_to_edges, justify=0
        )
        self.children.append(self.edge_button)

        self.children.append(pbge.widgets.ButtonWidget(
            350, -250, 40, 40, pbge.image.Image("sys_geareditor_buttons.png", 40, 40),
            frame=6, on_click=self._quit_editor
        ))

    def _switch_to_nodes(self, *args):
        self.node_editor.active = True
        self.edges_editor.active = False
        self.node_button.border = pbge.widgets.widget_border_on
        self.edge_button.border = pbge.widgets.widget_border_off
        self.active_entrance_uid = None
        self.active_edge = None

    def _switch_to_edges(self, *args):
        self.node_editor.active = False
        self.edges_editor.active = True
        self.node_button.border = pbge.widgets.widget_border_off
        self.edge_button.border = pbge.widgets.widget_border_on
        self.active_entrance_uid = None
        self.active_edge = None

    def _quit_editor(self, *args):
        self.finished = True

    def _click_world_map(self, wid, ev):
        pygame.event.post(pygame.event.Event(CLICK_WORLD_MAP_TILE_EVENT, pos=wid.data))

    def render(self, flash=False):
        self.world_map_viewer.render(self.active_entrance_uid, self.active_edge)

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
