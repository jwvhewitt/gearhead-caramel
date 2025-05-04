from typing import override
from game.content.ghplots import missionbuilder
from pbge.plots import Plot
import game
import gears
import pbge
import pygame
import random
from game import teams, ghdialogue
from game.content import gharchitecture, ghwaypoints, plotutility, missiontext, ghcutscene
from pbge.dialogue import Offer, ContextTag
from game.ghdialogue import context
from game.content.ghcutscene import SimpleMonologueDisplay
from game.content import adventureseed
from gears import champions
from game.content.dungeonmaker import DG_NAME, DG_ARCHITECTURE, DG_SCENE_TAGS, DG_MONSTER_TAGS, DG_TEMPORARY, \
    DG_PARENT_SCENE, DG_EXPLO_MUSIC, DG_COMBAT_MUSIC, DG_DECOR
import copy

from . import mission_bigobs
from game.content.ghplots.missionbuilder import MAIN_OBJECTIVE_VALUE

# Mystery missions are exactly what they sound like - a mystery!
# Do not call these missions lightly - save them for one-shot local events and/or lancedev!
# A mystery mission may add an ongoing side story, a permanent complication to the campaign, 
# or who knows what else!
BAMO_MYSTERYMISSION = "BAMO_MYSTERYMISSION"


class MyMi_DoubleEncounter(Plot):
    LABEL = BAMO_MYSTERYMISSION
    active = True
    scope = "LOCALE"

    GOOD_ENEMIES = (
        gears.factions.BioCorp, gears.factions.KettelIndustries, gears.factions.RegExCorporation,
        gears.factions.Ravagers, gears.factions.BladesOfCrihna, gears.factions.BoneDevils,
        gears.factions.TreasureHunters, gears.factions.ProDuelistAssociation
    )

    def custom_init(self, nart):
        myscene = self.elements["LOCALE"]
        a, b = random.sample(self.GOOD_ENEMIES, 2)
        myfac = self.elements.setdefault("ENEMY_FACTION", a)
        roomtype = self.elements["ARCHITECTURE"].get_a_room()
        self.register_element("ROOM", roomtype(15, 15), dident="LOCALE")

        team2 = self.register_element("_eteam", teams.Team(enemies=(myscene.player_team,)), dident="ROOM")
        team3 = self.register_element("_bteam", teams.Team(enemies=(myscene.player_team, team2)))

        mynpc = self.register_element("NPC", nart.camp.cast_a_combatant(
            myfac, self.rank, opposed_faction=self.elements["ALLIED_FACTION"], myplot=self
        ), lock=True)
        _=plotutility.CharacterMover(nart.camp, self, mynpc, myscene, team2)
        myunit = gears.selector.RandomMechaUnit(self.rank, 120, myfac, myscene.environment, add_commander=False)

        team2.contents += myunit.mecha_list

        myunit = gears.selector.RandomMechaUnit(self.rank, 200, b, myscene.environment, add_commander=True)
        self.elements["_commander2"] = myunit.commander
        team3.contents += myunit.mecha_list

        self.obj = adventureseed.MissionObjective("Investigate mecha activity nearby",
                                                  MAIN_OBJECTIVE_VALUE * 2)
        self.adv.objectives.append(self.obj)

        self.intro_ready = True
        self.team_b_deployed = False

        team4 = self.register_element("_cargoteam", teams.Team(), dident="ROOM")
        team4.contents.append(game.content.plotutility.CargoContainer())

        tgen = gears.artifacts.ArtifactBuilder(self.rank)
        self.elements["TREASURE"] = tgen.item

        return True

    def _eteam_ACTIVATETEAM(self, camp):
        if self.intro_ready:
            npc = self.elements["NPC"]
            ghdialogue.start_conversation(camp, camp.pc, npc, cue=ghdialogue.ATTACK_STARTER)
            self.intro_ready = False

    def t_ENDCOMBAT(self, camp: gears.GearHeadCampaign):
        ateam: teams.Team = self.elements["_eteam"]
        bteam: teams.Team = self.elements["_bteam"]
        cteam: teams.Team = self.elements["_cargoteam"]

        if len(ateam.get_members_in_play(camp)) < 1:
            if not self.team_b_deployed:
                _=pbge.alert("Just when you think the battle is over, a second force arrives to claim the cargo.")
                camp.scene.deploy_team(bteam.contents, bteam, self.elements["ROOM"].area)
                self.team_b_deployed = True
            elif len(bteam.get_members_in_play(camp)) < 1:
                if len(cteam.get_members_in_play(camp)) > 0:
                    _=plotutility.ItemGiverWithDisplay(camp, self.elements["TREASURE"], "After the battle, you discover the {} in the cargo container.")
                    self.obj.win(camp, 100)
                else:
                    self.obj.win(camp, 50)

    def NPC_offers(self, camp: gears.GearHeadCampaign):
        mylist = list()
        mylist.append(Offer("[WHATAREYOUDOINGHERE] I was supposed to recover this cargo before anyone else arrives...",
                            context=ContextTag([context.ATTACK, ])))

        mylist.append(Offer(
            "[SO_IT_SEEMS] Maybe we can finish before anyone else arrives. [LETSFIGHT]",
            context=ContextTag([context.COMBAT_CUSTOM, ]),
            data={"reply": "Looks like you're too late for that."}, effect=self.friendly_battle
        ))

        _=game.ghdialogue.SkillBasedPartyReply(
            Offer(
                "[GOOD_POINT] In that case, I'll leave you to it... my sensors indicate you won't have to wait long.",
                context=ContextTag([context.COMBAT_CUSTOM]), effect=self.friendly_retreat,
                data={"reply": "Then you don't stand a chance against both us and whoever else is looking."}
            ), camp, mylist, gears.stats.Ego, gears.stats.Negotiation, self.rank,
            difficulty=gears.stats.DIFFICULTY_HARD, no_random=False
        )

        if not camp.is_unfavorable_to_pc(self.elements["NPC"]):
            mylist.append(Offer(
                "[THANK_YOU] [GOODBYE]",
                context=ContextTag([context.COMBAT_CUSTOM, ]),
                data={"reply": "No worries. I'll get out of your way, then."},
                effect=self.friendly_withdraw
            ))

        return mylist

    def friendly_battle(self, camp: gears.GearHeadCampaign):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        if not npc.relationship.role and not camp.is_favorable_to_pc(npc.faction):
            npc.relationship.role = gears.relationships.R_OPPONENT
        npc.relationship.history.append(gears.relationships.Memory(
            "we fought over a mysterious cargo container",
            "I fought you over a mysterious cargo container",
            5, memtags=(gears.relationships.MEM_Clash, gears.relationships.MEM_Ideological)
        ))

    def friendly_retreat(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        npc.relationship.history.append(gears.relationships.Memory(
            "I left you to fight whoever for a cargo container",
            "I let you go home from a mission early without even fighting",
            10, memtags=(gears.relationships.MEM_Clash, gears.relationships.MEM_CallItADraw)
        ))
        self.elements["_eteam"].retreat(camp)

    def friendly_withdraw(self, camp):
        npc: gears.base.Character = self.elements["NPC"]
        npc.relationship = camp.get_relationship(npc)
        npc.relationship.history.append(gears.relationships.Memory(
            "you let me finish my mission without fighting",
            "I let you have that cargo container without putting up a fight",
            10, memtags=(gears.relationships.MEM_Clash, gears.relationships.MEM_CallItADraw)
        ))
        self.obj.win(camp, 25 + npc.get_reaction_score(camp.pc, camp))
        camp.scene.player_team.retreat(camp)



class MyMi_LancemateTimedDefense(mission_bigobs.BAM_TimedDefense):
    LABEL = BAMO_MYSTERYMISSION
    active = True
    scope = "LOCALE"

    @override
    def custom_init(self, nart):
        ok = super().custom_init(nart)

        npc = nart.camp.egg.seek_dramatis_person(nart.camp, self._is_good_npc, self)
        if not npc:
            return False

        myscene = self.seek_element(nart, "NPC_SCENE", self._is_best_scene, scope=self.elements["METROSCENE"])
        self.register_element("NPC", npc, dident="NPC_SCENE", lock=True)
        _=plotutility.CharacterMover(nart.camp, self, npc, self.elements["LOCALE"], self.elements["_bunkerteam"])

        self.npc_obj = adventureseed.MissionObjective("Defend {}".format(self.elements["NPC"]),
                                                  MAIN_OBJECTIVE_VALUE, can_reset=False)
        self.adv.objectives.append(self.npc_obj)

        self.convo_ready = True

        return ok

    def _is_good_npc(self, camp, candidate):
        return isinstance(candidate, gears.base.Character) and candidate.relationship and gears.relationships.RT_LANCEMATE in candidate.relationship.tags and candidate.combatant

    def _is_best_scene(self, nart, candidate):
        return isinstance(candidate, gears.GearHeadScene) and gears.tags.SCENE_PUBLIC in candidate.attributes

    def t_PCMOVE(self, camp: gears.GearHeadCampaign):
        super().t_PCMOVE(camp)
        if self.combat_started and self.convo_ready:
            ghcutscene.SimpleMonologueDisplay(
                "[HELP_ME_VS_MECHA_COMBAT] This [town] is under attack. We just need to hold on until reinforcements arrive.",
                self.elements["NPC"].get_root()
            )(camp)

            self.convo_ready = False

    def t_COMBATROUND(self, camp):
        super().t_COMBATROUND(camp)

        if self.combat_started and self.round_counter >= self.round_target:
            ally = self.elements["NPC"].get_root()
            if ally.is_operational():
                self.npc_obj.win(camp, 100 - ally.get_percent_damage_over_health())
                ghcutscene.SimpleMonologueDisplay(
                    "[THANKS_FOR_MECHA_COMBAT_HELP] I'll be at {NPC_SCENE} later if you need me.".format(**self.elements),
                    ally
                )(camp)
            else:
                self.elements["NPC"].relationship.reaction_mod -= 20
