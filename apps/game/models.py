from models.models import Model
from ..accounts.models import Account
from ..assets.models import Avatar, Icon, Map
from .utils import calculate_modifier


class Stage(Model):
    title: str = ''
    description: str = ''
    map: int = Map

class Scenario(Model):
    title: str = ''
    description: str = ''
    stage: int = Stage

class Skill(Model):
    title: str = ''
    description: str = ''
    level: int = 0

class Alignment(Model):
    title: str = ''
    description: str = ''
    icon = Icon

class Faction(Model):
    title: str = ''
    description: str = ''
    icon = Icon

class Modification(Model):
    title: str = 0
    description: str = ''

class Item(Model):
    title: str = ''
    description: str = ''
    icon: int = Icon

class Profession(Model):
    title: str = ''
    description: str = ''
    icon: int = Icon

class Gear(Model):
    # TODO Create specific item types.
    head: int = Item
    shoulders: int = Item
    chest: int = Item
    gloves: int = Item
    belt: int = Item
    legs: int = Item
    boots: int = Item
    neck: int = Item
    rings: int = [Item] # max 2
    sockets: int = [Item] # max derived from gear.
    max_sockets: int = 0
    arms: int = [Item] # max 2, some items take 2 slots
    side: int = Item

class SkillTree(Model):
    title: str = ''
    description: str = ''
    skills: set = {Skill}

class CharacterClass(Model):
    title: str = ''
    description: str = ''
    skill_tree: int = SkillTree
    icon: int = Icon

class Race(Model):

    title: str = ''
    description: str = ''
    icon: int = Icon

class Actor(Model):
    name: str = ''
    avatar: int = Avatar
    loc_x: float = 0.0
    loc_y: float = 0.0
    level: int = 0
    strength: int = 0
    constitution: int = 0
    dexterity: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0
    skills: set = {Skill}
    modifications: list = [Modification]
    max_health: float = 0.0
    health: float = 0.0
    max_mana: float = 0.0
    mana: float = 0.0
    stamina: float = 0.0
    max_energy: float = 0.0
    energy: float = 0.0
    block: float = 0.0
    dodge: float = 0.0
    speed: float = 0.0
    perception: float = 0.0
    stealth: float = 0.0
    resist: float = 0.0
    armor: float = 0.0
    spell_power: float = 0.0
    attack_power: float = 0.0
    healing_power: float = 0.0
    spell_critical: float = 0.0
    attack_critical: float = 0.0
    health_regen: float = 0.0
    mana_regen: float = 0.0
    stamina_regen: float = 0.0
    energy_regen: float = 0.0
    spell_penetration: float = 0.0
    armor_penetration: float = 0.0

class Character(Actor):
    player: int = Account
    character_class: int = CharacterClass
    alignment: int = Alignment
    faction: int = Faction
    profession: int = Profession
    race: int = Race
    items: list = [Item]
    experience: float = 0.0
    gear: int = Gear


models = [Scenario, Stage, Character, Skill, Alignment, Faction, SkillTree, CharacterClass, Gear, Profession, Item,
          Modification, Race]
