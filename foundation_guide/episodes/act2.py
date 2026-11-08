"""Act II — The Mayors.

Salvor Hardin has a week, a Board of Trustees who would rather edit an
encyclopedia than defend a planet, and an Anacreonian fleet on the way.  His
only weapons are politics, atomic power, and the fact that the other side has
already accepted his religion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..model import Exit, NPC, Object, Room, World

if TYPE_CHECKING:  # pragma: no cover
    from ..engine import Game


def _norm(text: str) -> str:
    return " ".join(text.lower().replace("\u2019", "'").split()).strip(" .!")


# ---------------------------------------------------------------------------
# Mayor's office
# ---------------------------------------------------------------------------

def ultimatum_read(g: "Game", obj: Object) -> None:
    g.award_once("ultimatum", 5, "Read the Anacreon ultimatum. It is rude in three languages.")
    g.set_flag("ultimatum_read")
    g.unlock_guide("TERMINUS")
    return None


def logic_read(g: "Game", obj: Object) -> None:
    g.award_once("logic", 5, "Symbolic logic: the only branch of mathematics with a survival instinct.")
    g.set_flag("logic_read")
    return None


def motto_read(g: "Game", obj: Object) -> None:
    g.say(
        g.ui.cyan(
            "VIOLENCE IS THE LAST REFUGE OF THE INCOMPETENT.\n"
            "    — Salvor Hardin, Mayor of Terminus"
        )
    )
    g.say(
        g.ui.dim(
            "Beneath the motto, in smaller letters: THIS SIGN HAS BEEN STOLEN "
            "TWICE. THE MAYOR CONSIDERS THIS A COMPLIMENT."
        )
    )
    return True


def notebook_read(g: "Game", obj: Object) -> None:
    g.say(
        g.ui.dim(
            "The notebook contains three columns headed THINGS TO DO, THINGS "
            "THE BOARD WILL NEVER DO, and THINGS THAT WILL ANNOY PIRENNE. The "
            "third column is full. The first column has one entry: WIN."
        )
    )
    return True


def lee_talk(g: "Game", npc: NPC) -> bool | None:
    if not g.has("lee_talked"):
        g.set_flag("lee_talked")
        g.say(
            "Yohan Lee is a broad, patient man with the expression of someone who "
            "has spent forty years guarding a politician from his own cleverness. "
            "He does not look impressed by the ultimatum. He has looked at worse."
        )
        g.say(
            "'One week,' Lee says. 'The Board wants to wait for the Vault. "
            "Pirenne wants to file a protest. The Anacreonians want the planet. "
            "I want lunch. Which of these do you intend to solve first?'"
        )
    return True


def lee_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("board", "pirenne", "trustees", "council"):
        g.say(
            "'Pirenne has the Vault key. He also has the Board, the Encyclopedia, "
            "and a deeply held belief that the Empire will send a policeman if we "
            "ask nicely. Show him something he cannot argue with. That means your "
            "logic sheets, not your charm.'"
        )
        return True
    if text in ("anacreon", "fleet", "wienis", "rodric"):
        g.say(
            "'Haut Rodric is at the landing pad, pretending to be an ambassador "
            "and not a scout. He drinks anything that is not nailed down. If you "
            "want to know what the flagship can do, ask him after the second glass.'"
        )
        return True
    if text in ("vault", "seldon", "time vault"):
        g.say(
            "'The Vault opens when the Board decides it is politically useful. "
            "Pirenne controls the key. Fara controls the schedule. The rest of us "
            "control the exits, if it comes to that.'"
        )
        return True
    if text in ("religion", "temple", "verisof", "aporat"):
        g.say(
            "'Verisof is back from Anacreon. He has been high priest there for "
            "fourteen years, which means he knows every ritual, every priest, and "
            "every way a navy can be cursed. He also knows Aporat, which is more "
            "useful.'"
        )
        return True
    if text in ("plan", "crisis", "advice"):
        g.say(
            "'You want advice? Do not fight the fleet. Make the fleet irrelevant. "
            "Anacreon cannot run its power plants without our technicians. Their "
            "priests know the prayers, not the physics. Find a way to remind them "
            "of that at the worst possible moment for Wienis.'"
        )
        return True
    return None


# ---------------------------------------------------------------------------
# Council chamber
# ---------------------------------------------------------------------------

def pirenne_show(g: "Game", npc: NPC, obj: Object) -> bool | None:
    if obj.key != "logic_sheets":
        return None
    if not g.has("logic_read"):
        g.say(
            "Pirenne takes the sheets, turns them over, and hands them back. "
            "'You expect me to read an analysis you have not read yourself? "
            "The Board may be doomed, Mayor, but it is not illiterate.'"
        )
        return True
    if g.has("board_convinced"):
        g.say(
            "Pirenne has already given you the Vault key. He is now pretending he "
            "did not, for the sake of his professional dignity."
        )
        return True
    g.set_flag("board_convinced")
    g.state.obj_loc["vault_key"] = "player"
    g.award_once("pirenne", 10, "The Board of Trustees admitted the obvious. Miracles do occur.")
    g.unlock_guide("THE PLAN")
    g.say(
        "Pirenne reads the analysis twice. His face performs a brief civil war "
        "between dignity and arithmetic. Arithmetic wins."
    )
    g.say(
        "'The treaty gives Anacreon independence and leaves the Empire with no "
        "powers of enforcement,' he says. 'And the ultimatum is therefore...' "
        "He cannot finish."
    )
    g.say(
        "'Real,' you say. 'It is real, it is due in a week, and the Empire is not "
        "coming. We can wait for the Vault, or we can govern.'"
    )
    g.say(
        "Pirenne removed a small key from his pocket and placed it on the table "
        "with the care of a man surrendering a relic. 'The Vault is yours, Mayor. "
        "Try not to make it a campaign rally.'"
    )
    g.say("He gives you the Vault key.")
    return True


def pirenne_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("vault", "seldon", "time vault"):
        g.say(
            "'The Vault is a scientific instrument, not a fortune-telling booth. "
            "It opens at the fiftieth anniversary. I have the key. I do not have "
            "the slightest intention of consulting it before the Board has "
            "completed its deliberations.'"
        )
        return True
    if text in ("anacreon", "ultimatum", "war", "fleet"):
        g.say(
            "'The Empire will not allow a provincial kingdom to annex an Imperial "
            "charter world. I have sent a strongly worded protest through the "
            "proper channels. It will arrive after the fleet, but it will arrive.'"
        )
        return True
    if text in ("board", "encyclopedia", "duty"):
        g.say(
            "'The Encyclopedia is the greatest scientific project in history. "
            "Everything else is politics, and politics is what happens while "
            "scientists are editing footnotes.'"
        )
        return True
    return None


def sutt_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("anacreon", "fleet", "war"):
        g.say(
            "Tomaz Sutt stares at the ceiling. 'We have no metals, no fleet, and "
            "no army. We have a printing press and a very good index. The "
            "Anacreonians have a navy. I have considered the strategic situation "
            "from every angle, and the angle I keep returning to is surrender.'"
        )
        return True
    if text in ("vault", "seldon", "fara"):
        g.say(
            "'Fara thinks the Vault will solve everything. Fara also thinks the "
            "proper way to end a sentence is with a subordinate clause. I would "
            "not rely on either.'"
        )
        return True
    return None


def fara_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("vault", "seldon", "time vault"):
        g.say(
            "Jord Fara smiles with the serenity of a man who has read the minutes "
            "of the universe. 'The Vault opens at the anniversary. Hari Seldon "
            "knew we would need him. It is all a question of trusting the Plan.'"
        )
        return True
    if text in ("hardin", "mayor", "politics"):
        g.say(
            "'Mayor Hardin is a clever man with a talent for making cleverness "
            "look like common sense. The Board has decided to be patient with him. "
            "Patience is a virtue. So is a locked door.'"
        )
        return True
    return None


# ---------------------------------------------------------------------------
# City square
# ---------------------------------------------------------------------------

def newspaper_read(g: "Game", obj: Object) -> None:
    g.award_once("newspaper", 3, "Read the Terminus City Journal. Journalism survives the Empire.")
    g.set_flag("newspaper_read")
    return None


def seldon_statue_read(g: "Game", obj: Object) -> None:
    g.say(
        "The statue is newer than the ones on Trantor and considerably less "
        "confident. Hari Seldon sits in a wheelchair, hands folded over a book, "
        "looking slightly surprised to have been cast in bronze."
    )
    g.say(
        "The inscription reads: HARI SELDON — FOUNDER. Beneath that, in letters "
        "added later by the City Council: HE DID THE MATH. Beneath that, in "
        "different letters: PLEASE DO NOT CLIMB."
    )
    return True


def sermak_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("anacreon", "war", "fleet", "appeasement"):
        g.say(
            "Sef Sermak is young, angry, and careful with his anger. 'You have "
            "spent thirty years giving nuclear power to our enemies and calling "
            "it diplomacy. Now their navy is at our door and you want to give "
            "them a reception.'"
        )
        g.say(
            "'I am not asking you to attack first. I am asking you to stop "
            "pretending that the wolf will become a vegetarian if we improve the "
            "menu.'"
        )
        return True
    if text in ("hardin", "mayor"):
        g.say(
            "'Hardin is the most dangerous kind of politician: one who is usually "
            "right. It makes him insufferable. It does not make him wrong.'"
        )
        return True
    if text in ("election", "council", "party"):
        g.say(
            "'The next election will happen whether you win this crisis or not. "
            "That is the difference between us, Mayor. I believe in politics after "
            "the emergency. You believe in the emergency after politics.'"
        )
        return True
    return None


# ---------------------------------------------------------------------------
# Power plant and workshop
# ---------------------------------------------------------------------------

def reactor_manual_read(g: "Game", obj: Object) -> None:
    g.award_once("reactor_manual", 2, "Read the reactor manual. Knowledge is power, and power is voltage.")
    g.set_flag("reactor_manual_read")
    return None


def power_cell_take(g: "Game", obj: Object) -> None:
    g.award_once("power_cell", 3, "A spare power cell. Heavy, glowing, and full of opinions.")
    g.say(
        "You lift the power cell out of its foam cradle. It is warm, heavy, and "
        "emits a low hum that sounds like a committee approving its own minutes."
    )
    return None


def waveguide_take(g: "Game", obj: Object) -> None:
    g.award_once("waveguide", 3, "A waveguide: the plumbing of the electromagnetic spectrum.")
    g.say(
        "The waveguide is a length of precision tubing with connectors at both "
        "ends and a warning label that says DO NOT BEND. Someone has bent it, "
        "then carefully bent it back."
    )
    return None


def reactor_use(g: "Game", obj: Object, target: object) -> bool:
    g.say(
        "The reactor is sealed, shielded, and monitored by three separate "
        "bureaucracies. The Guide recommends not opening it unless you have a "
        "spare planet."
    )
    return True


def control_console_use(g: "Game", obj: Object, target: object) -> bool:
    g.say(
        "The console reports: REACTOR OUTPUT NOMINAL. CITY LOAD NOMINAL. "
        "POLITICAL STABILITY: SEE ATTACHED REPORT. The attached report is blank."
    )
    return True


# ---------------------------------------------------------------------------
# Temple
# ---------------------------------------------------------------------------

def verisof_talk(g: "Game", npc: NPC) -> bool:
    if not g.has("verisof_met"):
        g.set_flag("verisof_met")
        g.award_once("verisof", 5, "Poly Verisof explained the religion of science. It works.")
        g.unlock_guide("RELIGION OF SCIENCE")
        g.say(
            "Poly Verisof looks like a high priest who has spent fourteen years "
            "pretending to be one. His crimson robe is immaculate. His expression "
            "is that of a man who has just discovered that the holiday is over."
        )
        g.say(
            "'You have one week,' he says. 'Wienis will land, demand your "
            "surrender, and then discover that his fleet cannot fire a shot "
            "without a Foundation technician. That is the theory. The practice "
            "requires a hyperwave relay, a very old curse, and a priest with "
            "better timing than Wienis.'"
        )
    if g.has("plan_known") and not g.has("cipher_received"):
        if g.is_carried("vault_key"):
            g.set_flag("cipher_received")
            g.state.obj_loc["cipher"] = "player"
            g.unlock_guide("RELIGION OF SCIENCE")
            g.say(
                "Verisof takes the Vault key, weighs it in his hand, and nods. "
                "'Seldon's blessing and the Board's key. That is enough authority "
                "for a curse, even in a secular century.'"
            )
            g.say(
                "He produces a thin strip of silver foil covered in tiny writing. "
                "'The liturgy of the hyperwave. Aporat knows the response. Get it "
                "to the relay in the sanctuary, and make sure the flagship is "
                "listening.'"
            )
            g.say("He gives you the cipher.")
        else:
            g.say(
                "Verisof frowns. 'Seldon's message is not enough. I need the "
                "Board's key, or at least the Board's frightened cooperation. "
                "Bring me proof that the Vault has opened for you.'"
            )
    return True


def verisof_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("religion", "science", "faith", "church"):
        g.say(
            "'The religion of science is a machine for making barbarians accept "
            "reality. It has candles because candles are cheap. It has rituals "
            "because rituals are memorable. It has priests because someone has to "
            "keep the reactor running on Sunday.'"
        )
        return True
    if text in ("relay", "hyperwave", "sanctuary"):
        g.say(
            "'The Prayer Engine in the sanctuary is a hyperwave relay with a "
            "decorative housing. It needs a waveguide, a power cell, the current "
            "fleet frequency, and a litany. The first two are in the power plant. "
            "The frequency is in Haut Rodric's head or his pockets. The litany is "
            "in Aporat's conscience.'"
        )
        return True
    if text in ("aporat", "theo", "priest"):
        g.say(
            "'Theo Aporat is the highest-ranking priest in the Anacreonian navy. "
            "He has seen the curse work. He has also seen what happens when it "
            "does not. Convince him that the fleet will be dark and he will speak "
            "the words that make it so.'"
        )
        return True
    if text in ("wienis", "anacreon", "fleet", "rodric"):
        g.say(
            "'Wienis is a fool with a navy and a nephew on a throne. Haut Rodric "
            "is his scout, his ambassador, and his drinking problem. The fleet is "
            "called the Wienis, which tells you everything about the prince's "
            "modesty.'"
        )
        return True
    return None


def aporat_talk(g: "Game", npc: NPC) -> bool:
    if not g.has("plan_known"):
        g.say(
            "Theo Aporat regards you with the wary contempt of a priest who has "
            "been sent to inspect a rival temple. 'You are the mayor,' he says. "
            "'You are also, I am told, a mathematician. The fleet is not impressed "
            "by arithmetic.'"
        )
        return True
    if not g.has("cipher_received"):
        g.say(
            "Aporat watches Verisof's silver foil disappear into your pocket. "
            "'You have the words but not the authority,' he says. 'Bring me the "
            "cipher and the assurance that the fleet will listen.'"
        )
        return True
    if not g.has("aporat_ready"):
        g.set_flag("aporat_ready")
        g.say(
            "Aporat is silent for a long moment. Then he looks at the Prayer "
            "Engine, and at the candles, and at the small ordinary door that leads "
            "back to the city."
        )
        g.say(
            "'I have blessed ships that were about to burn cities,' he says. "
            "'I have told dying men that the atoms would receive them. I have "
            "never once been asked whether the atoms were listening.'"
        )
        g.say(
            "He takes the cipher from you and reads it. 'When the relay opens, I "
            "will speak the curse. Not for you. For every priest who has ever "
            "pretended that a power plant is a god. The god is a machine. The "
            "machine answers to us.'"
        )
        g.say("Aporat stands beside the Prayer Engine. He is ready.")
        return True
    g.say(
        "Aporat is praying quietly beside the relay. The prayer sounds suspiciously "
        "like a checklist."
    )
    return True


def aporat_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("curse", "litany", "religion"):
        g.say(
            "'A curse is a technical instruction with better staging,' Aporat "
            "says. 'The hyperwave carries the command. The priests supply the "
            "fear. The machine supplies the darkness. It is the only theology I "
            "have ever seen work reliably.'"
        )
        return True
    if text in ("wienis", "fleet", "anacreon"):
        g.say(
            "'Wienis believes the fleet is his. The fleet believes it belongs to "
            "Anacreon. The engineers believe it belongs to the Foundation. In "
            "practice, it belongs to whoever controls the relay.'"
        )
        return True
    return None


def relay_use(g: "Game", obj: Object, target: object) -> bool:
    key = getattr(target, "key", None) if target is not None else None

    if key == "waveguide":
        if g.has("waveguide_installed"):
            g.say("The waveguide is already connected.")
            return True
        g.set_flag("waveguide_installed")
        g.state.obj_loc["waveguide"] = "relay"
        g.award_once("install_waveguide", 3, "Connected the waveguide. The Prayer Engine now has a throat.")
        g.say(
            "You fit the waveguide into the back of the Prayer Engine. It clicks "
            "into place with the sound of a machine accepting a new doctrine."
        )
        return True

    if key == "power_cell":
        if g.has("cell_installed"):
            g.say("The power cell is already installed.")
            return True
        if not (g.is_carried("towel") or "towel" in g.state.obj_worn):
            g.say(
                "You reach for the relay's bare power coupling and think better of "
                "it. The casing is live. You need insulation. A towel would do."
            )
            return True
        g.set_flag("cell_installed")
        g.state.obj_loc["power_cell"] = "relay"
        g.award_once("install_cell", 3, "Installed the power cell without electrocuting anyone. A triumph.")
        g.say(
            "You wrap the towel around your hands, seat the power cell in its "
            "cradle, and feel the relay come alive. The candles flicker. Somewhere "
            "a choir begins a hymn in a key that was not entirely approved by the "
            "Building Safety Commission."
        )
        return True

    if key == "frequency_card":
        if g.has("frequency_installed"):
            g.say("The fleet frequency is already tuned.")
            return True
        g.set_flag("frequency_installed")
        g.state.obj_loc["frequency_card"] = "relay"
        g.award_once("install_frequency", 3, "Tuned the relay to the Anacreonian flagship. Long distance charges apply.")
        g.say(
            "You slide the frequency card into the tuning slot. The relay's "
            "indicator turns from a sulky amber to a confident green. According "
            "to the dial, you are now speaking directly to the flagship Wienis."
        )
        return True

    if key == "cipher":
        if g.has("cipher_installed"):
            g.say("The cipher is already loaded.")
            return True
        g.set_flag("cipher_installed")
        g.state.obj_loc["cipher"] = "relay"
        g.say(
            "You feed the cipher into the relay. The silver foil vanishes into a "
            "slot that was designed for exactly this sort of theatrical nonsense. "
            "The litany is loaded."
        )
        return True

    if key is not None:
        g.say(
            "The Prayer Engine does not accept that component. It is a hyperwave "
            "relay, not a suggestion box."
        )
        return True

    # USE RELAY
    if g.has("fleet_disabled"):
        g.say(
            "The relay hums with a satisfied green light. The Anacreonian fleet "
            "remains dark. Somewhere, a prince is composing a complaint."
        )
        return True
    missing: list[str] = []
    if not g.has("waveguide_installed"):
        missing.append("the waveguide")
    if not g.has("cell_installed"):
        missing.append("the power cell")
    if not g.has("frequency_installed"):
        missing.append("the fleet frequency card")
    if not g.has("cipher_installed"):
        missing.append("the cipher")
    if not g.has("plan_known"):
        missing.append("a reason to believe this will work")
    if not g.has("aporat_ready"):
        missing.append("a priest willing to speak the curse")
    if missing:
        g.say("The Prayer Engine is not ready. It still needs " + ", ".join(missing) + ".")
        return True

    g.set_flag("fleet_disabled")
    g.award_once("broadcast", 20, "The curse of Aporat, broadcast on a Foundation hyperwave. The religion of science works.")
    g.unlock_guide("RELIGION OF SCIENCE")
    g.unlock_guide("ATOMICS")
    g.achievement("THE FIRST CRISIS")
    g.say(
        "Aporat places both hands on the Prayer Engine. Verisof opens the relay. "
        "The candles go out one by one, not blown out, but swallowed."
    )
    g.say(
        "Somewhere above Terminus, aboard the flagship Wienis, every light in the "
        "fleet goes dark. The engines sigh and stop. The guns retract. The "
        "navigation screens display a single line of text in the Foundation's "
        "old liturgical font: THE POWER IS WITHDRAWN UNTIL THE FAITH IS RESTORED."
    )
    g.say(
        "On the bridge, four hundred Anacreonian officers discover that they have "
        "become passengers. In the temples of three kingdoms, priests begin to "
        "explain, very carefully, that this was always a possibility."
    )
    g.say(
        "Aporat steps back from the relay. His hands are shaking. 'It works,' he "
        "says. 'I hate that it works.'"
    )
    g.say(
        "The first crisis is over. The fleet is dark, and Wienis is waiting at the "
        "landing pad with a treaty he no longer has the power to enforce."
    )
    return True


# ---------------------------------------------------------------------------
# Time Vault
# ---------------------------------------------------------------------------

def vault_enter(g: "Game", first: bool) -> None:
    if g.has("plan_known"):
        g.say("The Vault is empty now. The glass cubicle reflects your own face and a future you have already begun.")
        return
    g.set_flag("plan_known")
    g.award_once("vault", 10, "Hari Seldon explained the Plan. Again. He is very good at it.")
    g.unlock_guide("THE PLAN")
    g.unlock_guide("RELIGION OF SCIENCE")
    g.unlock_guide("TERMINUS")
    g.say(
        "The lights dim. The glass cubicle fills with a figure in a wheelchair, "
        "holding a book that is no longer there."
    )
    g.say(
        "'I am Hari Seldon,' says the figure. 'You are the Mayor of Terminus, or "
        "you are about to be. I cannot see you, so I will assume you are whoever "
        "the Board is currently trying to arrest. That is usually the person who "
        "matters.'"
    )
    g.say(
        "'The Encyclopedia was a fraud. You know that. What you may not know is "
        "that the fraud was necessary. The first crisis is not a fleet. It is a "
        "choice between force and influence. You have no fleet. You have "
        "influence. Use it.'"
    )
    g.say(
        "'Anacreon's navy runs on our technicians and its crews pray to our "
        "priests. The flagship carries a hyperwave relay we installed for exactly "
        "this moment. Find the relay in the temple. Find the priest who has the "
        "courage to curse his own fleet. Broadcast the litany at the right "
        "moment, and the fleet will go dark.'"
    )
    g.say(
        "'Do not mistake this for a victory of faith. It is a victory of "
        "infrastructure. The religion is the packaging. The power plant is the "
        "product. And the price, Mayor, is that you will have to keep selling it.'"
    )
    g.say(
        "'The first crisis will pass. There will be others. There will be a "
        "mayor after you, and a merchant after him, and a Mule after all of us. "
        "Do not let the Plan become a religion. That is my job.'"
    )
    g.say("The image fades. The lights come back up, slightly embarrassed.")


def vault_door_open(g: "Game", obj: Object) -> bool | None:
    if g.state.obj_locked.get("vault_door", True):
        g.say(
            "The Vault door is sealed by a lock older than the city and newer than "
            "the Empire's sense of humour. It needs the Board's key."
        )
        return True
    g.say(
        "The Vault door slides open with a sound like a library clearing its "
        "throat. Cold blue light spills into the vestry."
    )
    return True


# ---------------------------------------------------------------------------
# Landing pad
# ---------------------------------------------------------------------------

def rodric_talk(g: "Game", npc: NPC) -> bool:
    if g.has("rodric_bribed"):
        g.say(
            "Haut Rodric is considerably less impressive with whiskey in him. He "
            "is telling a nearby flagpole about his military career. The flagpole "
            "is winning."
        )
    else:
        g.say(
            "Anselm haut Rodric is a broad, polished man with a smile that has "
            "been rehearsed in front of a mirror and a uniform that has been "
            "pressed by someone who fears him."
        )
        g.say(
            "'Mayor Hardin,' he says. 'I bring greetings from His Puissant Majesty "
            "the King of Anacreon, who is very much looking forward to owning your "
            "planet. I am told the weather is dreadful. I shall improve it with "
            "central heating.'"
        )
    return True


def rodric_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("fleet", "flagship", "wienis", "navy"):
        if g.has("rodric_bribed"):
            g.say(
                "'The flagship is the Wienis. Prince Wienis named it after himself. "
                "He wanted to name the entire navy after himself, but the admiral "
                "objected and was promoted to a very distant sector.'"
            )
        else:
            g.say(
                "'The fleet is the finest in the Periphery. The flagship is the "
                "Wienis, named for our beloved Prince Regent. It can reduce a "
                "planet to gravel in an afternoon. Would you like a brochure?'"
            )
        return True
    if text in ("relay", "hyperwave", "religion", "priest"):
        if g.has("rodric_bribed"):
            g.say(
                "'The Foundation installed a hyperwave relay on the flagship. "
                "Official reason: fleet communications. Actual reason: the priests "
                "insisted. The thing has a direct line to your temple, and I have "
                "the current frequency in my pocket. Or I did before the whiskey.'"
            )
        else:
            g.say(
                "'The priests have their rituals. We have the guns. The two "
                "arrangements coexist because neither side has yet found a "
                "convenient excuse to end them.'"
            )
        return True
    if text in ("treaty", "surrender", "terms"):
        g.say(
            "'Terms are simple. Terminus becomes an Anacreonian protectorate. Your "
            "mayor becomes a governor. Your Board becomes a museum. Your priests "
            "keep their candles. Everyone who cooperates gets a title, and everyone "
            "who does not gets a very small grave.'"
        )
        return True
    return None


def rodric_give(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key != "whiskey":
        g.say(
            "Rodric examines the offered object with a professional eye and "
            "returns it. 'I have a rule,' he says. 'Never accept a gift from a "
            "politician unless it is drinkable.'"
        )
        return True
    if g.has("rodric_bribed"):
        g.say("Rodric has already had quite enough. He is now explaining the balance of power to a chair.")
        return True
    g.state.obj_loc["whiskey"] = None
    g.set_flag("rodric_bribed")
    g.state.obj_loc["frequency_card"] = "player"
    g.award_once("rodric", 5, "Bribed an Anacreonian envoy with whiskey. Diplomacy, Foundation style.")
    g.say(
        "Rodric takes the bottle, checks the label, and decides that the label is "
        "close enough to a friend. Two glasses later he is telling you things he "
        "would not tell his prince."
    )
    g.say(
        "'The flagship's hyperwave relay,' he says, tapping his nose with the "
        "wrong end of the glass. 'Foundation-installed. Current frequency card is "
        "in my pocket. I was supposed to keep it secret. I was also supposed to "
        "keep this bottle secret. One of us has failed.'"
    )
    g.say("He hands you the frequency card and pours another glass. 'Do not tell Wienis. He has no sense of humour about communications security.'")
    return True


def wienis_talk(g: "Game", npc: NPC) -> bool:
    if g.has("fleet_disabled"):
        g.set_flag("wienis_confronted")
        g.say(
            "Prince Regent Wienis is standing at the landing pad with two guards, "
            "a treaty, and the expression of a man whose entire navy has just "
            "failed to return his calls."
        )
        g.say(
            "'What have you done?' he demands. 'The fleet is dark. The priests are "
            "singing. My admiral is asking whether the warranty covers divine "
            "intervention.'"
        )
        g.say(
            "He throws the treaty on the table. 'What do you want, Hardin? Money? "
            "Recognition? A larger office? Everyone wants something. Name it.'"
        )
        g.say(
            "The Guide notes that this is the moment where a mayor becomes a "
            "founder. Two answers are possible, and both of them work: say FAITH, "
            "or say TRADE."
        )
    else:
        g.say(
            "Prince Regent Wienis does not offer you a chair. He stands at the "
            "landing pad in a coat worth more than the city budget, flanked by "
            "guards and backed by a fleet you cannot see."
        )
        g.say(
            "'Mayor Hardin. You have one week. I am told you are a man who likes "
            "to talk. I am a man who likes to acquire. We can do both, but only "
            "one of us will enjoy it.'"
        )
        g.say(
            "He gestures at the treaty on the table. 'Sign, and Terminus becomes a "
            "protectorate. Refuse, and it becomes a lesson. I am told the weather "
            "is better after the lesson.'"
        )
    return True


def wienis_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("fleet", "navy", "flagship", "relay"):
        if g.has("fleet_disabled"):
            g.say(
                "'The fleet is dark,' Wienis says, through his teeth. 'The relay "
                "is yours. The priests are yours. The technicians are yours. I am "
                "beginning to think the planet was not the prize.'"
            )
        else:
            g.say(
                "'The fleet is the finest in the Periphery. It carries enough "
                "nuclear firepower to make Terminus a memory and enough priests to "
                "bless the memory afterward. I consider this a complete strategic "
                "package.'"
            )
        return True
    if text in ("treaty", "terms", "surrender"):
        g.say(
            "'The treaty is generous. You keep your city, your Council, your "
            "precious Encyclopedia. You lose only the right to make decisions. "
            "Many governors have found this arrangement quite comfortable.'"
        )
        return True
    if text in ("religion", "priests", "aporat", "verisof"):
        g.say(
            "'The priests are useful. They keep the workers calm and the navy "
            "blessed. When they become inconvenient, they discover that even a "
            "high priest can be transferred to a very small temple on a very cold "
            "moon.'"
        )
        return True
    return None


def wienis_attack(g: "Game", npc: NPC) -> bool:
    g.death(
        "You strike Prince Wienis. His guards are professional, the treaty table "
        "is heavy, and the lesson is brief. The Guide notes that violence was, "
        "once again, the last refuge of the incompetent."
    )
    return True


def finish_doctrine(g: "Game", doctrine: str) -> bool:
    if g.has("doctrine_done"):
        g.say("The choice has already been made. History is many things, but it is not indecisive.")
        return True
    g.set_flag("doctrine_done")
    g.meta.doctrine = doctrine
    g.meta.ending = "act2_" + doctrine
    g.award_once("doctrine", 20, "Chose what the Foundation will become. The Guide takes notes.")
    g.unlock_guide("RELIGION OF SCIENCE")
    g.unlock_guide("THE PLAN")

    if doctrine == "faith":
        g.achievement("THE PROPHET OF TERMINUS")
        g.say(
            "You choose the religion of science. Not as a trick this time, but as "
            "a policy. The Four Kingdoms will keep their temples, their candles, "
            "and their prayers. They will also keep their Foundation-trained "
            "priests, their Foundation-maintained reactors, and their quiet "
            "understanding that the machine is the god and the god has a service "
            "contract."
        )
        g.say(
            "Wienis stares at you. 'You would rule through priests?' he says. "
            "'That is not government. That is theatre.'"
        )
        g.say(
            "'It is both,' you say. 'The difference is which one you can repair.'"
        )
        g.say(
            "The treaty is rewritten on the landing pad, in front of the guards, "
            "the priests, and a newspaper reporter who has been hiding behind the "
            "flag. Anacreon keeps its king, its fleet, and its dignity. The "
            "Foundation keeps the power. The religion of science becomes the "
            "Foundation's first empire, and Salvor Hardin becomes its first saint, "
            "whether he likes it or not."
        )
    else:
        g.achievement("THE MERCHANT OF TERMINUS")
        g.say(
            "You choose trade. The treaty is torn up and replaced with a commercial "
            "agreement so complicated that the Anacreonian lawyers need three days "
            "and two translators to realize they have lost."
        )
        g.say(
            "Terminus will repair the fleets, supply the power cells, train the "
            "technicians, and sell the Four Kingdoms the medicines that keep their "
            "princes alive. The Foundation will become too useful to conquer and "
            "too expensive to ignore."
        )
        g.say(
            "Wienis reads the agreement twice. 'This is not a victory,' he says. "
            "'It is an invoice.'"
        )
        g.say(
            "'The invoice is the victory,' you say. 'Collecting is the politics.'"
        )
        g.say(
            "The religion of science remains, because people need rituals, but it "
            "is no longer the only bridge between Terminus and the kingdoms. There "
            "is also commerce, which is older, quieter, and considerably harder to "
            "excommunicate. Hardin signs the last page, orders a shipment of "
            "textbooks, and goes home to a city that has not been invaded."
        )

    g.say(
        "The first crisis is over. The Foundation has survived by being more "
        "useful than dangerous, which is the one kind of survival the Guide "
        "considers stylish."
    )
    g.finish_act()
    return True


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------

def act2_hints(g: "Game") -> str:
    room = g.room().key
    if not g.has("ultimatum_read"):
        return "There is an ultimatum on your desk. READ ULTIMATUM before the week gets shorter."
    if not g.has("logic_read"):
        return "The symbolic analysis on your desk is your only argument. READ LOGIC SHEETS."
    if not g.has("board_convinced"):
        return "Take the logic sheets to Pirenne in the council chamber. SHOW LOGIC SHEETS TO PIRENNE."
    if not g.has("plan_known"):
        return "The Vault key opens the door in the temple vestry. GO VAULT and let Seldon explain."
    if not g.has("cipher_received"):
        return "Talk to Verisof in the temple again. He has a litany and a very low opinion of Wienis."
    if not g.has("rodric_bribed"):
        return "Haut Rodric at the landing pad likes whiskey. The mayor's cabinet contains some. GIVE WHISKEY TO RODRIC."
    if not g.has("aporat_ready"):
        return "Theo Aporat is in the temple. TALK TO APORAT after you have the cipher. He needs to choose a side."
    if not g.has("power_cell"):
        return "Open the supply crate in the power plant and TAKE POWER CELL. Read the manual if you want points for prudence."
    if not g.has("waveguide"):
        return "The waveguide is on the workbench in the workshop south of the power plant."
    if not g.has("waveguide_installed"):
        return "Install the waveguide: USE WAVEGUIDE ON RELAY in the temple."
    if not g.has("cell_installed"):
        return "Install the power cell: USE POWER CELL ON RELAY. Keep your towel on; the casing is live."
    if not g.has("frequency_installed"):
        return "Tune the relay: USE FREQUENCY CARD ON RELAY."
    if not g.has("cipher_installed"):
        return "Load the litany: USE CIPHER ON RELAY."
    if not g.has("fleet_disabled"):
        return "Everything is ready. USE RELAY, then watch the fleet discover infrastructure."
    if room == "landing_pad":
        return "Wienis is waiting. TALK TO WIENIS, then SAY FAITH or SAY TRADE to decide how the Foundation will rule."
    return "The fleet is dark. Go south to the landing pad and tell Wienis what the Foundation will become."


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------

def act2_on_say(g: "Game", text: str) -> bool | None:
    if g.room().key != "landing_pad" or not g.has("fleet_disabled"):
        return None
    low = _norm(text)
    if low in (
        "faith",
        "religion",
        "the religion of science",
        "religion of science",
        "the faith",
        "priest",
        "priests",
    ):
        return finish_doctrine(g, "faith")
    if low in (
        "trade",
        "commerce",
        "merchant",
        "merchants",
        "science",
        "reason",
        "trade and science",
        "business",
    ):
        return finish_doctrine(g, "trade")
    if low in ("the fleet is dark", "fleet is dark", "your fleet is dark"):
        g.say(
            "Wienis flinches. Behind him, the flagship's running lights are still "
            "out. The guards have begun to look at their own boots, as if checking "
            "whether the ground is still loyal."
        )
        g.say("'Choose,' Wienis says. 'Faith or trade. Every empire begins with one of them.'")
        return True
    return None


def build() -> World:
    rooms: dict[str, Room] = {
        "mayor_office": Room(
            key="mayor_office",
            name="Mayor's Office, City Hall",
            desc=(
                "City Hall is a squat, honest building with delusions of grandeur "
                "and a heating system that has never shared those delusions. Your "
                "office occupies the corner with the best window and the worst "
                "furniture.\n\n"
                "On the desk sits the Anacreon ultimatum, a set of symbolic-logic "
                "sheets, and a cold cup of coffee. On the wall, framed in cheap "
                "metal, is the motto that has followed you through every election: "
                "VIOLENCE IS THE LAST REFUGE OF THE INCOMPETENT.\n\n"
                "Through the east door, the Board of Trustees is pretending to "
                "govern. Through the south door, Terminus is waiting to find out "
                "whether you can."
            ),
            brief="The mayor's office: one desk, one crisis, one framed motto.",
            coords=(0, 0),
            map_label="Office",
            exits={
                "east": Exit(dest="council_chamber", label="council chamber"),
                "south": Exit(dest="city_square", label="city square"),
            },
        ),
        "council_chamber": Room(
            key="council_chamber",
            name="Council Chamber of the Board of Trustees",
            desc=(
                "The council chamber is panelled in dark wood and lit by lamps "
                "designed to make every argument look like a formal proceeding. A "
                "long table dominates the room. Five chairs wait behind it; three "
                "of them are currently occupied by people who would rather be "
                "editing something.\n\n"
                "The charter of the Encyclopedia Foundation hangs on the wall, "
                "framed and sealed. It is a beautiful document. It has never "
                "stopped a warship."
            ),
            brief="The Board of Trustees, deliberating at the speed of footnotes.",
            coords=(1, 0),
            map_label="Council",
            exits={"west": Exit(dest="mayor_office", label="mayor's office")},
        ),
        "city_square": Room(
            key="city_square",
            name="Terminus City Square",
            desc=(
                "The square is the closest thing Terminus has to a heart: a wide "
                "paved space surrounded by City Hall, the Temple of the Atom, the "
                "power plant, and a row of shops that sell mostly coffee and "
                "political opinions.\n\n"
                "A statue of Hari Seldon sits in the centre, looking at a book he "
                "no longer holds. A newspaper stand displays the latest edition of "
                "the Terminus City Journal, whose headline is visible from here: "
                "ANACREON DEMANDS SURRENDER — MAYOR PROMISES 'A PROPER REPLY'.\n\n"
                "A road leads south to the landing pad, where an Anacreonian "
                "delegation has been waiting for three days and complaining about "
                "the coffee."
            ),
            brief="Terminus City Square: a statue, a newspaper, and a great deal of nervous optimism.",
            coords=(0, 1),
            map_label="Square",
            exits={
                "north": Exit(dest="mayor_office", label="City Hall"),
                "west": Exit(dest="power_plant", label="power plant"),
                "east": Exit(dest="temple", label="temple"),
                "south": Exit(dest="landing_pad", label="landing pad"),
            },
        ),
        "power_plant": Room(
            key="power_plant",
            name="Terminus Atomic Power Plant",
            desc=(
                "The power plant is the Foundation's real cathedral: a high, clean "
                "cavern of pipes, turbines, and glowing conduits. The reactor sits "
                "behind three layers of shielding and one layer of bureaucracy.\n\n"
                "A supply crate stands near the maintenance bay, its seal intact. "
                "A reactor manual lies open on a console, held down by a wrench "
                "that has been used to settle at least one argument."
            ),
            brief="The atomic plant hums with the confidence of a machine that has never been elected.",
            coords=(-1, 1),
            map_label="Power",
            exits={
                "east": Exit(dest="city_square", label="city square"),
                "south": Exit(dest="workshop", label="workshop"),
            },
        ),
        "workshop": Room(
            key="workshop",
            name="Maintenance Workshop",
            desc=(
                "The workshop smells of solder, ozone, and the kind of optimism that "
                "requires safety goggles. Tools hang from pegboards in descending "
                "order of legality. A workbench occupies the centre of the room, "
                "covered in half-finished devices and fully finished grudges.\n\n"
                "A waveguide lies on the bench beside a coil of wire and a note that "
                "says DO NOT BEND. The waveguide has been bent."
            ),
            brief="A workshop full of tools, spare parts, and unresolved safety warnings.",
            coords=(-1, 2),
            map_label="Workshop",
            exits={"north": Exit(dest="power_plant", label="power plant")},
        ),
        "temple": Room(
            key="temple",
            name="Temple of the Atom",
            desc=(
                "The Temple of the Atom is a converted power station with better "
                "lighting and considerably more incense. Candles line the walls in "
                "holders shaped like atomic orbitals. A stained-glass window depicts "
                "the First Reactor, its control rods raised in benediction.\n\n"
                "At the far end, the altar supports the Prayer Engine: a hyperwave "
                "relay dressed in gold leaf and theology. Poly Verisof stands to one "
                "side, looking as if he has just remembered a very important "
                "appointment. A second priest, darker and more careful, watches from "
                "the shadows.\n\n"
                "A door behind the altar leads to the vestry."
            ),
            brief="Candles, incense, and a hyperwave relay pretending to be holy.",
            coords=(1, 1),
            map_label="Temple",
            exits={
                "west": Exit(dest="city_square", label="city square"),
                "north": Exit(dest="vestry", label="vestry"),
            },
        ),
        "vestry": Room(
            key="vestry",
            name="Temple Vestry",
            desc=(
                "The vestry is a small room behind the sanctuary, hung with spare "
                "robes and the smell of cold candle wax. A ledger on the table "
                "records donations in a hand that grows more optimistic toward the "
                "end of each page.\n\n"
                "The Vault door fills the east wall. It is a slab of dark metal with "
                "no handle, no keyhole, and a small brass plate that reads: THE "
                "VAULT OPENS AT THE APPOINTED TIME. THE APPOINTED TIME IS NOT YOUR "
                "CONCERN."
            ),
            brief="A vestry, a ledger, and a door that has strong opinions about schedules.",
            coords=(1, 2),
            map_label="Vestry",
            exits={
                "south": Exit(dest="temple", label="sanctuary"),
                "vault": Exit(
                    dest="time_vault",
                    label="Vault door",
                    condition=lambda g: not g.state.obj_locked.get("vault_door", True),
                    blocked="The Vault door is sealed. The Board's key should open it.",
                ),
            },
        ),
        "time_vault": Room(
            key="time_vault",
            name="The Time Vault",
            desc=(
                "The Vault is a circular room with a glass cubicle at its centre. "
                "The cubicle is empty. The chairs arranged around it are dusty. The "
                "lights are dim, as if the room is saving power for a very important "
                "appointment.\n\n"
                "On the wall, a plaque reads: HARI SELDON — THE PLAN CONTINUES. "
                "Someone has added, in pencil: PLEASE CONTINUE QUIETLY."
            ),
            brief="An empty glass cubicle and a room built for a voice from the past.",
            coords=(2, 2),
            map_label="Vault",
            on_enter=vault_enter,
            exits={"west": Exit(dest="vestry", label="vestry")},
        ),
        "landing_pad": Room(
            key="landing_pad",
            name="Anacreonian Landing Pad",
            desc=(
                "The landing pad is a flat expanse of reinforced concrete outside "
                "the city, decorated with floodlights, guards, and a ceremonial "
                "red carpet that has been laid down with the confidence of a "
                "conquering army and the corners curled by the wind.\n\n"
                "An Anacreonian courier ship crouches at the edge of the pad, its "
                "engines cold. A treaty table stands beneath a canopy. Prince "
                "Regent Wienis waits beside it, flanked by guards. Haut Rodric "
                "hovers nearby with the expression of a man who has been told to be "
                "diplomatic and has taken it as a personal insult.\n\n"
                "The city lies to the north. The sky is full of things that may or "
                "may not be warships."
            ),
            brief="A red carpet, an Anacreonian prince, and a treaty nobody intends to honour.",
            coords=(0, 2),
            map_label="Landing",
            exits={"north": Exit(dest="city_square", label="city square")},
        ),
    }

    objects: dict[str, Object] = {
        # Starting inventory -------------------------------------------------
        "towel": Object(
            key="towel",
            names=["towel", "guide towel", "my towel"],
            short="towel",
            location="player",
            container=True,
            open=True,
            wearable=True,
            desc=(
                "A large, serviceable towel. The Guide insists it is the most "
                "useful object in the known universe. Today it will be used to "
                "insulate a mayor from a live power coupling, which is not the "
                "advertised use but is certainly in the spirit of the thing."
            ),
        ),
        "mayor_seal": Object(
            key="mayor_seal",
            names=["mayor's seal", "seal", "badge", "chain of office", "mayor badge"],
            short="mayor's seal",
            location="player",
            desc=(
                "The seal of the Mayor of Terminus. It is made of base metal, "
                "engraved with the city's crest, and technically grants you the "
                "authority to do almost anything except raise taxes without a "
                "vote. The Guide considers this an excellent definition of "
                "democracy."
            ),
        ),
        "notebook": Object(
            key="notebook",
            names=["notebook", "notes", "journal"],
            short="notebook",
            location="player",
            readable=True,
            on_read=notebook_read,
            desc="A mayor's notebook, full of plans and the phone numbers of people who owe him favours.",
        ),
        # Mayor's office -----------------------------------------------------
        "desk": Object(
            key="desk",
            names=["desk", "mayor's desk", "table"],
            short="desk",
            location="mayor_office",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "The mayor's desk is scarred by decades of urgent signatures, "
                "coffee cups, and at least one knife thrown in a budget meeting. "
                "It is the most honest piece of furniture in City Hall."
            ),
        ),
        "ultimatum": Object(
            key="ultimatum",
            names=["ultimatum", "message", "note", "anacreon ultimatum", "document"],
            short="Anacreon ultimatum",
            location="mayor_office",
            fixed=True,
            takeable=False,
            readable=(
                "FROM: HIS PUISSANT MAJESTY, THE KING OF ANACREON\n"
                "TO: THE MAYOR AND COUNCIL OF TERMINUS\n\n"
                "It has come to our attention that Terminus persists in existing "
                "within our sphere of influence. We are prepared to overlook this "
                "oversight in exchange for the immediate surrender of the city, "
                "the transfer of all atomic facilities, and the appointment of a "
                "Royal Governor.\n\n"
                "You have one week. We have a fleet. Please choose quickly; the "
                "weather is turning.\n\n"
                "A handwritten note at the bottom reads: THIS IS A FORM LETTER. "
                "THE FLEET IS NOT."
            ),
            on_read=ultimatum_read,
            desc="A crisply printed ultimatum with a very large seal and a very short deadline.",
        ),
        "logic_sheets": Object(
            key="logic_sheets",
            names=["logic sheets", "symbolic logic", "analysis", "sheets", "papers"],
            short="logic sheets",
            location="mayor_office",
            readable=(
                "SYMBOLIC ANALYSIS OF THE ANACREON ULTIMATUM AND THE IMPERIAL TREATY\n\n"
                "1. The treaty imposes no enforceable obligations on Anacreon.\n"
                "2. The Empire retains no powers of enforcement.\n"
                "3. The ultimatum therefore means exactly what it says: surrender "
                "or be annexed.\n"
                "4. The Board's proposed response — a strongly worded protest — has "
                "a predicted effect of zero, with a margin of error of zero.\n\n"
                "A note in the mayor's hand: PIRENNE WILL HATE THIS. SHOW HIM ANYWAY."
            ),
            on_read=logic_read,
            desc="A dense set of symbolic-logic sheets, covered in arrows, brackets, and the mayor's marginal notes.",
        ),
        "cabinet": Object(
            key="cabinet",
            names=["cabinet", "drinks cabinet", "cupboard"],
            short="drinks cabinet",
            location="mayor_office",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A small drinks cabinet. The key is missing, but the lock has been "
                "broken since the previous mayor's farewell party. Inside, a bottle "
                "of something amber waits for diplomacy."
            ),
        ),
        "whiskey": Object(
            key="whiskey",
            names=["whiskey", "whisky", "bottle", "drink", "liquor"],
            short="bottle of whiskey",
            location="cabinet",
            desc=(
                "A bottle of locally distilled whiskey. The label says TERMINUS "
                "RESERVE — AGED THREE WEEKS. Beneath that, in smaller letters: "
                "THE WEEKS WERE VERY LONG."
            ),
        ),
        "motto": Object(
            key="motto",
            names=["motto", "sign", "framed motto", "quote"],
            short="framed motto",
            location="mayor_office",
            fixed=True,
            takeable=False,
            readable=True,
            on_read=motto_read,
            desc="The mayor's framed motto, polished every year and ignored every budget cycle.",
        ),
        # Council chamber ----------------------------------------------------
        "board_table": Object(
            key="board_table",
            names=["table", "board table", "council table"],
            short="council table",
            location="council_chamber",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A long table of dark wood, large enough to seat five trustees, "
                "their egos, and a quorum of their excuses. Someone has carved "
                "THE ENCYCLOPEDIA FIRST into the edge. Someone else has carved "
                "AFTER THE PLANET."
            ),
        ),
        "charter": Object(
            key="charter",
            names=["charter", "foundation charter", "document", "framed charter"],
            short="Foundation charter",
            location="council_chamber",
            fixed=True,
            takeable=False,
            readable=(
                "THE ENCYCLOPEDIA FOUNDATION CHARTER\n\n"
                "The Foundation shall compile the Encyclopedia Galactica for the "
                "glory of the Empire and the preservation of knowledge. The Board "
                "of Trustees shall have full administrative authority over all "
                "Foundation affairs.\n\n"
                "A recent amendment, in different ink, reads: THE MAYOR SHALL HAVE "
                "FULL AUTHORITY OVER ANYTHING THE BOARD HAS NOT YET FINISHED "
                "DISCUSSING. THIS INCLUDES THE EMERGENCY EXITS."
            ),
            desc="The charter of the Encyclopedia Foundation, framed and increasingly irrelevant.",
        ),
        # City square --------------------------------------------------------
        "newspaper": Object(
            key="newspaper",
            names=["newspaper", "journal", "news", "paper", "Terminus City Journal"],
            short="newspaper",
            location="city_square",
            fixed=True,
            takeable=False,
            readable=(
                "THE TERMINUS CITY JOURNAL\n\n"
                "ANACREON DEMANDS SURRENDER — MAYOR PROMISES 'A PROPER REPLY'\n\n"
                "The Royal Navy of Anacreon has been observed conducting exercises "
                "near the Terminus system. Prince Regent Wienis denies that the "
                "exercises are directed at the Foundation, calling them 'a routine "
                "demonstration of affection.'\n\n"
                "In related news, the Temple of the Atom has announced a special "
                "service for the safety of the city. Attendance is mandatory for "
                "all priests and strongly encouraged for everyone who enjoys "
                "electricity.\n\n"
                "Editorial, page 4: WHY THE BOARD SHOULD LET THE MAYOR DO HIS JOB. "
                "Letters, page 5: WHY THE MAYOR SHOULD LET THE BOARD DO ITS JOB."
            ),
            on_read=newspaper_read,
            desc="The latest edition of the Terminus City Journal, folded open to a headline nobody wants to read.",
        ),
        "seldon_statue": Object(
            key="seldon_statue",
            names=["statue", "seldon statue", "monument", "hari seldon"],
            short="statue of Hari Seldon",
            location="city_square",
            fixed=True,
            takeable=False,
            readable=True,
            on_read=seldon_statue_read,
            desc=(
                "A bronze Hari Seldon sits in a wheelchair, looking at a book that "
                "is no longer in his hands. The sculptor gave him a kindly "
                "expression. The pigeons have given him a hat."
            ),
        ),
        # Power plant and workshop -------------------------------------------
        "reactor": Object(
            key="reactor",
            names=["reactor", "atomic reactor", "power plant", "core"],
            short="reactor",
            location="power_plant",
            fixed=True,
            takeable=False,
            on_use=reactor_use,
            desc=(
                "The reactor is a sealed sphere of alloy and shielding, humming "
                "with the controlled enthusiasm of a star that has been persuaded "
                "to take a desk job. Three warning lights blink in a pattern that "
                "means NOMINAL. A fourth light, unlabeled, blinks in a pattern that "
                "means MANAGEMENT."
            ),
        ),
        "reactor_manual": Object(
            key="reactor_manual",
            names=["reactor manual", "manual", "instructions", "book"],
            short="reactor manual",
            location="power_plant",
            fixed=True,
            takeable=False,
            readable=(
                "TERMINUS ATOMIC POWER PLANT — OPERATOR'S MANUAL\n\n"
                "SECTION 12: SPARE POWER CELLS\n"
                "Spare cells are stored in the sealed supply crate. Under no "
                "circumstances should the primary cell be removed while the reactor "
                "is online. Under no circumstances should the spare cell be used to "
                "power unauthorized religious equipment without written permission "
                "from the Mayor.\n\n"
                "A handwritten note in the margin reads: THE MAYOR IS STANDING RIGHT "
                "HERE. PERMISSION GRANTED. — S.H."
            ),
            on_read=reactor_manual_read,
            desc="A thick operator's manual, held open by a wrench and several ominous bookmarks.",
        ),
        "supply_crate": Object(
            key="supply_crate",
            names=["supply crate", "crate", "box"],
            short="supply crate",
            location="power_plant",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A heavy supply crate stamped ATOMIC POWER PLANT — SPARES. The seal "
                "is intact. A smaller label reads: OPEN ONLY IF YOU KNOW WHAT YOU "
                "ARE DOING. A third label, added later, reads: OR IF THE MAYOR SAYS "
                "SO."
            ),
        ),
        "power_cell": Object(
            key="power_cell",
            names=["power cell", "cell", "battery", "atomic cell"],
            short="power cell",
            location="supply_crate",
            on_take=power_cell_take,
            desc=(
                "A sealed atomic power cell about the size of a large book. It is "
                "warm, heavy, and capable of running a small temple for a year. The "
                "warning label says DO NOT DROP. The second warning label says DO "
                "NOT READ THE FIRST WARNING LABEL WHILE HOLDING THE CELL."
            ),
        ),
        "control_console": Object(
            key="control_console",
            names=["console", "control console", "controls", "panel"],
            short="control console",
            location="power_plant",
            fixed=True,
            takeable=False,
            on_use=control_console_use,
            desc="A control console covered in dials, switches, and a small sign that says DO NOT LICK THE CONSOLE.",
        ),
        "workbench": Object(
            key="workbench",
            names=["workbench", "bench", "work table"],
            short="workbench",
            location="workshop",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A workbench scarred by decades of repairs. Someone has soldered "
                "their initials into the corner. Another someone has soldered a "
                "reply. The reply is unprintable."
            ),
        ),
        "waveguide": Object(
            key="waveguide",
            names=["waveguide", "tube", "pipe", "precision tube"],
            short="waveguide",
            location="workshop",
            on_take=waveguide_take,
            desc=(
                "A precision waveguide, about a metre long, with connectors at both "
                "ends. It is designed to carry hyperwave signals with minimal loss. "
                "It has been bent and unbent so many times that it now carries "
                "signals with a slight accent."
            ),
        ),
        "coils": Object(
            key="coils",
            names=["coils", "wire", "spare wire", "cable"],
            short="coils of wire",
            location="workshop",
            fixed=True,
            takeable=False,
            desc="Several coils of wire in different colours, sorted by a system that exists only in the mind of the person who left them.",
        ),
        "tools": Object(
            key="tools",
            names=["tools", "wrench", "screwdriver", "hammer"],
            short="tools",
            location="workshop",
            fixed=True,
            takeable=False,
            desc="A pegboard of tools. Most are where they should be. One is missing, and a small outline on the board has been labelled BORROWED BY THE MAYOR.",
        ),
        # Temple -------------------------------------------------------------
        "altar": Object(
            key="altar",
            names=["altar", "holy table", "sanctuary table"],
            short="altar",
            location="temple",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "The altar is a slab of polished stone covered in candles, "
                "offerings, and a collection plate that has been carefully designed "
                "to look poor."
            ),
        ),
        "relay": Object(
            key="relay",
            names=["relay", "hyperwave relay", "prayer engine", "engine", "holy engine"],
            short="Prayer Engine",
            location="temple",
            fixed=True,
            takeable=False,
            on_use=relay_use,
            on_use_with=relay_use,
            desc=(
                "The Prayer Engine is a hyperwave relay in a gold-leaf housing. Its "
                "control panel is hidden behind a hinged icon of the First Reactor. "
                "A small brass plate reads: SPEAK, AND THE ATOM WILL LISTEN. A "
                "smaller plate, added by a technician, reads: SPEAK CLEARLY. THE "
                "ATOM HAS POOR RECEPTION IN THIS QUADRANT."
            ),
        ),
        "candles": Object(
            key="candles",
            names=["candles", "candle", "lights"],
            short="candles",
            location="temple",
            fixed=True,
            takeable=False,
            desc=(
                "Dozens of candles burn in holders shaped like atomic orbitals. "
                "They are replaced every morning by an acolyte who has been told "
                "the candles are symbolic. The acolyte has also been told not to "
                "let them go out, which suggests the symbolism is load-bearing."
            ),
        ),
        "collection_plate": Object(
            key="collection_plate",
            names=["collection plate", "plate", "offerings"],
            short="collection plate",
            location="temple",
            fixed=True,
            takeable=False,
            desc=(
                "A silver collection plate containing three coins, a button, and a "
                "note that says I O U ONE CONVERSION. The Guide approves of "
                "creative tithing."
            ),
        ),
        "vault_door": Object(
            key="vault_door",
            names=["vault door", "door", "vault"],
            short="Vault door",
            location="vestry",
            fixed=True,
            takeable=False,
            container=True,
            open=False,
            openable=True,
            locked=True,
            unlock_key="vault_key",
            on_open=vault_door_open,
            desc=(
                "A slab of dark metal with no visible handle. A brass plate reads: "
                "THE VAULT OPENS AT THE APPOINTED TIME. Someone has scratched "
                "beneath it: APPOINTED BY WHOM?"
            ),
        ),
        "ledger": Object(
            key="ledger",
            names=["ledger", "book", "accounts"],
            short="ledger",
            location="vestry",
            fixed=True,
            takeable=False,
            readable=(
                "TEMPLE DONATIONS — CURRENT YEAR\n\n"
                "First week: 42 credits, one chicken, two prayers for rain.\n"
                "Second week: 18 credits, one prayer for the rain to stop.\n"
                "Third week: 65 credits, a note asking whether the atom accepts "
                "cheques.\n"
                "Fourth week: 300 credits, anonymous. The handwriting looks "
                "suspiciously like the mayor's."
            ),
            desc="The temple ledger, balanced with faith and creative accounting.",
        ),
        "vestments": Object(
            key="vestments",
            names=["vestments", "robes", "robe", "spare robe"],
            short="spare vestments",
            location="vestry",
            fixed=True,
            takeable=False,
            desc=(
                "Spare crimson robes hang from a rail. They are sized for a high "
                "priest, a visiting dignitary, and, in one optimistic corner, a "
                "very large acolyte."
            ),
        ),
        "vault_plaque": Object(
            key="vault_plaque",
            names=["plaque", "vault plaque", "sign"],
            short="Vault plaque",
            location="time_vault",
            fixed=True,
            takeable=False,
            readable=(
                "HARI SELDON — THE PLAN CONTINUES.\n\n"
                "The Vault was constructed to remind the Foundation that history "
                "is not a sequence of accidents. It is a sequence of decisions, "
                "most of them made by people who did not realize they were making "
                "them.\n\n"
                "PLEASE CONTINUE QUIETLY."
            ),
            desc="A small plaque beside the empty glass cubicle.",
        ),
        "vault_cubicle": Object(
            key="vault_cubicle",
            names=["cubicle", "glass cubicle", "glass box", "vault"],
            short="glass cubicle",
            location="time_vault",
            fixed=True,
            takeable=False,
            desc=(
                "The glass cubicle is empty, but the air inside it is slightly "
                "colder than the rest of the room. The Guide suggests this is "
                "either a scientific phenomenon or a very polite ghost."
            ),
        ),
        # Landing pad --------------------------------------------------------
        "anacreon_ship": Object(
            key="anacreon_ship",
            names=["ship", "courier", "anacreon ship", "courier ship"],
            short="Anacreonian courier",
            location="landing_pad",
            fixed=True,
            takeable=False,
            desc=(
                "A sleek Anacreonian courier with red-and-gold markings and a "
                "gleaming hull. It is the sort of ship designed to make a planet "
                "feel underdressed."
            ),
        ),
        "treaty_table": Object(
            key="treaty_table",
            names=["table", "treaty table", "canopy table"],
            short="treaty table",
            location="landing_pad",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A folding table covered with a white cloth and a treaty document "
                "that has been printed in three languages, none of which contains "
                "the word 'temporary'."
            ),
        ),
        "treaty": Object(
            key="treaty",
            names=["treaty", "agreement", "document", "terms"],
            short="treaty",
            location="landing_pad",
            fixed=True,
            takeable=False,
            readable=(
                "TREATY OF FRIENDSHIP AND PROTECTION\n\n"
                "Article 1: Terminus shall accept the protection of the Kingdom of "
                "Anacreon.\n"
                "Article 2: The Mayor shall be appointed Royal Governor.\n"
                "Article 3: All atomic facilities shall be transferred to the "
                "Crown.\n"
                "Article 4: The Board of Trustees shall retain its ceremonial "
                "functions, including the ceremony of not being consulted.\n\n"
                "The spaces for signatures are blank. A note in the margin reads: "
                "SIGN HERE, HARDIN. THE FLEET IS WAITING."
            ),
            desc="An Anacreonian treaty of 'friendship', already signed by the king and waiting for a mayor.",
        ),
        "flag": Object(
            key="flag",
            names=["flag", "banner", "anacreon flag"],
            short="Anacreonian flag",
            location="landing_pad",
            fixed=True,
            takeable=False,
            desc=(
                "The flag of Anacreon: a red field, a golden sunburst, and a "
                "smaller symbol in the corner that represents either the royal "
                "house or a tax exemption. The wind is not impressed."
            ),
        ),
        # Items given during the act -----------------------------------------
        "vault_key": Object(
            key="vault_key",
            names=["vault key", "key", "board key", "vault_key"],
            short="Vault key",
            location=None,
            desc=(
                "A small key of dark metal, warm from Pirenne's pocket. It opens "
                "the Vault in the temple vestry. It also opens a surprising number "
                "of conversations about the Board's relevance."
            ),
        ),
        "frequency_card": Object(
            key="frequency_card",
            names=["frequency card", "frequency", "card", "relay card"],
            short="frequency card",
            location=None,
            desc=(
                "A thin card bearing the current hyperwave frequency of the "
                "Anacreonian flagship. On the back, in Rodric's handwriting: IF "
                "FOUND, PLEASE RETURN TO THE NEAREST ANACREONIAN AMBASSADOR. DO NOT "
                "LET THE MAYOR SEE IT."
            ),
        ),
        "cipher": Object(
            key="cipher",
            names=["cipher", "litany", "curse", "code", "silver foil"],
            short="cipher",
            location=None,
            desc=(
                "A strip of silver foil covered in tiny writing. It contains the "
                "liturgy of the hyperwave and the curse of Aporat. Reading it aloud "
                "is discouraged in mixed company and encouraged in temples."
            ),
        ),
    }

    npcs: dict[str, NPC] = {
        "lee": NPC(
            key="lee",
            names=["lee", "yohan lee", "yohan", "aides", "aide"],
            short="Yohan Lee",
            location="mayor_office",
            desc=(
                "Yohan Lee is a broad, patient man with the expression of someone "
                "who has spent forty years guarding a politician from his own "
                "cleverness. He has the build of a retired wrestler and the "
                "patience of a man who has watched Hardin win arguments with "
                "people who thought they were winning."
            ),
            topics={
                "board": "Pirenne has the Vault key. Show him your logic sheets.",
                "anacreon": "Rodric is at the landing pad. He drinks anything that is not nailed down.",
                "vault": "Pirenne controls the key. Fara controls the schedule. The rest of us control the exits.",
                "religion": "Verisof is back from Anacreon. He knows Aporat. That is more useful than a navy.",
                "plan": "Make the fleet irrelevant. Anacreon cannot run its power plants without our technicians.",
            },
            on_ask=lee_topics,
            on_talk=lee_talk,
        ),
        "pirenne": NPC(
            key="pirenne",
            names=["pirenne", "lewis pirenne", "doctor pirenne", "chairman"],
            short="Lewis Pirenne",
            location="council_chamber",
            desc=(
                "Lewis Pirenne is a tall, thin man with the bearing of a scholar "
                "who has been interrupted by history and intends to file a "
                "complaint. His collar is immaculate. His patience is not."
            ),
            topics={
                "vault": "The Vault is a scientific instrument, not a fortune-telling booth. I have the key.",
                "anacreon": "The Empire will not allow a provincial kingdom to annex a charter world.",
                "board": "The Encyclopedia is the greatest scientific project in history. Everything else is politics.",
            },
            on_ask=pirenne_topics,
            on_show=pirenne_show,
        ),
        "sutt": NPC(
            key="sutt",
            names=["sutt", "tomaz sutt", "trustee sutt"],
            short="Tomaz Sutt",
            location="council_chamber",
            desc=(
                "Tomaz Sutt is a round, worried man who has spent his life "
                "cataloguing the decline of things and has recently begun to "
                "suspect he is one of them."
            ),
            topics={
                "anacreon": "We have no metals, no fleet, and no army. We have a printing press and a very good index.",
                "vault": "Fara thinks the Vault will solve everything. Fara also thinks subordinate clauses are a form of rest.",
            },
            on_ask=sutt_topics,
        ),
        "fara": NPC(
            key="fara",
            names=["fara", "jord fara", "trustee fara"],
            short="Jord Fara",
            location="council_chamber",
            desc=(
                "Jord Fara is small, round, and placid, with the air of a man who "
                "has made peace with the universe and expects the universe to "
                "reciprocate."
            ),
            topics={
                "vault": "The Vault opens at the anniversary. Hari Seldon knew we would need him.",
                "hardin": "Mayor Hardin is clever. The Board has decided to be patient with him.",
            },
            on_ask=fara_topics,
        ),
        "sermak": NPC(
            key="sermak",
            names=["sermak", "sef sermak", "councilman", "councilman sermak"],
            short="Sef Sermak",
            location="city_square",
            desc=(
                "Sef Sermak is young enough to be angry and careful enough to be "
                "dangerous. He stands in the square with three supporters and the "
                "expression of a man who has already written your concession "
                "speech."
            ),
            topics={
                "anacreon": "You have spent thirty years giving nuclear power to our enemies and calling it diplomacy.",
                "hardin": "Hardin is the most dangerous kind of politician: one who is usually right.",
                "election": "The next election will happen whether you win this crisis or not.",
            },
            on_ask=sermak_topics,
        ),
        "verisof": NPC(
            key="verisof",
            names=["verisof", "poly verisof", "high priest", "priest"],
            short="Poly Verisof",
            location="temple",
            desc=(
                "Poly Verisof is a slim, tired man in an immaculate crimson robe. "
                "He looks like a high priest who has spent fourteen years "
                "pretending to be one and has recently been asked to prove it."
            ),
            topics={
                "religion": "The religion of science is a machine for making barbarians accept reality.",
                "relay": "The Prayer Engine needs a waveguide, a power cell, the fleet frequency, and a litany.",
                "aporat": "Theo Aporat has seen the curse work. Convince him and he will speak it.",
                "wienis": "Wienis is a fool with a navy and a nephew on a throne.",
            },
            on_ask=verisof_topics,
            on_talk=verisof_talk,
        ),
        "aporat": NPC(
            key="aporat",
            names=["aporat", "theo aporat", "theo", "anacreon priest"],
            short="Theo Aporat",
            location="temple",
            desc=(
                "Theo Aporat is a dark, careful man in a crimson robe cut in the "
                "Anacreonian style. He watches the Prayer Engine with the expression "
                "of a priest who has heard the machine answer back."
            ),
            topics={
                "curse": "A curse is a technical instruction with better staging.",
                "wienis": "Wienis believes the fleet is his. The fleet belongs to whoever controls the relay.",
            },
            on_ask=aporat_topics,
            on_talk=aporat_talk,
        ),
        "wienis": NPC(
            key="wienis",
            names=["wienis", "prince wienis", "prince regent", "regent"],
            short="Prince Regent Wienis",
            location="landing_pad",
            desc=(
                "Prince Regent Wienis is a dark, hook-nosed man with grey hair and "
                "a squint in his right eye. He wears a coat worth more than the "
                "city budget and the expression of a man who has never been told "
                "no by anyone who could enforce it."
            ),
            topics={
                "fleet": "The fleet is the finest in the Periphery. It carries enough firepower to make Terminus a memory.",
                "treaty": "The treaty is generous. You keep your city, your Council, your Encyclopedia. You lose only decisions.",
                "religion": "The priests are useful. When they become inconvenient, they are transferred to a very cold moon.",
            },
            on_ask=wienis_topics,
            on_talk=wienis_talk,
            on_attack=wienis_attack,
        ),
        "rodric": NPC(
            key="rodric",
            names=["rodric", "haut rodric", "anselm haut rodric", "envoy", "ambassador"],
            short="Haut Rodric",
            location="landing_pad",
            desc=(
                "Anselm haut Rodric is a broad, polished man with a rehearsed smile "
                "and a uniform pressed by someone who fears him. He is the sort of "
                "ambassador who considers a treaty a preliminary to a victory "
                "parade."
            ),
            topics={
                "fleet": "The flagship is the Wienis. It can reduce a planet to gravel in an afternoon.",
                "relay": "The Foundation installed a hyperwave relay on the flagship. Official reason: communications.",
                "treaty": "Terms are simple. Terminus becomes a protectorate. Everyone who cooperates gets a title.",
            },
            on_ask=rodric_topics,
            on_talk=rodric_talk,
            on_give=rodric_give,
        ),
    }

    return World(
        act=2,
        title="The Mayors",
        subtitle="Terminus, 50 Foundation Era",
        protagonist="Salvor Hardin",
        start_room="mayor_office",
        intro=(
            "You are Salvor Hardin, Mayor of Terminus. Thirty years ago, Hari "
            "Seldon's Vault opened and told the Foundation that the Encyclopedia "
            "Galactica was a fraud. You were the one who acted on it. The Board of "
            "Trustees has never entirely forgiven you, and the voters have never "
            "entirely stopped.\n\n"
            "Now the first crisis of the Plan has arrived. Anacreon, the strongest "
            "of the Four Kingdoms, has sent an ultimatum: surrender within a week, "
            "or be annexed. The Board would like to file a protest. The Anacreonians "
            "would like to land. You have a city, a printing press, an atomic power "
            "plant, and the deeply held conviction that violence is the last refuge "
            "of the incompetent.\n\n"
            "You also have a towel. The Guide considers this the beginning of a "
            "strategy."
        ),
        rooms=rooms,
        objects=objects,
        npcs=npcs,
        max_score=100,
        guide_keys=["TERMINUS", "ATOMICS"],
        hints=act2_hints,
        on_say=act2_on_say,
        epilogue=(
            "The first crisis ends with the Foundation still standing and the "
            "religion of science still working. Somewhere in the city, a priest "
            "blesses a power plant. Somewhere in the Palace of Anacreon, a prince "
            "reads a treaty and discovers that the expensive part is not the war."
        ),
    )

