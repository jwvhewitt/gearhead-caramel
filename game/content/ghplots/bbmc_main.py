import gears
from pbge.plots import Plot, Adventure, PlotState
from game.content.plotutility import LMSkillsSelfIntro
import pbge
from pbge.dialogue import Offer,ContextTag
from game import teams,ghdialogue
from game.ghdialogue import context
import pygame
import random
from game.content.plotutility import AdventureModuleData
from game.content import gharchitecture, ghterrain, ghrooms, ghwaypoints, ghcutscene

class BearBastardMechaCampStub( Plot ):
    LABEL = "SCENARIO_BEARBASTARDSMECHACAMP"
    active = True
    scope = True
    # Creates a Bear Bastard's Mecha Camp adventure.

    ADVENTURE_MODULE_DATA = AdventureModuleData(
        "Bear Bastard's Mecha Camp",
        "Learn everything you need to know about being a mecha pilot from a notorious bandit hoping to cash in on his involvement in the Typhon Incident. Fun and educational!",
        (157, 9, 9), "VHS_BearBastardsMechaCamp.png", convoborder="sys_convoborder_bbmc.png"
    )

    def custom_init( self, nart ):
        """Load the features."""
        self.ADVENTURE_MODULE_DATA.apply(nart.camp)

        myplot = self.add_first_locale_sub_plot( nart, locale_type="BBMC_SceneOne", ident="SCENE_ONE" )
        self.elements["BEARBASTARD"] = myplot.elements["NPC"]

        self.add_sub_plot(nart, "BBMC_SceneTwo", ident="SCENE_TWO")

        return True

    def SCENE_ONE_WIN(self, camp):
        self.subplots["SCENE_TWO"].start_first_battle(camp)


class SceneTwo(Plot):
    LABEL = "BBMC_SceneTwo"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")

        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(
            40, 40, "Last Hope Quarry", player_team=team1, scale=gears.scale.MechaScale,
            combat_music="Jethro on the Run.ogg", exploration_music="A Surprising Encounter.ogg",
            environment=gears.tags.GroundEnv
        )
        myscenegen = pbge.randmaps.SceneGenerator(myscene, gharchitecture.MechaScaleDeadzone())
        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        a1,a2 = random.choice(pbge.randmaps.anchors.OPPOSING_CARDINALS)

        self.register_element("ROOM1", pbge.randmaps.rooms.OpenRoom(anchor=a1), dident="LOCALE")
        self.register_element("ROOM2", pbge.randmaps.rooms.OpenRoom(anchor=a2), dident="LOCALE")
        self.register_element("ROOM3", ghrooms.MSRuinsRoom(15,15,anchor=pbge.randmaps.anchors.middle), dident="LOCALE")

        team2 = self.register_element("TEAM2", teams.Team(name="Enemy Team", enemies=[team1]), dident="ROOM2")

        self.register_element("ENTRANCE1", pbge.scenes.waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle), dident="ROOM1")
        self.register_element("ENTRANCE3", pbge.scenes.waypoints.Waypoint(), dident="ROOM3")

        return True

    def start_first_battle(self, camp: gears.GearHeadCampaign):
        # Give the PC the practice mecha
        self.practice_mek = gears.selector.get_design_by_full_name("CBG-87 Ice Wind")
        self.original_pc_mek = camp.get_pc_mecha(camp.pc)
        camp.party.append(self.practice_mek)
        camp.assign_pilot_to_mecha(camp.pc, self.practice_mek)
        if self.original_pc_mek:
            self.practice_mek.colors = self.original_pc_mek.colors

        camp.go(self.elements["ENTRANCE1"])


class SceneOne(Plot):
    LABEL = "BBMC_SceneOne"
    active = True
    scope = "LOCALE"

    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")

        myscene = gears.GearHeadScene(
            25, 25, "Last Hope Memorial Park", player_team=team1,
            scale=gears.scale.HumanScale, civilian_team=team2, attributes=(gears.personality.DeadZone,),
            exploration_music='Journey of Hope.ogg', combat_music='Jethro on the Run.ogg'
        )
        myscenegen = pbge.randmaps.PartlyUrbanGenerator(
            myscene, gharchitecture.HumanScaleDeadzone(), road_terrain=ghterrain.Flagstone,
            urban_area=ghrooms.GrassRoom(13, 13, anchor=pbge.randmaps.anchors.middle), road_thickness=3
        )
        statue_room = self.register_element("STATUE_ROOM", pbge.randmaps.rooms.OpenRoom(
            7, 7, (pbge.randmaps.IS_CITY_ROOM, pbge.randmaps.IS_CONNECTED_ROOM),
            archi=pbge.randmaps.architect.Architecture(floor_terrain=ghterrain.Flagstone),
            anchor=pbge.randmaps.anchors.middle
        ))
        myscene.contents.append(statue_room)
        statue_room.contents.append(team2)

        entry_room = pbge.randmaps.rooms.Room(
            3, 3, (pbge.randmaps.IS_CONNECTED_ROOM,),
            anchor=pbge.randmaps.anchors.south
        )
        myscene.contents.append(entry_room)
        my_exit = self.register_element(
            "ENTRANCE", ghwaypoints.Exit(
                desc="The way out of the park.\nYou've already paid your momey; might as well stay for the mecha camp.",
                plot_locked=True, anchor=pbge.randmaps.anchors.middle
            )
        )
        entry_room.contents.append(my_exit)

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE",)

        self.register_element("STATUE", ghwaypoints.ParkStatueMan(
            name="Bear Bastard Statue",
            desc="A magnificent statue of Bear Bastard, looking as heroic as possible given the subject matter. A golden plaque at the bottom of the statue reads \"In honor of Bear Bastard, Saviour of Last Hope, Master of the Impossible\".",
            anchor=pbge.randmaps.anchors.middle
        ), dident="STATUE_ROOM")

        west_shrine_room = self.register_element(
            "_west_shrine_room", pbge.randmaps.rooms.Room(5,15,anchor=pbge.randmaps.anchors.west), dident="LOCALE"
        )

        east_shrine_room = self.register_element(
            "_east_shrine_room", pbge.randmaps.rooms.Room(5,15,anchor=pbge.randmaps.anchors.east), dident="LOCALE"
        )

        north_shrine_room = self.register_element(
            "_north_shrine_room", pbge.randmaps.rooms.Room(5,5,anchor=pbge.randmaps.anchors.north), dident="LOCALE"
        )

        self.register_element(
            "DUTY_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Duty",
                desc="The plaque on this shrine reads:\n\"Let me be honest and true at all times, and never fail to fulfil my responsibilites.\"",
                anchor=pbge.randmaps.anchors.south
            ), dident="_west_shrine_room"
        )

        self.register_element(
            "FELLOWSHIP_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Fellowship",
                desc="The plaque on this shrine reads:\n\"Let me be considerate to all in everything I do, and do wrong by no one.\"",
                anchor=pbge.randmaps.anchors.north
            ), dident="_west_shrine_room"
        )

        self.register_element(
            "GLORY_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Glory",
                desc="The plaque on this shrine reads:\n\"Let me strive every moment to make myself better and better, to the best of my ability, that all may profit by it.\"",
                anchor=pbge.randmaps.anchors.middle
            ), dident="_north_shrine_room"
        )

        self.register_element(
            "JUSTICE_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Justice",
                desc="The plaque on this shrine reads:\n\"Let me think of the right and lend all my assistance to those who need it, with no regard for anything but justice.\"",
                anchor=pbge.randmaps.anchors.north
            ), dident="_east_shrine_room"
        )


        self.register_element(
            "PEACE_SHRINE", ghwaypoints.Shrine(
                name="Shrine of Peace",
                desc="The plaque on this shrine reads:\n\"Let me act always with compassion, and wield my immense power only to protect life.\"",
                anchor=pbge.randmaps.anchors.south
            ), dident="_east_shrine_room"
        )

        self.register_element("PRESENT", gears.base.Treasure(name="Present", value=10))

        npc: gears.base.Character = self.register_element("NPC", nart.camp.get_major_npc("Bear Bastard"))
        npc.place(myscene, team=team2)

        self.intro_ready = True
        self.impatience_counter = -1
        self.had_first_conversation = False
        self.finished_bump_practice = False
        self.tiles_moved = 0
        self.bumped_objects = set()
        self.had_second_conversation = False
        self.finished_pickup_practice = False
        self.opened_mecha_arena = False

        return True

    def LOCALE_ENTER(self, camp):
        if self.intro_ready:
            pbge.alert("You enter Last Hope Memorial Park, eager for the first day of mecha camp. Today is the day you learn how to be a proper cavalier!")
            if camp.pc.has_badge("Typhon Slayer"):
                pbge.alert("Not that you aren't already a highly accomplished cavalier. But it never hurts to get a refresher every once in a while.")
            ghcutscene.SimpleMonologueDisplay(
                "Listen close, {pc.gender.noun}-cub! I'm Bear Bastard, hero of the Typhon Incident! I'll be running this camp for aspiring cavaliers such as yourself. Why don't you come over here so we can talk?".format(pc=camp.pc),
                self.elements["NPC"]
            )(camp)
            self.intro_ready = False
            self.impatience_counter = 0

    def t_HALFMINUTE(self, camp):
        if self.impatience_counter > -1:
            if not self.had_first_conversation:
                self.impatience_counter += 1
                if self.impatience_counter == 2:
                    ghcutscene.SimpleMonologueDisplay(
                        "Alright, I can see you've got some problems with doing what you're told. That's actually kinda relateable. Just see if you can move over to me and we can start the conversation.",
                        self.elements["NPC"]
                    )(camp)

                elif self.impatience_counter == 3:
                    ghcutscene.SimpleMonologueDisplay(
                        "Okay, you know what? Let's try a visualization exercise. Pretend you've got a keyboard and/or a mouse right there in front of you. Or a joypad if you're into that steamy stuff. Imagine an orange square on the ground.",
                        self.elements["NPC"]
                    )(camp)
                    ghcutscene.SimpleMonologueDisplay(
                        "You can move this orange cursor around with the power of your mind, by which I mean your mouse or numeric keypad or whatever. Move the cursor over to me and left click. Or press enter. That should get the job done.",
                        self.elements["NPC"]
                    )(camp, False)
            elif self.finished_bump_practice and not self.had_second_conversation:
                self.impatience_counter += 1
                if self.impatience_counter % 2 == 0:
                    ghcutscene.SimpleMonologueDisplay(
                        "I'm getting bored over here... finish looking around and come talk to me. It's not that big of a park.",
                        self.elements["NPC"]
                    )(camp)

    def STATUE_BUMP(self, camp):
        if not self.had_first_conversation:
            ghcutscene.SimpleMonologueDisplay(
                "Alright, so you can move. I can see how you'd get us confused, with the both of us being ruggedly handsome and all, but that statue ain't gonna talk back to you. What you need to do is come bump into me.",
                self.elements["NPC"]
            )(camp)
        elif not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["STATUE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def ENTRANCE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["ENTRANCE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def ENTRANCE_menu(self, camp, thingmenu):
        if self.opened_mecha_arena:
            thingmenu.desc = "Having finished training at the park, it's time to go to the mecha arena and learn how to fight."
            thingmenu.add_item("Go to the arena.", self._win_scene_one)
            thingmenu.add_item("Stay here a bit longer.", None)
        elif pbge.util.config.getboolean("GENERAL", "dev_mode_on"):
            thingmenu.add_item("Skip straight to the arena.", self._win_scene_one)
            thingmenu.add_item("Why be in such a hurry?", None)

    def _win_scene_one(self, camp: gears.GearHeadCampaign):
        camp.check_trigger("WIN", self)

    def DUTY_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["DUTY_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def FELLOWSHIP_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["FELLOWSHIP_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def GLORY_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["GLORY_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def JUSTICE_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["JUSTICE_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def PEACE_SHRINE_BUMP(self, camp):
        if self.had_first_conversation and not self.finished_bump_practice:
            self.bumped_objects.add(self.elements["PEACE_SHRINE"])
            if len(self.bumped_objects) > 3:
                self._complete_bump_practice(camp)

    def NPC_offers(self, camp):
        mylist = list()
        npc: gears.base.Character = self.elements["NPC"]
        if not self.had_first_conversation:
            if camp.pc.has_badge("Typhon Slayer") or (npc.relationship and gears.relationships.RT_LANCEMATE in npc.relationship.tags):
                mylist.append(Offer(
                    "[SWEAR] It's you, [audience]! What the bloody bazookas are you doing here? You're not a beginner mecha pilot.",
                    ContextTag([context.HELLO]), effect=self._have_first_conversation, allow_generics=False
                ))
                mylist.append(Offer(
                    "Yeah, I suppose... the next technology we're going to practice is moving around and bumping into things. Take a look at some of the stuff in this park. Just walk over and bump into it, like you did for me.",
                    ContextTag([context.CUSTOM]), data={"reply": "A cavalier should always keep up with the latest technology."}, allow_generics=False
                ))
                mylist.append(Offer(
                    "No scam, I've gone legit. This is me sharing my years of mecha piloting knowledge to the youngster generation. So the next lesson is moving around and bumping into stuff. Take a look at the things in this park. Just walk over and bump into 'em, like you did for me.",
                    ContextTag([context.CUSTOM]), data={"reply": "I'm checking up on you; see what kind of scam you're pulling this time."}, allow_generics=False
                ))

            else:
                mylist.append(Offer(
                    "Good job, you can move around and interact with other people. You're going to be doing a whole lot of that as a cavalier.",
                    ContextTag([context.HELLO]), effect=self._have_first_conversation, allow_generics=False
                ))

                mylist.append(Offer(
                    "You're gonna walk around the park and bump into stuff. You might have noticed there's a bunch of things in the park. Just like starting the conversation with me, you can interact with these things by walking right up to them and seeing what happens.",
                    ContextTag([context.CUSTOM]), data={"reply": "[THANKS_FOR_ADVICE] What's next?"}, allow_generics=False
                ))

            mylist.append(Offer(
                "You say that now, but just wait until the next bit! We're going to try moving around and bumping into stuff! That's how you interact with most things in this messed-up world... just walk straight up to a thing and see what happens.",
                ContextTag([context.CUSTOM]), data={"reply": "Gee, this lesson has really been worth the money I paid so far."}, allow_generics=False
            ))


        elif not self.finished_bump_practice:
            mylist.append(Offer(
                "Your next job is to walk around for a bit and check out the things in the park. Let's do some visualization: you can do that by moving the cursor over the thing you want to examine, using either your mental mouse or spiritual numeric keypad, and left clicking or pressing enter.",
                ContextTag([context.HELLO]), allow_generics=False
            ))
            mylist.append(Offer(
                "Ooh, now you're getting into advanced territory. Right clicking brings up your Mind Palace Popup Menu! From there you can choose to interact with the object or do a whole bunch of other things.",
                ContextTag([context.CUSTOM]), data={"reply": "What happens if I right click instead?"},
                allow_generics=False
            ))

        elif self.finished_bump_practice and not self.finished_pickup_practice:
            mylist.append(Offer(
                "I've just sent a message to your phone. You can take a look at memos by pressing 'm' or right-clicking to get the popup menu. After this, we move on to the good stuff.",
                ContextTag([context.HELLO]), allow_generics=False, effect=self._have_second_conversation
            ))

        elif self.finished_pickup_practice:
            mylist.append(Offer(
                "That's all you need to know about moving around. Next, I'm gonna teach you how to fight! Head to the park exit and we can go to Last Hope Arena.",
                ContextTag([context.HELLO]), allow_generics=False, effect=self._open_mecha_arena
            ))

        return mylist

    def _open_mecha_arena(self, camp):
        self.opened_mecha_arena = True
        self.memo = "Go to the park exit and enter mecha combat."

    def t_PCMOVE(self,camp):
        if self.had_first_conversation and not self.finished_bump_practice and self.tiles_moved > -1:
            self.tiles_moved += 1
            if self.tiles_moved > 10:
                ghcutscene.SimpleMonologueDisplay(
                    "Wow, look at you, movin' all around the park, just like a pro!",
                    self.elements["NPC"]
                )(camp)
                self.tiles_moved = -1

    def _have_first_conversation(self, camp):
        self.had_first_conversation =True

    def _have_second_conversation(self, camp):
        # Actually isn't this the third conversation? I can't remember anymore. Whatever.
        self.had_second_conversation =True
        self.memo = "I left a present for you somewhere in this park. I'll just say, you can find it between Justice and Peace. Pretty good riddle, huh? To pick it up move to the tile where the box is, then click on that tile again."
        present: gears.base.Treasure = self.elements["PRESENT"]
        present.place(self.elements["LOCALE"], (23, 12))

    def PRESENT_GET(self, camp):
        pbge.alert("Suddenly, the box explodes in your hands!")
        pbge.my_state.view.play_anims(gears.geffects.SuperBoom(pos=camp.pc.pos), pbge.scenes.animobs.Caption("Surprise!", pos=camp.pc.pos, delay=6))
        present: gears.base.Treasure = self.elements["PRESENT"]
        if present in camp.pc.inv_com:
            camp.pc.inv_com.remove(present)
        ghcutscene.SimpleMonologueDisplay(
            "And let that be a lesson to you- you can't trust everyone you meet. That was just a firecracker but it could've been a plasma grenade or worse. This is what you call the tough love school of teaching. Come back over here; I have one last thing to discuss.",
            self.elements["NPC"]
        )(camp)
        self.memo = "Return to Bear Bastard for one more conversation."
        self.finished_pickup_practice = True

    def _complete_bump_practice(self, camp):
        self.finished_bump_practice = True
        ghcutscene.SimpleMonologueDisplay(
            "Alright, that's enough bumpin' practice for now. You can finish looking around the park, then come back and talk to me again. We've got one more lesson before you're ready to get in a mek.",
            self.elements["NPC"]
        )(camp)
        self.impatience_counter = 0

