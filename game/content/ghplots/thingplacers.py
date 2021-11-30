# You need a player to find a thing but you'd rather subcontract out the finding bits.
from pbge.plots import Plot, PlotState
from game.content import plotutility, gharchitecture, ghwaypoints, ghcutscene
import gears
import pbge
from game import teams
import random
import game.content.plotutility
import game.content.gharchitecture
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
from . import missionbuilder


#   ***********************
#   ***  VIP_SCREENING  ***
#   ***********************
#
# Elements:
#  METROSCENE, METRO
#  LOCALE: The place where the NPC will be found; probably a building in METROSCENE, or METROSCENE itself
#  NPC: The VIP to be found; this subplot will place the NPC
#

class DaBouncer(Plot):
    LABEL = "VIP_SCREENING"
    active = True
    scope = "LOCALE"

    def custom_init( self, nart ):
        myroom = self.register_element(
            '_introom', pbge.randmaps.rooms.ClosedRoom(),
            dident="LOCALE"
        )
        bteam = self.register_element("_bteam", teams.Team("Bouncer Team", allies=(self.elements["LOCALE"].civilian_team,)), dident="_introom")
        bouncer = self.register_element("BOUNCER", gears.selector.random_character(self.rank, local_tags=self.elements["METROSCENE"].attributes, job=gears.jobs.ALL_JOBS["Security Guard"]), lock=True, dident="_bteam")

        # Create the VIP's office.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(
            35, 35, "{}'s Office".format(self.elements["NPC"]), player_team=team1, civilian_team=team2,
            attributes=(gears.tags.SCENE_BUILDING,),
            scale=gears.scale.HumanScale)

        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR", dident="LOCALE")
        office = self.register_element('_office',
                                       pbge.randmaps.rooms.ClosedRoom(width=20, height=12,
                                                                      anchor=pbge.randmaps.anchors.south,
                                                                      decorate=gharchitecture.OfficeDecor()),
                                       dident="INTERIOR")
        office.contents.append(team2)
        team2.contents.append(self.elements["NPC"])

        office_exit = ghwaypoints.Exit(name="Exit", anchor=pbge.randmaps.anchors.south)
        office.contents.append(office_exit)

        elevator = self.register_element("_elevator", ghwaypoints.GlassDoor(name="Elevator", plot_locked=True,
                                                                            dest_wp=office_exit), dident="_introom")
        office_exit.dest_wp = elevator

        self.lockpick_pc = None
        self.bribe_cost = gears.selector.calc_mission_reward(self.rank, 300)

        return True

    def BOUNCER_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()

        mylist.append(Offer(
            "{NPC} isn't taking any uninvited visitors right now.".format(**self.elements),
            ContextTag([context.HELLO,]),
        ))

        if camp.credits > self.bribe_cost:
            mylist.append(Offer(
                "By an amazing coincidence, that's exactly the price of the VIP pass. Go right ahead.",
                ContextTag([context.CUSTOM,]), data={"reply": "What if I offer you ${:,}?".format(self.bribe_cost)},
                effect=self._bribe_guard
            ))

        game.ghdialogue.SkillBasedPartyReply(
            Offer("Sorry, my mistake... go right ahead.",
                  context=ContextTag([context.CUSTOM,]),
                  data={"reply": "We have an appointment. Or do you want to tell {} you didn't let {} through?".format(self.elements["NPC"], camp.pc)},
                  effect=self._lie_guard), camp, mylist,
            gears.stats.Charm, gears.stats.Negotiation, self.rank, difficulty=gears.stats.DIFFICULTY_AVERAGE
        )

        game.ghdialogue.SkillBasedPartyReply(
            Offer("Huh? I don't see anything.",
                  context=ContextTag([context.CUSTOM,]),
                  data={"reply": "[DISTRACTION] (Steal Passcard)"},
                  effect=self._steal_card), camp, mylist,
            gears.stats.Reflexes, gears.stats.Stealth, self.rank, difficulty=gears.stats.DIFFICULTY_AVERAGE
        )

        return mylist

    def _bribe_guard(self, camp):
        camp.credits -= self.bribe_cost
        self.elements["BOUNCER"].relationship.reaction_mod += 10
        self.win_missiom(camp)

    def _lie_guard(self, camp):
        camp.dole_xp(100, gears.stats.Negotiation)
        self.win_missiom(camp)

    def _steal_card(self, camp: gears.GearHeadCampaign):
        camp.dole_xp(200, gears.stats.Stealth)
        self.elements["BOUNCER"].relationship.reaction_mod -= 10
        self.win_missiom(camp)

    def _elevator_menu(self, camp, thingmenu: pbge.scenes.waypoints.PuzzleMenu):
        thingmenu.desc = "You stand before an elevator. A passcard is needed to operate it."
        self.lockpick_pc = ghcutscene.AddSkillBasedLancemateMenuItem(
            thingmenu, "[I_CAN_PICK_LOCK]", self._pick_lock, camp, gears.stats.Craft, gears.stats.Computers, self.rank,
            difficulty=gears.stats.DIFFICULTY_HARD, pc_msg="Attempt to pick the lock.", no_random=True
        )
        thingmenu.add_item("Leave it alone.", None)

    def _pick_lock(self, camp):
        camp.dole_xp(100, gears.stats.Computers)
        self.win_missiom(camp)

    def win_missiom(self, camp):
        self.elements["_elevator"].plot_locked = False
        self.end_plot(camp)
        missionbuilder.NewLocationNotification(self.elements["INTERIOR"], self.elements["_elevator"])

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        # The bouncer gets plot armor until the PCs can collect the card.
        npc: gears.base.Character = self.elements["BOUNCER"]
        if not npc.is_operational():
            if camp.get_active_party():
                pbge.alert("You find an passcard for the elevator on {}'s belt.".format(npc))
                self.win_missiom(camp)
            else:
                npc.wipe_damage()

#   *********************
#   ***  PLACE_SCENE  ***
#   *********************
#
# GOAL_SCENE: The scene to be placed
# GOAL_ROOM: The entry room to this scene; may be None
# METROSCENE, MISSION_GATE: How we attach this to the adventure
# ENEMY_FACTION: Optional enemy faction for any combat encounters

class CombatSceneToTargetScene(Plot):
    LABEL = "PLACE_SCENE"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35,35,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE", temporary=True )

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(random.randint(8,15),random.randint(8,15),parent=outside_scene,anchor=pbge.randmaps.anchors.middle))

        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE")
        myent = self.register_element(
            "ENTRANCE",
            game.content.ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"], anchor=pbge.randmaps.anchors.middle),
            dident="ENTRANCE_ROOM"
        )

        inside_scene = self.elements["GOAL_SCENE"]
        inside_room = self.elements.get("GOAL_ROOM")
        if not inside_room:
            introom = self.register_element('GOAL_ROOM',
                                            pbge.randmaps.rooms.ClosedRoom(random.randint(6, 10), random.randint(6, 10),
                                                                         anchor=pbge.randmaps.anchors.south,),
                                            dident="GOAL_SCENE")
        int_con = game.content.plotutility.IntConcreteBuildingConnection(nart, self, outside_scene, inside_scene, room1=mygoal, room2=inside_room)

        self.add_sub_plot(
            nart, "MECHA_ENCOUNTER",
            spstate=PlotState().based_on(self,{"ROOM":mygoal,"FACTION":self.elements.get("ENEMY_FACTION")}),
            necessary=False
        )

        self.location_unlocked = False
        self.add_sub_plot(nart,"REVEAL_LOCATION",spstate=PlotState(
            elements={"INTERESTING_POINT":"There's a mysterious bunker out there."},
        ).based_on(self),ident="LOCATE")
        return True

    def LOCATE_WIN(self,camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def go_to_locale(self,camp):
        camp.go(self.elements["ENTRANCE"])


#   *********************
#   ***  PLACE_THING  ***
#   *********************
#
# THING: The thing to be placed
# METROSCENE, MISSION_GATE: How we attach this to the adventure
# ENEMY_FACTION: Optional enemy faction for any combat encounters


class ThingInBunker(Plot):
    LABEL = "PLACE_THING"
    active = True
    scope = "METRO"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        return_to = (self.elements["METROSCENE"], self.elements["MISSION_GATE"])
        outside_scene = gears.GearHeadScene(
            35,35,plotutility.random_deadzone_spot_name(),player_team=team1,scale=gears.scale.MechaScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        myscenegen = pbge.randmaps.SceneGenerator(outside_scene, game.content.gharchitecture.MechaScaleSemiDeadzone())
        self.register_scene( nart, outside_scene, myscenegen, ident="LOCALE", dident="METROSCENE", temporary=True )

        mygoal = self.register_element("_goalroom",pbge.randmaps.rooms.FuzzyRoom(random.randint(8,15),random.randint(8,15),parent=outside_scene,anchor=pbge.randmaps.anchors.middle))

        self.register_element("ENTRANCE_ROOM", pbge.randmaps.rooms.OpenRoom(5, 5, anchor=random.choice(pbge.randmaps.anchors.EDGES)), dident="LOCALE")
        myent = self.register_element(
            "ENTRANCE",
            game.content.ghwaypoints.Exit(dest_wp=self.elements["MISSION_GATE"], anchor=pbge.randmaps.anchors.middle),
            dident="ENTRANCE_ROOM"
        )

        team1 = teams.Team(name="Player Team")
        inside_scene = gears.GearHeadScene(
            12,12,"Bunker",player_team=team1,scale= gears.scale.HumanScale,
            exploration_music="Lines.ogg", combat_music="Late.ogg",exit_scene_wp=return_to
        )
        intscenegen = pbge.randmaps.SceneGenerator(inside_scene, game.content.gharchitecture.DefaultBuilding())
        self.register_scene( nart, inside_scene, intscenegen, ident="GOALSCENE", dident="LOCALE", temporary=True )

        introom = self.register_element('_introom', pbge.randmaps.rooms.OpenRoom(random.randint(6,10), random.randint(6,10), anchor=pbge.randmaps.anchors.middle, decorate=pbge.randmaps.decor.OmniDec(win=game.content.ghterrain.Window)), dident="GOALSCENE")

        mything = self.elements["THING"]
        self.place_element(mything,introom)

        int_con = game.content.plotutility.IntConcreteBuildingConnection(nart, self, outside_scene, inside_scene, room1=mygoal, room2=introom)

        self.add_sub_plot(
            nart, "MECHA_ENCOUNTER",
            spstate=PlotState().based_on(self,{"ROOM":mygoal,"FACTION":self.elements.get("ENEMY_FACTION")}),
            necessary=False
        )
        self.add_sub_plot(nart,"BASE_ROOM_LOOT",spstate=PlotState(elements={"ROOM":introom,"FACTION":self.elements.get("ENEMY_FACTION")},).based_on(self))

        self.location_unlocked = False
        self.add_sub_plot(nart,"REVEAL_LOCATION",spstate=PlotState(
            elements={"INTERESTING_POINT":"There's a mysterious bunker out there."},
        ).based_on(self),ident="LOCATE")
        return True

    def LOCATE_WIN(self,camp):
        self.location_unlocked = True

    def MISSION_GATE_menu(self, camp, thingmenu):
        if self.location_unlocked:
            thingmenu.add_item("Go to {}".format(self.elements["LOCALE"]), self.go_to_locale)

    def go_to_locale(self,camp):
        camp.go(self.elements["ENTRANCE"])

