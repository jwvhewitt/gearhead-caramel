import pbge

class MoveModelToPos:
    def __init__(self, camp, chara, nav, dest):
        self.camp = camp
        self.chara = chara
        self.nav = nav
        self.dest = dest
        self.is_player_model = chara in self.camp.party
        self.path = self.nav.get_path(dest)[1:]

    def __call__(self):
        if self.path:
            p = self.path.pop(0)
            self.camp.fight.step(self.chara, p)
            if self.is_player_model:
                self.camp.scene.update_party_position(self.camp)
            if not self.path:
                # Spend the movement points.
                self.camp.fight.cstat[self.chara].spend_mp(self.nav.cost_to_tile[self.chara.pos])
                return False
            else:
                return True

class InvokeInvocation:
    def __init__(self, camp, invo: pbge.effects.Invocation, firing_pos, chara, targets, data):
        self.camp = camp
        self.invo = invo
        self.firing_pos = firing_pos
        self.chara = chara
        self.targets = targets
        self.data = data

    def __call__(self):
        if self.chara.pos == self.firing_pos:
            # Spend the movement points.
            _=self.invo.invoke(self.camp, self.chara, self.targets, pbge.my_state.view.anim_list, data=self.data)
            self.camp.fight.cstat[self.chara].spend_ap(1)
