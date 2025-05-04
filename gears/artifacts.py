from gears import selector
from . import base, scale, stats, attackattributes, geffects, materials
import random
import collections
import pbge

class MeleeWeaponClass:
    def __init__(self, name, min_damage=1, min_accuracy=1, min_penetration=1, reach=1, attack_stat=stats.Reflexes, attributes=(), shot_anim=None, min_rank=0, alt_names=()):
        self.name = name
        self.min_damage = min_damage
        self.min_accuracy = min_accuracy
        self.min_penetration = min_penetration
        self.reach = reach
        self.attack_stat=attack_stat
        self.attributes = list(attributes)
        self.shot_anim = shot_anim
        self.min_rank = min_rank
        self.alt_names = list(alt_names)

    def generate_weapon(self, weapon_scale=scale.MechaScale):
        return base.MeleeWeapon(
            name=self.name, reach=self.reach, damage=self.min_damage, accuracy=self.min_accuracy,
            penetration=self.min_penetration, attack_stat=self.attack_stat, scale=weapon_scale,
            attributes=self.attributes, shot_anim=self.shot_anim or geffects.SlashShot
        )

    ENERGY_TYPES = (
        "Beam", "Energy", "Plasma", "Laser", "Heat", "Power"
    )

    def generate_energy_weapon(self, weapon_scale=scale.MechaScale):
        return base.EnergyWeapon(
            name="{} {}".format(random.choice(self.ENERGY_TYPES), self.name), reach=self.reach, damage=self.min_damage, accuracy=self.min_accuracy,
            penetration=self.min_penetration, attack_stat=self.attack_stat, scale=weapon_scale,
            attributes=self.attributes, shot_anim=self.shot_anim or geffects.BeamSlashShot
        )

MELEE_WEAPON_CLASSES = (
    MeleeWeaponClass("Sword", min_damage=2, min_accuracy=2, attributes=(attackattributes.Defender,), alt_names=("Blade",)),
    MeleeWeaponClass("Scimitar", min_damage=2, min_accuracy=2, attributes=(attackattributes.Defender,), alt_names=("Sword", "Blade",)),
    MeleeWeaponClass("Katana", min_damage=2, min_accuracy=2, min_penetration=2, min_rank=35, alt_names=("Sword", "Blade",)),
    MeleeWeaponClass("Machete", min_accuracy=2, min_penetration=2, alt_names=("Blade",)),
    MeleeWeaponClass("Flamberge", min_damage=2, min_penetration=2, attributes=(attackattributes.Defender,), alt_names=("Sword", "Blade",)),
    MeleeWeaponClass("Dagger", min_accuracy=2, attributes=(attackattributes.FastAttack,), alt_names=("Blade",)),
    MeleeWeaponClass("Knife", min_accuracy=2, attack_stat=stats.Speed, attributes=(attackattributes.FastAttack,), alt_names=("Blade",)),
    MeleeWeaponClass("Axe", min_damage=2, min_penetration=2,),
    MeleeWeaponClass("Hammer", attack_stat=stats.Body, attributes=(attackattributes.Smash,)),
    MeleeWeaponClass("Staff", attack_stat=stats.Body, attributes=(attackattributes.Defender,)),
    MeleeWeaponClass("Rapier", min_accuracy=2, attack_stat=stats.Speed, attributes=(attackattributes.Defender,), alt_names=("Sword", "Foil")),
    MeleeWeaponClass("Mace", min_penetration=2, attributes=(attackattributes.Smash,)),
    MeleeWeaponClass("Morningstar", min_damage=2, attributes=(attackattributes.Brutal,)),
    MeleeWeaponClass("Flail", attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Lash", attack_stat=stats.Speed, attributes=(attackattributes.Flail,)),
    MeleeWeaponClass("Whip", reach=2, attack_stat=stats.Speed, attributes=(attackattributes.Flail,), min_rank=35),
    MeleeWeaponClass("Chain", min_damage=2, reach=2, attack_stat=stats.Speed, attributes=(attackattributes.Flail,), min_rank=55),
    MeleeWeaponClass("Spear", reach=2),
    MeleeWeaponClass("Lance", reach=2, attributes=(attackattributes.ChargeAttack,), min_rank=60),
    MeleeWeaponClass("Trident", min_penetration=2, reach=2, attributes=(attackattributes.ChargeAttack,), alt_names=("Spear",), min_rank=70),
    MeleeWeaponClass("Scythe", min_damage=2, min_penetration=2, reach=2, min_rank=55, alt_names=("Blade",)),
    MeleeWeaponClass("Halberd", reach=2, min_damage=2, min_accuracy=2, min_rank=45, alt_names=("Blade",)),
    MeleeWeaponClass("Glaive", min_damage=2, reach=2, min_rank=40, alt_names=("Blade",)),
    MeleeWeaponClass("Ranseur", reach=2, attributes=(attackattributes.Defender,), min_rank=50, alt_names=("Spear",)),
    MeleeWeaponClass("Naginata", min_damage=2, reach=2, attributes=(attackattributes.FastAttack,), min_rank=55),
    MeleeWeaponClass("Greathammer", min_damage=2, reach=2, attack_stat=stats.Body, attributes=(attackattributes.Smash,), min_rank=40, alt_names=("Hammer",)),
    MeleeWeaponClass("Meteor Hammer", min_penetration=2, reach=3, attack_stat=stats.Speed, attributes=(attackattributes.Flail,), min_rank=75, alt_names=("Chain",)),
    MeleeWeaponClass("Boomerang", reach=3, alt_names=("Wing",)),
    MeleeWeaponClass("Shuriken", min_accuracy=2, reach=3, min_rank=50, alt_names=("Star",)),

)

MELEE_WEAPON_ATTRIBUTES = (
    attackattributes.Accurate, attackattributes.Agonize, attackattributes.BonusStrike1, attackattributes.BonusStrike2, 
    attackattributes.Brutal, attackattributes.BurnAttack, attackattributes.ChargeAttack,
    attackattributes.Defender, attackattributes.FastAttack, attackattributes.HaywireAttack,
)

MECHA_SCALE_MELEE_WEAPON_ATTRIBUTES = (
    attackattributes.OverloadAttack, attackattributes.DrainsPower
)

PERSONAL_SCALE_MELEE_WEAPON_ATTRIBUTES = (
    attackattributes.PoisonAttack,
)

class ArtifactBuilder:
    GENERIC_GRAMMAR = {
        "[historical_era]": [
            "the Age of Superpowers", "the previous age", "the Exodus", "the Homecoming", "the settlement of [planet]",
            "PreZero times"
        ],
        "[planet]": [
            "Luna", "Mars", "Venus", "the L5 system", "the L4 system",
        ],
        "[nationality]": [
            "PreZero", "Terran", "Orbital", "Lunar", "Martian", "Ravager",
        ],
        "[concept]": [
            "Concept", "Idea", "Sound", "Vision", "Color", "Measure", "Dream", "Database",
            "Ghost", "Scent", "Memory", "Illusion", "Simulacrum", "Song", "Price", "Awareness",
            "Dance", "Glow", "Echo", "Shadow", 
        ],
        "[theme]": [
            "Love", "Death", "Taxes", "Beauty", "Mecha", "Fortune", "Happiness", "Sorrow",
            "Passion", "Peace", "Friendship", "Solitude", "Battle", "Hope", "Night",
            "Life", "Light", "Struggle", "Betrayal", "Cosmos", "Sex", "Everything",
            "Fantasy", "Jealousy", "Happiness", "Freedom", "Justice", "Order", "Pride",
            "Utopia", "Metropolis", "Nature", "History", "Future", "Nothingness",
            "Despair", "Passion", "Ecstasy", "Devotion", "Faith", "Reason", "Water", "Spring",
            "Summer", "Autumn", "Winter", "Tacos", "Data", "Pain", "Pleasure", "Legend",
        ],
    }

    MELEE_WEAPON_GRAMMAR = {
        "[name]":  [
            "[proper_name] [base_name]", "[proper_name] [alt_name]", "[alt_name] of [proper_name]", "[base_name] of [proper_name]",
            "[adjective] [alt_name] of [proper_name]",
            "[adjective] [base_name] of [proper_name]", "[proper_name] [adjective] [alt_name]",
            "[alt_name] of [adjective] [proper_name]", "[base_name] of [adjective] [proper_name]",
        ],
        "[desc]": [
            "[ItemIdentity] [ItemOrigin]. [ITEM_DESCRIPTION]"
        ],
        "[ItemIdentity]": [
            "This [base_name]", "The [final_name]"
        ],
        "[ItemOrigin]": [
            "is of unknown origin", "was developed in a [origin] lab", "was crafted for a [origin] pilot",
            "is the result of a [origin] weapons program", "is a heavily modified [nationality] [alt_name]",
            "was previously owned by a [owner_adjective] [owner]", "was custom built for a [owner]",
            "is a prototype designed by [origin] engineers", "was custom built for a [owner_adjective] [owner]",
            "was built to the specifications of a [origin] [job]", "was constructed during [historical_era]",
        ],
        "[ITEM_DESCRIPTION]": [
            "It was designed to [capability] against [target].", "It can [capability].",
            "It is highly effective against [target].", "To eliminate [target], this weapon can [capability].",
            "It is effective against [target].", "It can [capability] to defeat [target].",
        ],
        "[origin]": [
            "secret", "advanced", "mysterious", "[nationality]", "illicit", "criminal", "top secret",
            "amateur", "government"
        ],
        "[owner]": [
            "[nationality] [job]", "[job]"
        ],
        "[job]": [
            "pilot", "cavalier", "duelist", "gladiator", "soldier", "commander", "pirate", "aristo"
        ],
        "[owner_adjective]": [
            "famous", "infamous", "legendary", "ill-fated", "ambitious"
        ],
    }

    ARTWORK_GRAMMAR = {
        "[name]": [
            "[concept] of [theme]", "[adjective] [theme]", "[concept] of the [adjective] [noun]",
            "[noun] and [adjective] [theme]", "[adjective] [concept] of [noun]", "[noun] and [theme]"
        ],
        "[desc]": [
            "This [medium] dates from [historical_era]."
        ],
        "[medium]": [
            "painting", "sculpture", "pottery", "print", "bowl", "collectable figure", "poem",
            "holo-form", "postcard", "advertisement", "greeting card", "toy", "lamp", "phone charger",
            "bracelet", "necklace", "dongle", "triptych", "diptych", "kaleidoscope", "transit card"
        ],
        "[adjective]": [
            "Useless", "Useful", "Artificial", "Adorable", "Uncomfortable", "Comfortable", "Good", "Bad", "Open",
            "Modern",
            "Shiny", "Bright", "Honorable", "Stupid", "Smart", "Healthy", "Sinful", "Interesting", "Surprising",
            "Bland",
            "Sexy", "Loud", "Quiet", "New", "Important", "Wonderful", "Great", "Fun", "Beautiful", "Pretty", "Ugly",
            "Cool", "Strange", "Fast", "Slow", "Lucky", "Big", "Huge", "Long", "Small", "Tiny", "Exciting", "Gigantic",
            "Cosmic", "Natural", "Unwanted", "Delicate", "Stormy", "Fragile", "Strong", "Flexible", "Rigid", "Cold",
            "Hot", "Irradiated", "Poor", "Living", "Dead", "Creamy", "Delicious", "Cool", "Excellent", "Boring",
            "Happy",
            "Sad", "Confusing", "Valuable", "Old", "Young", "Loud", "Hidden", "Bouncy", "Magnetic", "Smelly", "Hard",
            "Easy", "Serious", "Kind", "Gentle", "Greedy", "Lovely", "Cute", "Plain", "Dangerous", "Silly", "Smart",
            "Fresh", "Obsolete", "Perfect", "Ideal", "Professional", "Current", "Fat", "Rich", "Poor", "Wise", "Absurd",
            "Foolish", "Blind", "Deaf", "Creepy", "Nice", "Adequate", "Expensive", "Cheap", "Fluffy", "Rusted",
            "Hormonal",
            "Lying", "Freezing", "Acidic", "Green", "Red", "Blue", "Yellow", "Orange", 'Purple', "Grey", "Brown",
            "Pink",
            "Dirty", "Gothic", "Metallic", "Mutagenic", "Outrageous", "Incredible", "Miraculous", "Unlucky",
            "Hated", "Loved", "Feared"
        ],
        "[noun]": [
            "Hominid", "Underwear", "Paluke", "Artifice", "Lie", "Knowledge", "Battle", "Weather", "Food", "News",
            "Mecha", "Fashion", "Athlete", "Music", "Politics", "Religion", "Love", "War", "History",
            "Technology", "Time", "Internet", "Literature", "Destiny", "Romance", "Base", "Stuff", "Agriculture",
            "Sports", "Science", "Television", "Atmosphere", "Sky", "Color", "Sound", "Taste", "Friendship", "Law",
            "Beer", "Singing", "Cola", "Pizza", "Vaporware", "Buzz", "Mood", "Dissent", "City", "House", "Town",
            "Village", "Country", "Planet", "Fortress", "Universe", "Program", "Arena", "Wangtta", "Hospital",
            "Medicine", "Therapy", "Library", "Education", "Philosophy", "Family", "Jive", "Feel", "Coffee",
            "Hope", "Hate", "Love", "Fear", "Sale", "Life", "Market", "Enemy", "Data", "Fish", "Beast",
            "Something", "Everything", "Nothing", "Sabotage", "Justice", "Fruit", "Pocket", "Parfait", "Flavor",
            "Talent", "Prison", "Plan", "Noise", "Bottom", "Force", "Anything", "Top", "Appeal", "Booster",
            "Complaint", "Chatting", "Dream", "Heart", "Secret", "Fauna", "Desire", "Situation", "Risk",
            "Crime", "Vice", "Virtue", "Treasure", "Storm", "Vapor", "School", "Uniform", "World", "Body",
            "Pain", "Fault", "Profit", "Business", "Prophet", "Animal", "Bedroom", "Kitchen", "Home", "Apartment",
            "Vehicle", "Machine", "Bathroom", "Fruit", "Side", "Entertainment", "Movie", "Game", "Chemistry",
            "Synergy", "Opinion", "Hero", "Villain", "Thief", "Fantasy", "Adventure", "Mission", "Job",
            "Career", "Glamour", "Diary", "Expression", "Hairdo", "Environment", "Wizard", "Drug"
        ]
    }

    def __init__(self, rank, target_scale=scale.MechaScale, auto_generate=True):
        self.rank = max(rank + random.randint(1,10), 10)
        if random.randint(1,5) == 3:
            self.rank += random.randint(-5, 10)
        self.grammar = collections.defaultdict(list)
        pbge.dialogue.grammar.Grammar.absorb(self.grammar, self.GENERIC_GRAMMAR)
        self.target_scale = target_scale
        self.item = None

        if auto_generate:
            self.generate_melee_weapon()

    def generate_artwork(self):
        # A treasure worth about as much as you'd expect.
        pbge.dialogue.grammar.Grammar.absorb(self.grammar, self.ARTWORK_GRAMMAR)
        self.item = base.Treasure(value=selector.calc_mission_reward(self.rank, random.randint(200,500), round_it_off=True), weight=min(random.randint(5,50), random.randint(5,50)))

        self.item.name = pbge.dialogue.grammar.convert_tokens("[name]", self.grammar)
        self.grammar["[final_name]"].append(str(self.item.name))
        self.item.desc = pbge.dialogue.grammar.convert_tokens("[desc]", self.grammar)

    def _improve_damage(self):
        self.item.damage += 1

    def _improve_accuracy(self):
        self.item.accuracy += 1

    def _improve_penetration(self):
        self.item.penetration += 1

    def _gain_melee_attribute(self):
        nu_aa = random.choice(self._get_melee_attack_attributes())
        if hasattr(nu_aa, "FAMILY") and nu_aa.FAMILY:
            for old_aa in list(self.item.attributes):
                if hasattr(old_aa, "FAMILY") and old_aa.FAMILY == nu_aa.FAMILY:
                    self.item.attributes.remove(old_aa)
        self.item.attributes.append(nu_aa)

    def _get_melee_attack_attributes(self):
        candidates = list(MELEE_WEAPON_ATTRIBUTES)
        if self.target_scale is scale.MechaScale:
            candidates += list(MECHA_SCALE_MELEE_WEAPON_ATTRIBUTES)
        elif self.target_scale is scale.HumanScale:
            candidates += list(PERSONAL_SCALE_MELEE_WEAPON_ATTRIBUTES)
        return self._get_possible_attack_attributes(candidates)

    def _get_possible_attack_attributes(self, full_list):
        candidates = list()
        for aa in full_list:
            if aa not in self.item.LEGAL_ATTRIBUTES:
                continue
            if aa in self.item.attributes:
                continue
            if hasattr(aa, "FAMILY") and aa.FAMILY and any([(getattr(wa, "FAMILY", None)==aa.FAMILY and wa.COST_MODIFIER >= aa.COST_MODIFIER) for wa in self.item.attributes]):
                continue
            candidates.append(aa)
        return [aa for aa in full_list if aa in self.item.LEGAL_ATTRIBUTES and aa not in self.item.attributes]

    def _build_weapon_grammar(self):
        for aa in self.item.attributes:
            if hasattr(aa, "ADJECTIVES"):
                self.grammar["[adjective]"] += list(aa.ADJECTIVES)
            if hasattr(aa, "TARGETS"):
                self.grammar["[target]"] += list(aa.TARGETS)
            if hasattr(aa, "CAPABILITIES"):
                self.grammar["[capability]"] += list(aa.CAPABILITIES)

        if self.item.accuracy > 2:
            self.grammar["[target]"].append("highly mobile targets")
            self.grammar["[capability]"].append("strike agile enemies")
        if self.item.penetration > 2:
            self.grammar["[target]"].append("heavily armored targets")
            self.grammar["[capability]"].append("penetrate thick armor")
        if self.item.damage > 2:
            self.grammar["[target]"].append("large targets")
            self.grammar["[capability]"].append("cause massive damage")
        else:
            self.grammar["[target]"].append("light targets")


    def generate_melee_weapon(self):
        pbge.dialogue.grammar.Grammar.absorb(self.grammar, self.MELEE_WEAPON_GRAMMAR)
        myclass = random.choice([mw for mw in MELEE_WEAPON_CLASSES if mw.min_rank <= self.rank])
        if random.randint(1,3) == 2 or self.rank > random.randint(25,120):
            self.item = myclass.generate_energy_weapon(self.target_scale)
            self.grammar["[alt_name]"].append(myclass.name)
        else:
            self.item = myclass.generate_weapon(self.target_scale)

        self.grammar["[base_name]"].append(self.item.name)
        self.grammar["[alt_name]"] += myclass.alt_names

        proper_name_candidates = [selector.GENERIC_NAMES.gen_word(), selector.PREZERO_NAMES.gen_word()]

        material = materials.Metal
        if max(random.randint(20,200), random.randint(20,200)) <= self.rank:
            material = materials.Biotech
            proper_name_candidates.append(selector.PREZERO_NAMES.gen_word())
            proper_name_candidates.append(selector.VENUS_NAMES.gen_word())
            self.grammar["[adjective]"].append("Bio")
            self.grammar["[origin]"] += ["PreZero", "Vesuvian", "ancient", "Pax Europan", "Imperator Zetan",]
        elif random.randint(0,120) <= self.rank:
            material = materials.Advanced
            for t in range(2):
                proper_name_candidates.append(selector.ORBITAL_NAMES.gen_word())
            self.grammar["[origin]"] += ["corporate",]
        elif random.randint(0,75) <= min(self.rank, 74):
            material = materials.Ceramic
            for t in range(2):
                proper_name_candidates.append(selector.LUNA_NAMES.gen_word())
            self.grammar["[origin]"] += ["Lunar", "orbital",]

        self.grammar["[proper_name]"].append(random.choice(proper_name_candidates))

        while self.item.shop_rank() < max(self.rank, 25):
            candidates = list()
            if self.item.damage < self.item.MAX_DAMAGE:
                candidates += [self._improve_damage] * 4
            if self.item.accuracy < self.item.MAX_ACCURACY:
                candidates += [self._improve_accuracy] * 3
            if self.item.penetration < self.item.MAX_PENETRATION:
                candidates += [self._improve_penetration] * 3
            if self._get_melee_attack_attributes() and len(self.item.attributes) < 3:
                candidates += [self._gain_melee_attribute] * (3 - len(self.item.attributes))

            if not candidates:
                break

            upgrade = random.choice(candidates)
            upgrade()

        if random.randint(1,50) == 23:
            self.item.attack_stat = random.choice(stats.PRIMARY_STATS)

        self.item.material = material

        self._build_weapon_grammar()
        self.item.name = pbge.dialogue.grammar.convert_tokens("[name]", self.grammar)
        self.grammar["[final_name]"].append(str(self.item.name))
        self.item.desc = pbge.dialogue.grammar.convert_tokens("[desc]", self.grammar)



