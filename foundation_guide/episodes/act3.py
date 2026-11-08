"""Act III — The Mule.

Bayta Darell is on her honeymoon on Kalgan when the Mule's fleet takes the
pleasure planet.  With her husband Toran, a runaway clown called Magnifico, and
a yacht named *Bayta*, she escapes to the ruins of Trantor, where Ebling Mis is
searching the Imperial Library for the Second Foundation.  The answer is buried
in the oldest catalogue in the Galaxy, and so is the Mule.

The act follows the shape of Asimov's "The Mule": Kalgan, the clown, the
Visi-Sonor, Star's End, Tazenda and Rossem, and a final choice in a farmhouse
with a blaster and a friend.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..model import Exit, NPC, Object, Room, World

if TYPE_CHECKING:  # pragma: no cover
    from ..engine import Game

QUIET_ENDING = "act3_quiet"
OPEN_ENDING = "act3_open"


def _norm(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(
        text.lower().replace("\u2019", "'").replace("-", " ").split()
    ).strip(" .!")


def _has_blaster(g: "Game") -> bool:
    return g.is_carried("blaster")


# ---------------------------------------------------------------------------
# Kalgan: promenade, hotel, palace
# ---------------------------------------------------------------------------


def newspaper_read(g: "Game", obj: Object) -> None:
    g.award_once(
        "kalgan_newspaper",
        2,
        "Read the Kalgan Daily. Journalism survives everything except accuracy.",
    )
    g.set_flag("newspaper_read")
    g.unlock_guide("KALGAN")
    g.unlock_guide("THE MULE")
    return None


def itinerary_read(g: "Game", obj: Object) -> None:
    g.award_once(
        "honeymoon_itinerary",
        2,
        "Read the honeymoon itinerary. The romantic part lasted one paragraph.",
    )
    g.set_flag("itinerary_read")
    g.unlock_guide("KALGAN")
    return None


def palace_condition(g: "Game") -> bool:
    return "uniform" in g.state.obj_worn or g.has("palace_uniform_ok")


def hangar_condition(g: "Game") -> bool:
    return g.is_carried("exit_pass")


def major_domo_give(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key != "wine":
        g.say(
            "The major-domo examines the offered item with the expression of a "
            "man who has been bribed before and found the experience "
            "underwhelming. 'The Mule does not accept gifts. He accepts "
            "invoices.'"
        )
        return True
    if g.has("major_domo_bribed"):
        g.say(
            "The major-domo is asleep in his chair, smiling at a dream in which "
            "the Mule is audited by the Imperial Revenue Service. He has no "
            "further use for wine."
        )
        return True
    g.state.obj_loc["wine"] = None
    g.set_flag("major_domo_bribed")
    g.state.obj_loc["exit_pass"] = "player"
    g.state.obj_loc["trophy_key"] = "player"
    g.award_once(
        "bribe",
        5,
        "Bribed the Mule's major-domo with Kalganian wine. Democracy is a broad church.",
    )
    g.unlock_guide("KALGAN")
    g.unlock_guide("THE MULE")
    g.achievement("THE PALACE IS ASLEEP")
    g.say(
        "The major-domo studies the bottle. 'Terminus Reserve,' he reads. "
        "'Aged three weeks. The Mule's cellar is not what it was.' He opens it "
        "with the fatalism of a civil servant accepting a pension."
    )
    g.say(
        "Two glasses later he is explaining the palace's security arrangements "
        "to a potted plant. He presses a departure pass and a small trophy key "
        "into your hand, then settles into his chair with the boneless "
        "confidence of a man who has decided that the next hour is somebody "
        "else's problem."
    )
    g.say("You have the exit pass and the trophy key.")
    return True


def major_domo_talk(g: "Game", npc: NPC) -> bool:
    if g.has("major_domo_bribed"):
        g.say(
            "The major-domo is asleep. His breathing is precise, as if even his "
            "snoring has been entered in a ledger."
        )
        return True
    g.say(
        "The major-domo is a thin, immaculate man with the eyes of someone who "
        "has counted every spoon in the palace and found the tally wanting. He "
        "regards your bellhop uniform without admiration."
    )
    g.say(
        "'The Hall of Triumphs is closed,' he says. 'The Mule's trophies are "
        "not for the entertainment of hotel staff. If you have business with "
        "the palace, state it to the guards. If you have no business, the "
        "promenade is that way.'"
    )
    return True


def major_domo_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("visi sonor", "instrument", "trophy", "hall of triumphs"):
        g.say(
            "'The clown's instrument is in the Hall of Triumphs,' he says. 'A "
            "hideous thing. It has no strings, no keys, and no proper method of "
            "being played. The Mule values it. The Mule values many things he "
            "does not understand. It is one of the privileges of power.'"
        )
        return True
    if text in ("pass", "exit", "departure", "hangar"):
        g.say(
            "'Departure passes are issued by me,' he says. 'They are issued to "
            "people who have completed their business, paid their bills, and "
            "not annoyed me. You have completed one of the three.'"
        )
        return True
    if text in ("mule", "bobo", "clown"):
        g.say(
            "'The Mule is not a man to be discussed by staff,' he says. 'He is "
            "also not a man to be discussed by me. I have a pension, a suite, "
            "and a very good memory. I intend to keep at least two of them.'"
        )
        return True
    if text in ("wine", "drink", "bribe"):
        g.say(
            "The major-domo's eyes flick to the bottle in your hand and then "
            "away, with the discipline of a man who has been trained not to "
            "want things in front of witnesses."
        )
        return True
    return None


def trophy_case_open(g: "Game", obj: Object) -> bool | None:
    g.say(
        "The glass case opens with a sigh. The Visi-Sonor sits on a cushion of "
        "black velvet, looking less like an instrument than like a machine that "
        "has been asked to behave itself in public."
    )
    return None


def visi_sonor_take(g: "Game", obj: Object) -> None:
    g.award_once(
        "visi_sonor",
        8,
        "Recovered the Visi-Sonor. The Mule's trophy collection has a new entry.",
    )
    g.set_flag("visi_sonor_taken")
    g.unlock_guide("VISI-SONOR")
    g.unlock_guide("THE MULE")
    g.achievement("THE CLOWN'S INSTRUMENT")
    g.say(
        "You lift the Visi-Sonor out of its case. It is lighter than it looks "
        "and warmer than it should be, as if something inside it has been "
        "waiting to be played."
    )
    return None


def magnifico_talk(g: "Game", npc: NPC) -> bool:
    if g.has("final_scene") and not g.has("ending_done"):
        g.say(
            "Magnifico looks at you with the sad brown eyes of the clown, "
            "except that the sadness is older now, and the eyes are not sad at "
            "all. They are patient."
        )
        g.say(
            "'You have been very kind to me,' he says. 'That is why I wanted "
            "you to be the one who understood. The Mule is not a monster. He is "
            "a very tired man with a very large talent and a very bad "
            "childhood. But he is still the Mule.'"
        )
        return True
    if g.has("magnifico_follows"):
        g.say(
            "Magnifico huddles in his absurd coat, the Visi-Sonor tucked under "
            "one arm like a sleeping animal. 'I am here,' he says. 'I am always "
            "here. That is the trouble with clowns.'"
        )
        return True
    g.say(
        "The clown is small enough to be mistaken for a child and strange "
        "enough to be mistaken for a hallucination. His nose is long, his "
        "cheeks are painted in two impossible circles, and his clothes look as "
        "if they were tailored for a smaller clown and then left in the rain."
    )
    g.say(
        "'They took it,' he whispers. 'The Mule's major-domo took my Visi-Sonor. "
        "It is all I have. Without it I cannot think. Without it I cannot hide. "
        "Please. The palace is north. The major-domo likes wine. Everyone at "
        "the palace likes wine. It is the only thing the Mule has not "
        "nationalised.'"
    )
    g.set_flag("magnifico_met")
    g.unlock_guide("THE MULE")
    g.unlock_guide("KALGAN")
    return True


def magnifico_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("visi sonor", "instrument", "music"):
        g.say(
            "'The Visi-Sonor is not music,' Magnifico says. 'It is what music "
            "wants to be when it grows up. It shows you things. It shows you "
            "what you are feeling before you have decided to feel it.'"
        )
        return True
    if text in ("mule", "bobo", "kalgan"):
        g.say(
            "'The Mule is a dream,' Magnifico says, and then, quickly, 'A bad "
            "dream. The kind you cannot wake from because it has your shoes.' "
            "He glances at the palace and adds nothing."
        )
        return True
    if text in ("foundation", "terminus", "psychohistory"):
        g.say(
            "'The Foundation is a world of great magic,' he says, in the voice "
            "of a man reciting a lesson. 'Fires that consume planets. Secrets "
            "of mighty strength.' He pauses. 'I have never been there. I have "
            "only heard the stories. The stories are better than most places.'"
        )
        return True
    if text in ("second foundation", "star's end", "stars end"):
        g.say(
            "Magnifico's eyes go wide and then carefully blank. 'The Second "
            "Foundation is a story for children,' he says. 'A story to make "
            "the dark feel smaller. Please do not ask me about it. I am a clown, "
            "not a librarian.'"
        )
        return True
    return None


def magnifico_give(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key != "visi_sonor":
        g.say(
            "Magnifico looks at the offered object, then at you, with the "
            "careful politeness of someone who has been given many things by "
            "people who wanted something back."
        )
        g.say("'Thank you,' he says. 'I will keep it. I keep everything.'")
        return True
    if g.has("magnifico_follows"):
        g.say(
            "Magnifico is already holding the Visi-Sonor against his chest, as "
            "if it might be confiscated again by a passing government."
        )
        return True
    g.set_flag("magnifico_follows")
    g.state.obj_loc["visi_sonor"] = "player"
    g.award_once(
        "magnifico",
        10,
        "Returned the Visi-Sonor to Magnifico. He is yours now, in the way that sadness is yours.",
    )
    g.unlock_guide("VISI-SONOR")
    g.unlock_guide("THE MULE")
    g.unlock_guide("SECOND FOUNDATION")
    g.achievement("THE CLOWN'S FRIEND")
    g.say(
        "Magnifico takes the Visi-Sonor with both hands. For a moment he does "
        "not move. Then he plays a single note, and the promenade changes "
        "colour, very slightly, in a way that has nothing to do with the sun."
    )
    g.say(
        "'I will go with you,' he says. 'I will go with you to the end of the "
        "Galaxy, if that is where the answer is. I am very good at being "
        "frightened. It is my only skill, and I have practised.'"
    )
    g.say(
        "He lets you carry the instrument, because he says his hands are "
        "shaking and because, in his experience, people do not confiscate "
        "things from the person who is helping them."
    )
    return True


# ---------------------------------------------------------------------------
# The yacht: course, launch, and the road to Star's End
# ---------------------------------------------------------------------------


def nav_use(g: "Game", obj: Object, target: object) -> bool:
    g.say(
        "The nav computer displays a polite cursor and a list of known "
        "destinations. It is waiting for a course. Type SET COURSE TO TRANTOR."
    )
    return True


def nav_set(g: "Game", obj: Object, value: str | None) -> bool:
    text = _norm(value)
    if not text:
        g.say("Set the course to what? The nav computer is patient, but not infinitely.")
        return True

    if text in ("trantor", "star's end", "stars end", "trantor ruins", "the centre", "the center"):
        if g.has("yacht_at_trantor"):
            g.say("The nav computer points out, with elaborate courtesy, that you are already at Trantor.")
            return True
        g.set_flag("course_trantor")
        g.clear_flag("course_rossem")
        g.award_once(
            "course_trantor",
            8,
            "Plotted a course to Trantor, Star's End. The centre of the Galaxy is a very old idea.",
        )
        g.unlock_guide("TRANTOR")
        g.unlock_guide("STAR'S END")
        g.say(
            "The nav computer accepts the coordinates for Trantor. The route "
            "unfolds across the screen like a nervous spider: Kalgan, the "
            "Periphery, the old Imperial lanes, and then the centre of the "
            "Galaxy, where the metal planet waits under its dead sky."
        )
        g.say("Course set for Trantor. The launch lever is armed.")
        return True

    if text in ("rossem", "tazenda", "tazenda rossem", "tazenda/rossem", "rossem tazenda"):
        if not g.has("tazenda_known"):
            g.say(
                "The nav computer has no coordinates for Tazenda. It suggests, "
                "in the tone of a machine that has been programmed by a "
                "committee, that you consult an archive."
            )
            return True
        if g.has("yacht_at_rossem"):
            g.say("The nav computer observes that you are already at Rossem.")
            return True
        g.set_flag("course_rossem")
        g.clear_flag("course_trantor")
        g.award_once(
            "course_rossem",
            5,
            "Plotted a course to Rossem. The clue was worth the fuel.",
        )
        g.unlock_guide("TAZENDA")
        g.unlock_guide("ROSSEM")
        g.say(
            "The nav computer accepts the Tazendian coordinates. The route is "
            "short, cold, and studded with the sort of minor worlds that "
            "galactic history uses as punctuation."
        )
        g.say("Course set for Rossem. The launch lever is armed.")
        return True

    g.say(
        "The nav computer knows Trantor, and it will know Tazenda once you "
        "bring it coordinates. It does not know that."
    )
    return True


def launch_use(g: "Game", obj: Object, target: object) -> bool:
    return launch_pull(g, obj)


def launch_pull(g: "Game", obj: Object) -> bool:
    if g.has("ending_done"):
        g.say("The lever is loose in your hand. There is nowhere left to go.")
        return True

    if g.has("course_rossem"):
        if not g.has("tazenda_known"):
            g.say("The nav computer refuses the course until it has coordinates.")
            return True
        if not g.has("magnifico_follows"):
            g.say(
                "The launch lever refuses to move. Magnifico is not aboard. The "
                "yacht's safety system is old-fashioned: it insists on a clown."
            )
            return True
        g.clear_flag("course_rossem")
        g.set_flag("reached_rossem")
        g.set_flag("yacht_at_rossem")
        g.clear_flag("yacht_at_kalgan")
        g.clear_flag("yacht_at_trantor")
        g.award_once(
            "reach_rossem",
            5,
            "Reached Rossem. It is cold, agricultural, and full of people pretending not to know things.",
        )
        g.unlock_guide("ROSSEM")
        g.unlock_guide("TAZENDA")
        g.achievement("THE PERIPHERY OF THE PERIPHERY")
        g.say(
            "The yacht drops out of hyperspace above a small, cold world with "
            "the colours of a dishcloth. Rossem turns beneath you, all fields "
            "and forests and roads that lead to villages that do not appear on "
            "any Imperial map."
        )
        g.say(
            "A stubby Tazendian patrol ship rises from the horizon, sees the "
            "Foundation markings on your hull, and decides, with the prudence "
            "of a small empire, to become very interested in something else."
        )
        g.say("The Bayta settles into a muddy landing field. Rossem is waiting.")
        g.teleport("rossem_landing")
        return True

    if g.has("course_trantor"):
        if not g.has("magnifico_follows"):
            g.say(
                "The launch lever refuses to move. Magnifico is not aboard. The "
                "yacht's safety system is old-fashioned: it insists on a clown."
            )
            return True
        g.clear_flag("course_trantor")
        g.set_flag("escaped_kalgan")
        g.set_flag("yacht_at_trantor")
        g.clear_flag("yacht_at_kalgan")
        g.award_once(
            "escape_kalgan",
            8,
            "Escaped Kalgan aboard the Bayta. The Mule's hangar crew will be very upset.",
        )
        g.unlock_guide("TRANTOR")
        g.unlock_guide("IMPERIAL LIBRARY")
        g.unlock_guide("STAR'S END")
        g.achievement("LEAVING ON A JET PLANE")
        g.say(
            "You pull the launch lever. The Bayta shivers, rises, and slides "
            "out of the hangar on a cushion of indignant air. Below, the "
            "Mule's palace shrinks to a gaudy toy, then to a memory, then to a "
            "coordinate."
        )
        g.say(
            "The yacht jumps. Hyperspace is not a place, but if it were, it "
            "would look like a dark room in which somebody has just told a "
            "very long joke and forgotten the punchline."
        )
        g.say(
            "You come out above Trantor. The old capital of the Galaxy is a "
            "sphere of metal, grey and silent, its cities buried under "
            "centuries of rust and weather. Star's End, the poets called it. "
            "From here, it looks like the end of every road."
        )
        g.teleport("trantor_ruins")
        return True

    g.say(
        "The launch lever is locked. The nav computer is still waiting for a "
        "destination. SET COURSE TO TRANTOR."
    )
    return True


def leave_yacht(g: "Game") -> bool:
    if g.has("yacht_at_trantor"):
        g.teleport("trantor_ruins")
    elif g.has("yacht_at_rossem"):
        g.teleport("rossem_landing")
    else:
        g.teleport("kalgan_hangar")
    return True


def glowlamp_take(g: "Game", obj: Object) -> None:
    g.set_flag("light")
    g.say(
        "The glowlamp comes on with a soft, dependable light. The Guide notes "
        "that a towel is useful in many situations, but none of them involve "
        "seeing in the dark."
    )
    return None


# ---------------------------------------------------------------------------
# Trantor and the Imperial Library
# ---------------------------------------------------------------------------


def rubble_search(g: "Game", obj: Object) -> bool:
    if g.has("library_found"):
        g.say(
            "The stair is already open. Below, the Imperial Library waits with "
            "the patience of an institution that has outlived several empires."
        )
        return True
    if not (g.has("light") or g.is_carried("glowlamp")):
        g.say(
            "The rubble is a mountain of black metal and broken statuary. In "
            "the dark you cannot tell a stair from a shadow. Somewhere aboard "
            "the yacht there is a glowlamp."
        )
        return True
    g.set_flag("library_found")
    if "stair" in g.world.objects:
        g.world.objects["stair"].hidden = False
    g.award_once(
        "library_entrance",
        5,
        "Found the stair to the Imperial Library. It was under the rubble, where libraries usually are.",
    )
    g.unlock_guide("IMPERIAL LIBRARY")
    g.unlock_guide("TRANTOR")
    g.say(
        "You haul a slab of fallen dome aside. Beneath it, a stair spirals "
        "down into the metal skin of Trantor, lit at intervals by emergency "
        "globes that have been burning, with bureaucratic stubbornness, for "
        "two hundred years."
    )
    g.say("A brass plate beside the stair reads: IMPERIAL LIBRARY — SILENCE, PLEASE.")
    return True


def caretaker_talk(g: "Game", npc: NPC) -> bool:
    if not g.has("caretaker_met"):
        g.set_flag("caretaker_met")
        g.say(
            "The caretaker is a small, ancient person wrapped in several "
            "libraries' worth of cardigans. They regard you over the top of a "
            "catalogue drawer with the calm of someone who has survived the "
            "sack of Trantor and several overdue notices."
        )
        g.say(
            "'The Imperial Library is closed,' they say. 'It has been closed "
            "since the Empire fell. We are open only for researchers, "
            "refugees, and people who know how to whisper. Which are you?'"
        )
    else:
        g.say(
            "The caretaker is reshelving a book that has been waiting four "
            "hundred years for a reader. They do not look up."
        )
    return True


def caretaker_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("archive", "restricted archive", "stacks"):
        g.say(
            "'The restricted archive is east,' the caretaker says. 'It contains "
            "the Imperial star atlases, the pre-Fall census records, and one "
            "very determined psychohistorian. Access requires Foundation "
            "credentials. The Empire is gone, but paperwork is eternal.'"
        )
        return True
    if text in ("library", "imperial library", "trantor"):
        g.say(
            "'The Library survived because books are heavy and looters are "
            "lazy,' the caretaker says. 'Also because the basement is the "
            "largest on Trantor. The Empire built its archives downward. It "
            "always did prefer to bury its mistakes.'"
        )
        return True
    if text in ("seldon", "psychohistory", "plan"):
        g.say(
            "'Hari Seldon consulted here,' the caretaker says. 'He was a "
            "charming man with the handwriting of a physician and the manners "
            "of a man who has already seen the end of the conversation. He "
            "reserved the same desk every week for forty years. We kept it "
            "empty after he died. Then we rented it out. The Empire fell.'"
        )
        return True
    if text in ("second foundation", "star's end"):
        g.say(
            "The caretaker's expression does not change. 'There is no Second "
            "Foundation,' they say. 'There is a restricted archive, a great "
            "deal of dust, and a rumour that has been reshelved under "
            "WISHFUL THINKING. Please do not ask again.'"
        )
        return True
    return None


def caretaker_show(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key != "credentials":
        g.say(
            "The caretaker examines the offered object with professional "
            "disapproval. 'The Library does not accept flowers, bribes, or "
            "unsolicited manuscripts. It accepts credentials.'"
        )
        return True
    if g.has("archive_open"):
        g.say("The caretaker has already opened the archive. They are pretending they did not enjoy it.")
        return True
    g.set_flag("archive_open")
    g.award_once(
        "archive_access",
        8,
        "Opened the restricted archive with Foundation credentials. Bureaucracy has its uses.",
    )
    g.unlock_guide("IMPERIAL LIBRARY")
    g.unlock_guide("SECOND FOUNDATION")
    g.achievement("THE LIBRARY CARD")
    g.say(
        "The caretaker takes your Foundation credentials, holds them up to the "
        "light, and squints at the seal. 'Terminus,' they read. 'Foundation. "
        "Scientific. Slightly optimistic.'"
    )
    g.say(
        "They stamp the credentials with a rubber stamp that has not been "
        "cleaned since the reign of Cleon I, and hand them back. 'The archive "
        "is east. Do not reshelve anything. Do not play music. Do not wake the "
        "psychohistorian unless you have brought coffee.'"
    )
    return True


def star_atlas_read(g: "Game", obj: Object) -> None:
    g.award_once(
        "star_atlas",
        4,
        "Read the Imperial star atlas. The Galaxy is larger than the footnotes suggest.",
    )
    g.set_flag("atlas_read")
    g.unlock_guide("STAR'S END")
    g.unlock_guide("TAZENDA")
    return None


def visi_sonor_use(g: "Game", obj: Object, target: object) -> bool:
    key = getattr(target, "key", None) if target is not None else None
    if key != "mis":
        if target is None:
            g.say(
                "You strike a chord on the Visi-Sonor. The room briefly smells "
                "of rain on a world you have never visited. The instrument is "
                "not interested in background music."
            )
        else:
            g.say(
                "The Visi-Sonor is not a weapon, a key, or a universal remote. "
                "It is an instrument. It works best on minds that are ready to "
                "listen."
            )
        return True
    if g.has("tazenda_known"):
        g.say(
            "Magnifico plays a quiet, tired phrase. Mis does not look up. The "
            "answer is already written in his notes, and in yours."
        )
        return True
    if not g.has("atlas_read"):
        g.say(
            "Mis waves the Visi-Sonor away. 'A starting point first,' he says. "
            "'The star atlas on the table. I need a fact to hang the music on. "
            "Even a genius cannot deduce a galaxy from a chord.'"
        )
        return True
    if not g.has("magnifico_follows"):
        g.say(
            "Mis looks at the Visi-Sonor, then at the empty space where a "
            "performer should be. 'I can hold the instrument,' he says. 'I "
            "cannot play it. Find the clown.'"
        )
        return True

    g.set_flag("tazenda_known")
    g.set_flag("secret_known")
    g.award_once(
        "decode",
        10,
        "Mis decoded Star's End while Magnifico played. The answer was under your feet all along.",
    )
    g.unlock_guide("TAZENDA")
    g.unlock_guide("SECOND FOUNDATION")
    g.unlock_guide("STAR'S END")
    g.unlock_guide("THE MULE")
    g.achievement("STAR'S END")
    g.say(
        "Magnifico raises the Visi-Sonor. The archive fills with a sound that "
        "is not quite music: a slow, luminous pressure, like a tide coming in "
        "over a library. Dust rises from the film books and hangs in the air, "
        "arranged in patterns that look almost like equations."
    )
    g.say(
        "Ebling Mis stops moving. His eyes are open, but they are looking at "
        "something that is not in the room. 'Star's End,' he mutters. 'Not the "
        "edge of the Galaxy. The centre. The old capital. Trantor. The clue was "
        "a joke, and the joke was on everyone who looked for a periphery.'"
    )
    g.say(
        "'Tazenda is a figurehead,' he says, faster now. 'A provincial kingdom "
        "with a good publicist. The Second Foundation is not there. It is here. "
        "Beneath the Library. Beneath the oldest catalogue in the Galaxy. The "
        "centre of the story.'"
    )
    g.say(
        "Mis looks up at you, and for the first time he looks afraid. 'The Mule "
        "must not learn the exact coordinates,' he says. 'He can burn a world. "
        "He cannot burn a secret that has already been hidden. But if he learns "
        "where to dig—'"
    )
    g.say(
        "Magnifico lowers the Visi-Sonor. His face is pale under the clown "
        "paint. 'Tazenda,' he says softly. 'Of course. The governors. The "
        "Elders. Rossem.'"
    )
    return True


def mis_talk(g: "Game", npc: NPC) -> bool:
    if g.has("tazenda_known"):
        g.say(
            "Ebling Mis is surrounded by notes, cold coffee, and the kind of "
            "silence that follows a very large idea. 'Star's End is Trantor,' "
            "he says. 'The exact location is in the catalogue. The Mule must "
            "not have it. If he asks, I will try not to answer. Try. That is "
            "the best a man can promise.'"
        )
        return True
    if not g.has("atlas_read"):
        g.say(
            "Ebling Mis is a large, untidy man in a stained jacket, smoking a "
            "cigar that violates at least three library regulations. He does "
            "not look up. 'I need a starting point,' he says. 'The star atlas. "
            "Bring me a fact. Facts are the only things that do not lie to me.'"
        )
        return True
    if not g.has("magnifico_follows"):
        g.say(
            "'I have the fact,' Mis says. 'I do not have the music. The "
            "Visi-Sonor focuses the mind. Without it I am a very clever man "
            "with a headache. Find the clown. Bring the instrument.'"
        )
        return True
    g.say(
        "Mis looks at the Visi-Sonor in your hands, then at Magnifico. 'Ah,' he "
        "says. 'The boy. Good. Let him play. I have been waiting for a sound "
        "that can drown out the Empire.'"
    )
    g.say("Perhaps you should USE THE VISI-SONOR ON MIS.")
    return True


def mis_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("tazenda", "rossem", "star's end"):
        if g.has("tazenda_known"):
            g.say(
                "'Tazenda is a decoy,' Mis says. 'A provincial kingdom dressed "
                "up as a mystery. Rossem is its poorest province. The Second "
                "Foundation is not there. It is at Star's End, and Star's End "
                "is Trantor.'"
            )
        else:
            g.say(
                "'Tazenda is a name in an old atlas,' Mis says. 'Rossem is a "
                "name in a newer one. Neither is an answer until the atlas "
                "tells me what question to ask.'"
            )
        return True
    if text in ("second foundation", "psychohistory", "plan"):
        g.say(
            "'The Second Foundation is the Plan's insurance policy,' Mis says. "
            "'A group of psychologists at the other end of the Galaxy, "
            "correcting the mathematics when people like the Mule introduce an "
            "error. I have spent my life trying to find them. I am beginning to "
            "suspect they have spent their lives trying not to be found.'"
        )
        return True
    if text in ("mule", "magnifico", "clown"):
        if g.has("tazenda_known"):
            g.say(
                "'The clown is the Mule,' Mis says, without drama. 'I have known "
                "since Terminus. It is the only explanation for the Visi-Sonor, "
                "the timing, and the way he looks at you when he thinks no one "
                "is watching. Do not tell him I know. He is stronger when he is "
                "afraid.'"
            )
        else:
            g.say(
                "'The Mule is a mutant,' Mis says. 'A single individual outside "
                "the equations. Psychohistory cannot predict him. That is not a "
                "reason to stop doing psychohistory. It is a reason to be "
                "careful with the answers.'"
            )
        return True
    return None


def mis_attack(g: "Game", npc: NPC) -> bool:
    if g.room().key == "rossem_farmhouse" and g.has("final_scene"):
        if not _has_blaster(g):
            g.state.obj_loc["blaster"] = "player"
            g.say("Toran presses a blaster into your hand. It is cold and very definite.")
        return finish_final(g, "quiet")
    g.say(
        "You cannot bring yourself to attack Ebling Mis. He is old, brilliant, "
        "and currently using his last clean handkerchief as a bookmark. The "
        "Guide suggests a more constructive form of violence, such as "
        "politics."
    )
    return True


# ---------------------------------------------------------------------------
# Rossem and the final choice
# ---------------------------------------------------------------------------


def elder_talk(g: "Game", npc: NPC) -> bool:
    if not g.has("elder_talked"):
        g.set_flag("elder_talked")
        g.award_once(
            "elder",
            5,
            "Talked to the Elders of Rossem. They know more than they say, which is the local definition of diplomacy.",
        )
        g.unlock_guide("ROSSEM")
        g.unlock_guide("TAZENDA")
        g.achievement("THE ELDERS OF ROSSEM")
        g.say(
            "The Elder is a brown, weathered man with hands like old roots and "
            "the careful eyes of someone who has spent his life pretending not "
            "to notice armies. He offers you a bowl of something warm and "
            "agricultural."
        )
        g.say(
            "'You are from the Foundation,' he says. 'The Mule's men are also "
            "from the Foundation, or they say so. They ask about Tazenda. They "
            "ask about the Second Foundation. They ask in the way that people "
            "ask when they already have a list of answers and are looking for "
            "the question.'"
        )
        g.say(
            "'Tazenda is our lord,' he says. 'The governor lives on the hill. "
            "The taxes come every year. The soldiers come when the governor is "
            "frightened. Tonight the soldiers are coming, and the sky is full "
            "of ships that do not belong to Tazenda. You should come to my "
            "farmhouse. It is east. It is not much, but it is not on the hill.'"
        )
        g.say("The Elder's farmhouse lies east of the village.")
    else:
        g.say(
            "The Elder is watching the sky. 'The ships are landing,' he says. "
            "'The governor is hiding in his compound. The Mule's men are "
            "looking for a clown. I would not want to be a clown tonight.'"
        )
    return True


def elder_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("tazenda", "governor", "taxes"):
        g.say(
            "'Tazenda rules twenty-seven worlds,' the Elder says. 'Or it says "
            "it does. We see a governor once a year, a tax collector twice, "
            "and a soldier whenever the governor is afraid. It is not a bad "
            "arrangement, as arrangements go. The alternative is worse.'"
        )
        return True
    if text in ("mule", "ships", "soldiers"):
        g.say(
            "'The Mule's ships came out of nowhere,' he says. 'They did not "
            "bomb us. They landed, asked questions, and left. That is worse "
            "than bombing. A bomb is honest.'"
        )
        return True
    if text in ("second foundation", "psychohistory", "star's end"):
        g.say(
            "The Elder's face closes like a door. 'We do not talk about the "
            "Second Foundation,' he says. 'The last man who talked about it was "
            "taken to the governor's compound. He came back, but he did not "
            "talk about anything after that.'"
        )
        return True
    if text in ("rossem", "farm", "village"):
        g.say(
            "'Rossem is a poor world,' the Elder says. 'Poor worlds are good at "
            "keeping secrets. Nobody important comes to look. The Empire did "
            "not. The Foundation did not. The Mule has come, but the Mule is "
            "looking for something, and people who are looking do not see what "
            "is in front of them.'"
        )
        return True
    return None


def final_scene(g: "Game", first: bool) -> None:
    if g.has("final_scene"):
        g.say(
            "The farmhouse is quiet. Mis sits at the table with his notes. "
            "Magnifico stands by the window. Toran watches the door. Outside, "
            "the Mule's ships wait."
        )
        return
    g.set_flag("final_scene")
    g.world.npcs["mis"].location = "rossem_farmhouse"
    g.world.npcs["toran"].location = "rossem_farmhouse"
    g.world.npcs["magnifico"].location = "rossem_farmhouse"
    if not _has_blaster(g):
        g.state.obj_loc["blaster"] = "player"
        g.say("Toran presses a blaster into your hand. It is cold and very definite.")
    g.unlock_guide("THE MULE")
    g.unlock_guide("SECOND FOUNDATION")
    g.achievement("THE MULE UNMASKED")
    g.say(
        "The Elder's farmhouse is one low room with a fire, a table, and a "
        "window full of ships. The ships are not Tazendian. They hang above "
        "Rossem in a silent, orderly constellation, and their running lights "
        "make the fields look like the bottom of a very cold sea."
    )
    g.say(
        "Ebling Mis sits at the table, surrounded by notes. His lips are "
        "moving. He is not talking to anyone in the room. Toran stands by the "
        "door with his hand on his holster. Magnifico stands by the window, "
        "his back to you, the Visi-Sonor folded under one arm."
    )
    g.say(
        "Magnifico sets the Visi-Sonor down on the table. When he turns, his "
        "face is still painted, but the paint no longer looks funny. 'I am "
        "sorry,' he says. 'I have been sorry for a long time. It is not an "
        "excuse, but it is the truth.'"
    )
    g.say(
        "'I am the Mule,' he says. 'I was Bobo the clown, and then I was "
        "Magnifico, and then I was the thing that took Kalgan. I did not want "
        "to be any of them. I wanted to be a man who could stop being afraid. "
        "The universe did not offer that option.'"
    )
    g.say(
        "Mis's voice rises. 'The catalogue,' he says. 'The old catalogue. The "
        "coordinates are in the catalogue. The Second Foundation is at—'"
    )
    g.say(
        "The Mule looks at you. 'You have been kind to me,' he says. 'That is "
        "why I am asking you, and not taking it from him. I can take it. I have "
        "taken a great many things. But I would rather you gave it to me.'"
    )
    g.say(
        "Toran's blaster is in your hand. The fire is loud. Mis is still "
        "speaking. You have one moment, and the Guide is not going to make it "
        "for you."
    )
    g.say("SHOOT MIS to stop him, or SAY NOTHING and let him speak.")


def finish_final(g: "Game", choice: str) -> bool:
    if g.has("ending_done"):
        g.say("The moment has passed. History is many things, but it is not generous.")
        return True
    g.set_flag("ending_done")
    g.meta.ending = QUIET_ENDING if choice == "quiet" else OPEN_ENDING
    g.award_once(
        "final",
        15,
        "Made the last choice. The Guide closes the book very quietly.",
    )
    g.unlock_guide("SECOND FOUNDATION")
    g.unlock_guide("THE MULE")
    g.unlock_guide("STAR'S END")

    if choice == "quiet":
        g.world.ending_title = "THE QUIET SHOT"
        g.achievement("THE QUIET SHOT")
        if not _has_blaster(g):
            g.state.obj_loc["blaster"] = "player"
        g.say(
            "You raise the blaster and fire. The sound is smaller than you "
            "expected, and the silence afterward is much larger."
        )
        g.say(
            "Ebling Mis falls forward onto his notes. His hand, still moving, "
            "reaches for a page that is no longer there. Then it stops. The "
            "last man who knew where the Second Foundation is hidden dies on "
            "the floor of a farmhouse on a planet nobody has heard of."
        )
        g.say(
            "The Mule does not move. For a long moment he looks at Mis, then at "
            "you. The clown paint is streaked with something that might be "
            "sweat, or grief, or both."
        )
        g.say(
            "'You chose him,' he says. 'You chose the secret over the man who "
            "could have saved you. I have met patriots before. They usually "
            "enjoy the choosing. You do not.'"
        )
        g.say(
            "He picks up the Visi-Sonor and walks to the door. Outside, the "
            "ships begin to move, one by one, back into the dark."
        )
        g.say(
            "'I will not destroy Rossem,' he says. 'I will not destroy Tazenda. "
            "I will go home and be a man who is afraid, and I will try to be "
            "less afraid than I was. That is the best I can offer. It is more "
            "than the Foundation would have offered me.'"
        )
        g.say(
            "The Mule leaves. The Second Foundation remains hidden. Bayta "
            "Darell sits down beside the body of a man she killed to save a "
            "secret she will never be allowed to tell."
        )
    else:
        g.world.ending_title = "THE OPEN BOOK"
        g.achievement("THE OPEN BOOK")
        g.say(
            "You lower the blaster. You say nothing. The fire ticks. Mis's "
            "voice rises into the quiet."
        )
        g.say(
            "'The Second Foundation is at Star's End,' he says. 'Trantor. The "
            "Imperial Library. Beneath the old catalogue, in the lowest "
            "archive, the one the Empire forgot to inventory. The coordinates "
            "are—'"
        )
        g.say(
            "The Mule listens. He does not smile. He does not gloat. He simply "
            "listens, with the terrible attention of a man who has spent his "
            "whole life being afraid of a room he could not find."
        )
        g.say(
            "'Thank you,' he says, when Mis is finished. 'I know what it cost "
            "you to say nothing. I know what it will cost you to live with "
            "this. I am not going to pretend that I am sorry. I am going to "
            "Tazenda first, because a figurehead is still a useful lesson. "
            "Then I am going to Trantor.'"
        )
        g.say(
            "He picks up the Visi-Sonor. At the door he pauses. 'The Second "
            "Foundation has been very clever for a very long time,' he says. "
            "'It will be interesting to see whether it is clever enough.'"
        )
        g.say(
            "The Mule leaves. The ships follow him. Somewhere in the ruins of "
            "Trantor, a very old library begins, very quietly, to close its "
            "doors."
        )
    g.finish_act()
    return True


def act3_on_say(g: "Game", text: str) -> bool | None:
    if g.room().key != "rossem_farmhouse" or not g.has("final_scene"):
        return None
    if g.has("ending_done"):
        return None
    low = _norm(text)
    if low in (
        "nothing",
        "nothing at all",
        "silence",
        "i say nothing",
        "say nothing",
        "spare him",
        "let him speak",
        "stay silent",
    ):
        return finish_final(g, "open")
    if low in ("the mule", "you are the mule", "magnifico is the mule"):
        g.say(
            "The Mule inclines his head. 'Yes,' he says. 'I am. I have been for "
            "some time. It is a relief to be recognised, and a terror, and a "
            "very small kind of freedom.'"
        )
        return True
    return None


def act3_on_command(g: "Game", verb: str, cmd: object) -> bool | None:
    if g.room().key != "rossem_farmhouse" or not g.has("final_scene"):
        return None
    if g.has("ending_done"):
        return None
    dobj = _norm(getattr(cmd, "dobj", "") or "")
    iobj = _norm(getattr(cmd, "iobj", "") or "")
    if verb == "attack" and ("mis" in dobj.split() or dobj in ("ebling mis", "doctor mis", "dr mis")):
        if not _has_blaster(g):
            g.state.obj_loc["blaster"] = "player"
            g.say("Toran presses a blaster into your hand. It is cold and very definite.")
        return finish_final(g, "quiet")
    if verb == "use" and "blaster" in dobj and "mis" in iobj.split():
        if not _has_blaster(g):
            g.state.obj_loc["blaster"] = "player"
            g.say("Toran presses a blaster into your hand. It is cold and very definite.")
        return finish_final(g, "quiet")
    return None


# ---------------------------------------------------------------------------
# Hints and world hooks
# ---------------------------------------------------------------------------


def act3_hints(g: "Game") -> str:
    if g.room().key == "rossem_farmhouse" and g.has("final_scene"):
        return "The Mule is Magnifico. Mis is about to speak. SHOOT MIS, or SAY NOTHING and let him finish."
    if not g.has("newspaper_read"):
        return "The newspaper stand on the promenade may explain why the Mule's banners are everywhere. READ NEWSPAPER."
    if not g.has("magnifico_met"):
        return "The clown on the beach is trying to tell you something. TALK TO MAGNIFICO."
    if not g.has("itinerary_read"):
        return "Your honeymoon itinerary is in the suite. READ ITINERARY. It may be the last useful document you own."
    if "uniform" not in g.state.obj_worn:
        return "The palace guard only admits staff. Search the suite wardrobe for a bellhop uniform, then WEAR UNIFORM."
    if not g.has("major_domo_bribed"):
        return "The major-domo at the palace controls the trophy key and the exit pass. The minibar in your suite contains an argument. GIVE WINE TO MAJOR-DOMO."
    if not g.has("visi_sonor_taken"):
        return "The Visi-Sonor is in the Hall of Triumphs. OPEN TROPHY CASE with the trophy key, then TAKE VISI-SONOR."
    if not g.has("magnifico_follows"):
        return "Return to the promenade and GIVE VISI-SONOR TO MAGNIFICO. He will follow you."
    if not g.has("escaped_kalgan"):
        if not g.has("course_trantor"):
            return "The yacht is in Hangar 7, south of the promenade. Board it and SET COURSE TO TRANTOR on the nav computer."
        return "The course is set. PULL THE LAUNCH LEVER."
    if not g.has("library_found"):
        if not (g.has("light") or g.is_carried("glowlamp")):
            return "Trantor is dark. The yacht's locker contains a glowlamp. OPEN LOCKER, TAKE GLOWLAMP, then SEARCH RUBBLE."
        return "SEARCH THE RUBBLE on the Trantor surface to find the stair to the Imperial Library."
    if not g.has("archive_open"):
        return "Show your Foundation credentials to the caretaker in the library atrium. SHOW CREDENTIALS TO CARETAKER."
    if not g.has("atlas_read"):
        return "READ THE STAR ATLAS on the archive worktable. Mis needs a starting point."
    if not g.has("tazenda_known"):
        return "Ask Magnifico to play for Mis. USE VISI-SONOR ON MIS."
    if not g.has("reached_rossem"):
        if not g.has("course_rossem"):
            return "Return to the yacht and SET COURSE TO ROSSEM. The Tazendian coordinates are now in the nav computer."
        return "PULL THE LAUNCH LEVER. Rossem is waiting."
    if not g.has("elder_talked"):
        return "TALK TO THE ELDER in the village. He knows where the governor lives and where the Mule's ships are landing."
    return "The Elder's farmhouse is east. Go there. The last choice is waiting."


def act3_on_start(g: "Game") -> None:
    g.set_flag("yacht_at_kalgan")
    g.world.npcs["toran"].location = "kalgan_promenade"
    g.world.npcs["magnifico"].location = "kalgan_promenade"


def act3_on_enter(g: "Game", room_key: str) -> None:
    if g.has("magnifico_follows") and not g.has("ending_done"):
        g.world.npcs["magnifico"].location = room_key
    if room_key == "yacht_bayta":
        g.world.npcs["toran"].location = "yacht_bayta"
    if room_key == "rossem_farmhouse":
        g.world.npcs["mis"].location = "rossem_farmhouse"
        g.world.npcs["toran"].location = "rossem_farmhouse"
        g.world.npcs["magnifico"].location = "rossem_farmhouse"
    if room_key in ("trantor_ruins", "library_atrium", "library_archive"):
        if g.is_carried("glowlamp"):
            g.set_flag("light")


def act3_on_turn(g: "Game") -> None:
    if g.has("magnifico_follows") and not g.has("ending_done"):
        g.world.npcs["magnifico"].location = g.state.room
    if g.state.room == "rossem_farmhouse" and g.has("final_scene"):
        g.world.npcs["mis"].location = "rossem_farmhouse"
        g.world.npcs["toran"].location = "rossem_farmhouse"
        g.world.npcs["magnifico"].location = "rossem_farmhouse"


def act3_epilogue(g: "Game") -> str:
    if g.meta.ending == QUIET_ENDING:
        return (
            "The Mule's ships leave Rossem without firing a shot. The Tazendian "
            "governor emerges from his compound, discovers that the occupation "
            "has been cancelled, and immediately begins writing a memoir in "
            "which he was never afraid. The Elder burns the memoir.\n\n"
            "On Terminus, the Foundation records a minor disturbance in the "
            "Tazendian sector and files it under NOT OUR PROBLEM. In the ruins "
            "of Trantor, a very old library continues to be a very old library. "
            "The Second Foundation is safe, for now, because a woman on a cold "
            "planet shot a friend before he could finish a sentence.\n\n"
            "The Guide notes that history is made of such sentences, and that "
            "the ones left unfinished are often the kindest."
        )
    if g.meta.ending == OPEN_ENDING:
        return (
            "The Mule's ships leave Rossem in a long, disciplined line. The "
            "Tazendian governor, who has spent the occupation hiding in a "
            "cellar, emerges to discover that the occupation has been "
            "reassigned to Trantor. He is not sure whether this is a promotion.\n\n"
            "On Terminus, the Foundation records a minor disturbance in the "
            "Tazendian sector and files it under NOT OUR PROBLEM. In the ruins "
            "of Trantor, a very old library begins to close its doors. Somewhere "
            "beneath it, a committee of psychologists begins, very quietly, to "
            "revise its estimates.\n\n"
            "The Guide notes that the Second Foundation has been found before, "
            "in stories, and that stories are not the same as safe. It suggests "
            "checking the locks."
        )
    return (
        "The story ends, as most stories do, in a room with a table and too "
        "many people who know too much. The Guide closes the book and checks "
        "that the towel is still there."
    )


# ---------------------------------------------------------------------------
# Supporting dialogue
# ---------------------------------------------------------------------------


def palace_bell_press(g: "Game", obj: Object) -> bool:
    g.say(
        "The bell rings. The major-domo looks at it, then at you, then at the "
        "bell again, as if a bell has never been rung before."
    )
    return True


def blaster_use_with(g: "Game", obj: Object, target: object) -> bool:
    if (
        g.room().key == "rossem_farmhouse"
        and g.has("final_scene")
        and getattr(target, "key", None) == "mis"
    ):
        return finish_final(g, "quiet")
    g.say(
        "You point the blaster at the universe in general. The universe "
        "declines to comment."
    )
    return True


def toran_talk(g: "Game", npc: NPC) -> bool:
    if g.has("magnifico_follows"):
        g.say(
            "Toran looks at the clown, then at you, then at the clown again. "
            "'I want to be clear,' he says, 'that I married you for your "
            "judgment. I am now questioning the judgment that brought us a "
            "clown and a stolen musical instrument on our honeymoon.'"
        )
        g.say("He is smiling. It is the smile of a man who has decided to be brave in advance.")
    else:
        g.say(
            "Toran Darell is a broad, calm man with the expression of someone "
            "who has already checked the exits and is now checking your face. "
            "He has been on Kalgan for three days and has disliked every one "
            "of them."
        )
        g.say(
            "'The Mule owns the port,' he says. 'The yacht is in Hangar 7. We "
            "need a departure pass before anyone decides to nationalise us. "
            "Also, there is a clown on the beach who has been trying to get our "
            "attention for twenty minutes. I am choosing to believe he is not "
            "a metaphor.'"
        )
    return True


def toran_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("kalgan", "mule", "takeover"):
        g.say(
            "'The Mule took Kalgan in a night,' Toran says. 'No battle. The "
            "warlord's fleet simply stopped being loyal. The casinos didn't "
            "even close. That is the part that worries me.'"
        )
        return True
    if text in ("yacht", "hangar", "bayta"):
        g.say(
            "'Hangar 7. She's fuelled and ready. We need an exit pass from the "
            "palace major-domo, who is apparently the most powerful man on "
            "Kalgan after the Mule and the head chef.'"
        )
        return True
    if text in ("magnifico", "clown", "visi sonor"):
        g.say(
            "'The clown is terrified of something,' Toran says. 'It isn't us. "
            "He keeps looking at the palace. Whatever he lost in there, he "
            "wants it back badly enough to trust strangers.'"
        )
        return True
    if text in ("trantor", "star's end", "mis", "library"):
        g.say(
            "'If anyone can find the Second Foundation, it's Ebling Mis,' Toran "
            "says. 'He's on Trantor, in the old Imperial Library. Star's End. "
            "He is also the rudest man in the Galaxy, but he is the rudest man "
            "who knows where the answers are.'"
        )
        return True
    if text in ("second foundation", "plan", "psychohistory"):
        g.say(
            "'The Foundation says the Second Foundation doesn't exist,' Toran "
            "says. 'The Foundation also says the Empire will send help. One of "
            "those is a lie, and the other is a hope.'"
        )
        return True
    return None


def clerk_talk(g: "Game", npc: NPC) -> bool:
    g.say(
        "The desk clerk is a thin, tired man in a uniform that has been "
        "pressed by someone who has stopped caring. He watches the Mule's "
        "guards in the lobby with the expression of a man who has learned to "
        "count them without moving his eyes."
    )
    g.say(
        "'Welcome to the Starfall,' he says. 'The Mule's takeover has been "
        "excellent for tourism. People come for the beaches and stay because "
        "the spaceport is closed. Can I help you?'"
    )
    return True


def clerk_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("palace", "major domo", "majordomo", "staff"):
        g.say(
            "'The palace is north. Staff entrance only. The major-domo runs the "
            "door, the trophies, and the departure passes. He is a stickler for "
            "paperwork and a soft touch for good wine. I did not say that.'"
        )
        return True
    if text in ("uniform", "bellhop", "clothes"):
        g.say(
            "'There is a bellhop uniform in your wardrobe,' the clerk says. "
            "'Your husband packed it. I did not ask why. I have learned not to "
            "ask why.'"
        )
        return True
    if text in ("hangar", "yacht", "bayta", "pass"):
        g.say(
            "'Hangar 7. The Bayta. Beautiful ship. Shame about the departure "
            "pass. The major-domo at the palace issues them, and he does not "
            "issue them to people who have not completed their business, paid "
            "their bills, and complimented his desk.'"
        )
        return True
    if text in ("wine", "minibar", "whiskey"):
        g.say(
            "'The minibar has a bottle of Terminus Reserve,' the clerk says. "
            "'The major-domo has a weakness for it. You did not hear that from "
            "me. You heard it from the potted plant.'"
        )
        return True
    if text in ("mule", "guards", "palace"):
        g.say(
            "'The Mule is not what you expect,' the clerk says. 'He is smaller. "
            "He is quieter. He looks at people as if he is reading a page they "
            "have not finished writing. That is all I will say. I have a "
            "family.'"
        )
        return True
    return None


def dockmaster_talk(g: "Game", npc: NPC) -> bool:
    g.say(
        "The dockmaster is a weathered woman with grease under her nails and "
        "a clipboard that has seen service in three wars and one customs "
        "dispute. She looks at your pass, then at you, then at the pass again."
    )
    g.say(
        "'You have a pass,' she says. 'So I don't have to shoot you. That's a "
        "good start. The Bayta is in berth seven. She's fuelled. Don't scratch "
        "the paint. The Mule charges for paint.'"
    )
    return True


def dockmaster_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("yacht", "bayta", "ship"):
        g.say(
            "'She's a Foundation yacht,' the dockmaster says. 'Small, fast, and "
            "built for people who expect to survive their mistakes. You'll "
            "like her.'"
        )
        return True
    if text in ("pass", "departure", "papers"):
        g.say(
            "'Keep the pass on you,' she says. 'The hangar guards collect them "
            "as souvenirs. The Mule encourages initiative.'"
        )
        return True
    if text in ("trantor", "star's end", "library"):
        g.say(
            "'Old Imperial lanes still work,' she says. 'Trantor is the centre. "
            "Star's End. Nothing there now but metal, libraries, and the kind of "
            "silence that makes pilots talk to themselves.'"
        )
        return True
    if text in ("mule", "palace"):
        g.say(
            "'He came in a night,' the dockmaster says. 'Didn't bomb the "
            "casinos. Didn't burn the hotels. Just walked in and stopped being "
            "refused. That's what frightens me.'"
        )
        return True
    return None


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------


def build() -> World:
    rooms: dict[str, Room] = {
        "kalgan_promenade": Room(
            key="kalgan_promenade",
            name="Kalgan Promenade, First Beach",
            desc=(
                "Kalgan is the Galaxy's pleasure planet: a world of white sand, "
                "neon hotels, gambling halls, and the cheerful assumption that "
                "tomorrow will be paid for by somebody else. The Mule's "
                "takeover has not improved the weather, but it has improved the "
                "banners. They hang from every lamp post, showing a thin, "
                "serious face above the slogan ORDER, PROSPERITY, AND A "
                "MODEST AMOUNT OF FEAR.\n\n"
                "A newspaper stand displays the Kalgan Daily. A frightened "
                "clown in a coat much too large for him stands at the edge of "
                "the beach, trying to look as if he belongs to the scenery. He "
                "is failing.\n\n"
                "The Hotel Starfall is east. The Mule's palace dominates the "
                "hill to the north, all white stone and borrowed grandeur. "
                "South, past the promenade, is the hangar district where your "
                "yacht is docked."
            ),
            brief="The Kalgan promenade: sunlight, banners, and a clown pretending to be furniture.",
            coords=(0, 0),
            map_label="Promenade",
            exits={
                "east": Exit(dest="hotel_lobby", label="Hotel Starfall"),
                "north": Exit(
                    dest="mule_palace",
                    label="Mule's palace",
                    condition=palace_condition,
                    blocked=(
                        "A palace guard blocks the way. 'Staff only,' he says, "
                        "looking at your tourist clothes. 'The Mule does not "
                        "receive honeymooners.'"
                    ),
                ),
                "south": Exit(
                    dest="kalgan_hangar",
                    label="hangar district",
                    condition=hangar_condition,
                    blocked=(
                        "A dockmaster at the edge of the hangar district checks "
                        "your papers and finds them lacking. 'No departure pass, "
                        "no hangar,' he says. 'The Mule is very firm on that "
                        "point, and also on most other points.'"
                    ),
                ),
            },
        ),
        "hotel_lobby": Room(
            key="hotel_lobby",
            name="Hotel Starfall, Lobby",
            desc=(
                "The Hotel Starfall is everything a honeymoon brochure promises "
                "and nothing a building inspector would approve. A fountain "
                "shaped like a spiral galaxy burbles in the centre of the "
                "marble floor. The ceiling is painted with constellations, "
                "several of which have been renamed after the Mule's generals.\n\n"
                "A desk clerk watches the door with the wary hospitality of "
                "someone who has learned that guests and conquerors use the same "
                "entrance. A lift at the back of the lobby goes up to the "
                "honeymoon suite."
            ),
            brief="The Starfall lobby: marble, a fountain, and a clerk who has seen everything twice.",
            coords=(1, 0),
            map_label="Hotel",
            exits={
                "west": Exit(dest="kalgan_promenade", label="promenade"),
                "up": Exit(dest="honeymoon_suite", label="lift to suite"),
            },
        ),
        "honeymoon_suite": Room(
            key="honeymoon_suite",
            name="Honeymoon Suite, Hotel Starfall",
            desc=(
                "The suite is all soft carpets, champagne-coloured curtains, "
                "and furniture designed by someone who believed that love "
                "should be upholstered. A balcony overlooks the hangar district "
                "and the bay beyond it. The bed is enormous. The luggage is "
                "still mostly packed, because the honeymoon had other plans.\n\n"
                "On the desk lies the itinerary. A wardrobe stands against one "
                "wall, a minibar against another, and a suitcase sits open on "
                "the luggage rack, revealing a postcard and the general "
                "disorder of a holiday interrupted by history."
            ),
            brief="A honeymoon suite with a view of the fleet, a wardrobe, and a minibar.",
            coords=(2, 0),
            map_label="Suite",
            exits={"down": Exit(dest="hotel_lobby", label="lobby")},
        ),
        "mule_palace": Room(
            key="mule_palace",
            name="The Mule's Palace, Grand Hall",
            desc=(
                "The palace was a casino before the Mule took Kalgan. The new "
                "management has kept the chandeliers, the marble, and the "
                "general air of expensive chance, but has replaced the roulette "
                "wheels with portraits of a thin, serious man who looks as if "
                "he has never enjoyed a single game.\n\n"
                "The Grand Hall is full of guards who have been told to look "
                "decorative and dangerous at the same time. A major-domo sits "
                "behind a desk at the foot of the stairs, guarding the Mule's "
                "appointments, the Mule's trophies, and the Mule's supply of "
                "good wine. A door east leads to the Hall of Triumphs."
            ),
            brief="The Mule's palace: chandeliers, guards, and a major-domo with a very good memory.",
            coords=(0, 1),
            map_label="Palace",
            exits={
                "south": Exit(dest="kalgan_promenade", label="promenade"),
                "east": Exit(dest="trophy_room", label="Hall of Triumphs"),
            },
        ),
        "trophy_room": Room(
            key="trophy_room",
            name="The Hall of Triumphs",
            desc=(
                "The Hall of Triumphs is a long, cold room lined with glass "
                "cases. The Mule's collection is eclectic: a warlord's ceremonial "
                "sword, a Foundation navigation medal, a bottle of wine from a "
                "planet that no longer exists, and a child's wooden horse with "
                "one ear missing.\n\n"
                "In the centre of the room, on a cushion of black velvet, sits "
                "the Visi-Sonor. It looks like a cross between a musical "
                "instrument and a machine that has been asked to apologise. A "
                "small brass plate reads: PROPERTY OF THE MULE. PLEASE DO NOT "
                "PLAY. THE MULE IS SENSITIVE TO CRITICISM."
            ),
            brief="A trophy hall full of loot, and one instrument that does not look like loot.",
            coords=(1, 1),
            map_label="Trophies",
            exits={"west": Exit(dest="mule_palace", label="Grand Hall")},
        ),
        "kalgan_hangar": Room(
            key="kalgan_hangar",
            name="Hangar 7, Kalgan Port",
            desc=(
                "Hangar 7 is a cathedral of steel and bad lighting. Ships of a "
                "dozen makes stand in numbered berths, their hulls daubed with "
                "the insignia of owners who have recently become former owners. "
                "Mechanics move between them with the unhurried efficiency of "
                "people who are paid by the hour and not by the revolution.\n\n"
                "In berth seven, small and sleek and stubbornly clean, waits the "
                "Bayta. She is a Foundation yacht, built for two people and a "
                "reasonable amount of luggage, with a hull that has never been "
                "asked to survive a war. A dockmaster watches you from beside a "
                "tool cart."
            ),
            brief="Hangar 7: the Bayta, a dockmaster, and a great deal of somebody else's fleet.",
            coords=(0, -1),
            map_label="Hangar",
            exits={
                "north": Exit(dest="kalgan_promenade", label="promenade"),
                "yacht": Exit(dest="yacht_bayta", label="the Bayta"),
            },
        ),
        "yacht_bayta": Room(
            key="yacht_bayta",
            name="The Bayta, Cabin",
            desc=(
                "The Bayta's cabin is compact, clean, and designed for two "
                "people who like each other. A pilot's seat faces a viewport "
                "full of whatever port you are currently parked in. A nav "
                "computer glows softly beside the console, its cursor blinking "
                "with the patience of a machine that has never been in a hurry.\n\n"
                "A storage locker is set into the rear bulkhead. Beside the "
                "console, a launch lever waits under a safety cover. The cabin "
                "smells faintly of coffee, ozone, and the particular optimism "
                "of a ship that has not yet been shot at."
            ),
            brief="The Bayta's cabin: a nav computer, a locker, and a launch lever with opinions.",
            coords=(0, -2),
            map_label="Bayta",
            exits={
                "out": Exit(
                    dest="kalgan_hangar",
                    label="hatch",
                    on_use=leave_yacht,
                ),
            },
        ),
        "trantor_ruins": Room(
            key="trantor_ruins",
            name="The Ruins of Trantor, Star's End",
            desc=(
                "The surface of Trantor is a metal plain stretching to a grey "
                "horizon. Once this planet was the capital of the Galaxy, a "
                "single city covering a world, its towers rising into an "
                "artificial sky. Now the sky is real and the towers are fallen. "
                "Rust-coloured domes sag between drifts of debris. A dead "
                "monorail line runs east into the haze like a sentence that has "
                "lost its verb.\n\n"
                "Nearby, a collapsed section of dome has left a mountain of "
                "rubble. The Bayta stands on a cracked landing apron, her hull "
                "the only clean thing for a hundred miles.\n\n"
                "It is dark. Somewhere beneath the rubble, according to the "
                "Guide's more optimistic footnotes, is the Imperial Library."
            ),
            brief="A dark metal plain, a mountain of rubble, and the Bayta.",
            coords=(4, 0),
            map_label="Trantor",
            dark=True,
            exits={
                "down": Exit(
                    dest="library_atrium",
                    label="stair into the Library",
                    condition=lambda g: g.has("library_found"),
                    blocked=(
                        "You can see no way down. The rubble has not been "
                        "searched. SEARCH RUBBLE."
                    ),
                ),
                "yacht": Exit(
                    dest="yacht_bayta",
                    label="the Bayta",
                    condition=lambda g: g.has("yacht_at_trantor"),
                    blocked="The Bayta is not here. The Guide checks the parking orbit.",
                ),
            },
        ),
        "library_atrium": Room(
            key="library_atrium",
            name="Imperial Library, Atrium",
            desc=(
                "The Imperial Library of Trantor is a cathedral built for books. "
                "Its atrium rises through five levels of galleries, each one "
                "packed with shelves that disappear into shadow. The shelves "
                "are not empty. They are merely patient. Somewhere above, a "
                "section of roof has fallen in, and a shaft of grey daylight "
                "falls through the dust like a librarian's disapproving stare.\n\n"
                "A card catalogue the size of a small building occupies the "
                "centre of the floor. Beside it, a reading desk holds a brass "
                "plaque. A caretaker moves between the drawers with the "
                "deliberate calm of someone who has survived the end of the "
                "world and still has paperwork.\n\n"
                "A sealed door east leads to the restricted archive."
            ),
            brief="The Library atrium: five galleries of dust, one enormous catalogue, and a caretaker.",
            coords=(4, 1),
            map_label="Library",
            exits={
                "up": Exit(dest="trantor_ruins", label="surface"),
                "east": Exit(
                    dest="library_archive",
                    label="restricted archive",
                    condition=lambda g: g.has("archive_open"),
                    blocked=(
                        "The archive door is sealed by a lock older than the "
                        "Empire and newer than the caretaker's patience. The "
                        "caretaker could open it, with the right credentials."
                    ),
                ),
            },
        ),
        "library_archive": Room(
            key="library_archive",
            name="Restricted Archive, Imperial Library",
            desc=(
                "The restricted archive is a long, low room lined with film "
                "books and filing cabinets. The air is cold and dry, the way "
                "libraries keep their air when they expect to be used for "
                "centuries. A worktable dominates the centre, buried under "
                "notes, star charts, cold coffee, and the remains of several "
                "meals that were abandoned in the middle of an idea.\n\n"
                "Ebling Mis sits behind the table. He is large, untidy, and "
                "surrounded by the particular chaos of a genius who has stopped "
                "noticing furniture. A star atlas lies open beside him.\n\n"
                "A door west leads back to the atrium."
            ),
            brief="The restricted archive: film books, old coffee, and Ebling Mis in his natural habitat.",
            coords=(4, 2),
            map_label="Archive",
            exits={"west": Exit(dest="library_atrium", label="atrium")},
        ),
        "rossem_landing": Room(
            key="rossem_landing",
            name="Rossem Landing Field",
            desc=(
                "The landing field is a rectangle of mud and crushed stone at "
                "the edge of a village that has never needed a name. The Bayta "
                "sits in the middle of it, looking expensive and slightly "
                "embarrassed. A stubby Tazendian patrol craft crouches at the "
                "far end of the field, its crew conspicuously interested in "
                "the horizon.\n\n"
                "Beyond the field, low stone houses cluster around a well. "
                "Fields rise toward a wooded hill. On the hill, a larger "
                "building with a Tazendian flag marks the governor's compound. "
                "The sky is the colour of old pewter, and there are ships in it "
                "that do not belong to Tazenda."
            ),
            brief="A muddy landing field, a village, and too many ships in the sky.",
            coords=(7, 0),
            map_label="Rossem",
            exits={
                "north": Exit(dest="rossem_village", label="village"),
                "yacht": Exit(dest="yacht_bayta", label="the Bayta"),
            },
        ),
        "rossem_village": Room(
            key="rossem_village",
            name="Village of Gentri, Rossem",
            desc=(
                "The village is a huddle of stone houses, wood smoke, and "
                "animals that have learned to ignore soldiers. The streets are "
                "mud. The well is frozen at the edges. A proclamation nailed to "
                "the community board announces, in the flat language of "
                "occupation, that all citizens will cooperate with the "
                "representatives of Tazenda and that the Second Foundation is a "
                "rumour spread by enemies of peace.\n\n"
                "An Elder stands by the well, watching the sky. On the hill "
                "above the village, the governor's compound flies a flag that "
                "is trying very hard to be reassuring. A path east leads to the "
                "Elder's farmhouse."
            ),
            brief="A cold village, a well, a proclamation, and an Elder who knows when to be silent.",
            coords=(7, 1),
            map_label="Village",
            exits={
                "south": Exit(dest="rossem_landing", label="landing field"),
                "east": Exit(
                    dest="rossem_farmhouse",
                    label="Elder's farmhouse",
                    condition=lambda g: g.has("elder_talked"),
                    blocked=(
                        "The path east is not yours to take yet. The Elder is "
                        "watching you. Perhaps you should TALK TO THE ELDER."
                    ),
                ),
            },
        ),
        "rossem_farmhouse": Room(
            key="rossem_farmhouse",
            name="The Elder's Farmhouse",
            desc=(
                "The farmhouse is one long room with a low ceiling, a stone "
                "fireplace, and windows that were built for a warmer planet. A "
                "table occupies the centre. Outside, the wind moves through the "
                "fields and brings the sound of ships."
            ),
            brief="A warm farmhouse, a table, and the sound of ships outside.",
            coords=(8, 1),
            map_label="Farmhouse",
            on_enter=final_scene,
            exits={"west": Exit(dest="rossem_village", label="village")},
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
                "useful object in the known universe. So far it has been used "
                "to wipe champagne off a honeymoon itinerary, to cushion a "
                "blaster in a locker, and to remind you that some things in "
                "the Galaxy are still reliable."
            ),
        ),
        # Kalgan promenade ---------------------------------------------------
        "newspaper": Object(
            key="newspaper",
            names=["newspaper", "kalgan daily", "daily", "paper", "news"],
            short="Kalgan Daily",
            location="kalgan_promenade",
            fixed=True,
            takeable=False,
            readable=(
                "THE KALGAN DAILY\n\n"
                "MULE'S FLEET TAKES KALGAN — WARLORD 'RETIRES'\n\n"
                "The armies of the Mule entered Kalgan today without "
                "resistance. The former warlord is reported to be enjoying a "
                "well-earned retirement in a location the Palace declines to "
                "specify, possibly because it has not been built yet.\n\n"
                "The Mule's representatives promise order, prosperity, and a "
                "modest amount of fear. Hotel prices remain unchanged. The "
                "casinos are open. The beaches are open. The subject of the "
                "Mule's origins remains closed.\n\n"
                "In related news, the Foundation has protested the takeover "
                "and announced a fact-finding mission, which is expected to "
                "find several facts and no fleet.\n\n"
                "Editorial, page 3: WHY THE MULE IS GOOD FOR TOURISM. Letters, "
                "page 4: WHY THE MULE IS NOT GOOD FOR TOURISM. Obituaries, "
                "page 5: A number of people who disagreed with both."
            ),
            on_read=newspaper_read,
            desc="A folded copy of the Kalgan Daily, its headline competing for attention with the Mule's banners.",
        ),
        "mule_banner": Object(
            key="mule_banner",
            names=["banner", "mule banner", "poster", "slogan"],
            short="Mule banner",
            location="kalgan_promenade",
            fixed=True,
            takeable=False,
            readable=(
                "ORDER. PROSPERITY. AND A MODEST AMOUNT OF FEAR.\n\n"
                "Beneath the slogan, in smaller letters: THE MULE SEES YOU.\n"
                "Beneath that, in different letters: THE MULE SEES YOUR TOWEL.\n"
                "Beneath that, in very small letters: PLEASE DO NOT CLIMB THE "
                "BANNERS. THIS MEANS YOU."
            ),
            desc="A bright banner showing the Mule's thin, serious face. The face has been slightly improved by a passing bird.",
        ),
        # Hotel lobby --------------------------------------------------------
        "guest_register": Object(
            key="guest_register",
            names=["register", "guest register", "guest book", "book"],
            short="guest register",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            readable=(
                "THE HOTEL STARFALL — GUEST REGISTER\n\n"
                "Mr. and Mrs. Toran Darell — Honeymoon Suite — 3 nights — "
                "paid in advance.\n"
                "Haut Rodric — Ambassador Suite — 1 night — paid in promises.\n"
                "The Mule — Imperial Suite — indefinite — paid in fear.\n"
                "A. Clerk — supply closet — still waiting for the deposit.\n\n"
                "A note in the margin reads: IF THE MULE ASKS, THE HONEYMOON "
                "SUITE IS EMPTY. IF THE HONEYMOONERS ASK, THE MULE IS NOT "
                "HERE. THIS IS CALLED HOSPITALITY."
            ),
            desc="A heavy register, open to a page full of names and careful omissions.",
        ),
        "fountain": Object(
            key="fountain",
            names=["fountain", "spiral fountain", "water"],
            short="fountain",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            desc=(
                "A fountain shaped like a spiral galaxy. The water is recycled, "
                "the galaxy is not. Somewhere in the plumbing, a pump is "
                "humming the first four notes of a song that was popular "
                "before the Empire fell."
            ),
        ),
        "clerk_desk": Object(
            key="clerk_desk",
            names=["desk", "clerk's desk", "reception desk", "counter"],
            short="reception desk",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            surface=True,
            desc="A polished reception desk with a bell, a ledger, and a small sign that says SERVICE WITH A SMILE. THE SMILE IS NOT INCLUDED.",
        ),
        # Honeymoon suite ----------------------------------------------------
        "itinerary": Object(
            key="itinerary",
            names=["itinerary", "honeymoon itinerary", "schedule", "plans"],
            short="honeymoon itinerary",
            location="honeymoon_suite",
            readable=(
                "DARELL HONEYMOON — KALGAN — ITINERARY\n\n"
                "Day 1: Arrive. Beach. Champagne. Ignore the news.\n"
                "Day 2: Palace tour (cancelled). Casino (closed). Beach "
                "(occupied). Champagne (still available).\n"
                "Day 3: Departure. The yacht Bayta is fuelled and waiting in "
                "Hangar 7. A departure pass is required. The hotel recommends "
                "the palace major-domo, who is a stickler for paperwork and a "
                "soft touch for good wine.\n\n"
                "Day 4: (blank)\n"
                "Day 5: (blank)\n\n"
                "A handwritten note at the bottom reads: IF THE GALAXY ENDS "
                "BEFORE DAY 4, WE ARE NOT ASKING FOR A REFUND. — T."
            ),
            on_read=itinerary_read,
            desc="A printed itinerary, already obsolete in several interesting ways.",
        ),
        "wardrobe": Object(
            key="wardrobe",
            names=["wardrobe", "closet", "cupboard"],
            short="wardrobe",
            location="honeymoon_suite",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A large wardrobe full of honeymoon clothes, a spare towel, and "
                "a bellhop uniform that Toran apparently packed as a joke. The "
                "joke has aged better than the champagne."
            ),
        ),
        "uniform": Object(
            key="uniform",
            names=["uniform", "bellhop uniform", "bellboy uniform", "costume", "staff uniform"],
            short="bellhop uniform",
            location="wardrobe",
            wearable=True,
            desc=(
                "A crisp hotel bellhop uniform. It is a size too large, which "
                "is lucky, because it has to conceal a towel, a wallet, and the "
                "general suspicion that you are not a bellhop."
            ),
        ),
        "minibar": Object(
            key="minibar",
            names=["minibar", "mini bar", "fridge", "bar"],
            short="minibar",
            location="honeymoon_suite",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A small minibar stocked with champagne, orange juice, and a "
                "bottle of Terminus Reserve whiskey that has been aged three "
                "weeks and priced as if it had been aged three centuries."
            ),
        ),
        "wine": Object(
            key="wine",
            names=["wine", "whiskey", "whisky", "bottle", "liquor", "drink"],
            short="bottle of whiskey",
            location="minibar",
            desc=(
                "A bottle of Terminus Reserve. The label says AGED THREE WEEKS. "
                "A smaller label says THE WEEKS WERE VERY LONG. A third label, "
                "added by the hotel, says NOT FOR RESALE. A fourth label, added "
                "by a previous guest, says TOO LATE."
            ),
        ),
        "suitcase": Object(
            key="suitcase",
            names=["suitcase", "luggage", "bags", "case"],
            short="suitcase",
            location="honeymoon_suite",
            container=True,
            open=True,
            desc=(
                "An open suitcase containing a postcard, a spare pair of "
                "sandals, and the faint smell of a holiday that was supposed to "
                "last longer."
            ),
        ),
        "postcard": Object(
            key="postcard",
            names=["postcard", "card", "picture"],
            short="postcard",
            location="suitcase",
            readable=(
                "The postcard shows the Kalgan beach at sunset, with the Mule's "
                "palace cunningly cropped out of the picture. On the back, in "
                "Toran's handwriting: 'Wish you were here. Actually, given the "
                "news, perhaps not. — T.'"
            ),
            desc="A postcard of a beach that no longer looks like the picture.",
        ),
        "bed": Object(
            key="bed",
            names=["bed", "honeymoon bed", "mattress"],
            short="bed",
            location="honeymoon_suite",
            fixed=True,
            takeable=False,
            desc="An enormous bed, designed for romance and currently used as a luggage rack.",
        ),
        "balcony": Object(
            key="balcony",
            names=["balcony", "view", "window"],
            short="balcony",
            location="honeymoon_suite",
            fixed=True,
            takeable=False,
            desc=(
                "The balcony overlooks the hangar district and the bay. From "
                "here you can see Hangar 7, the Bayta's berth, and the Mule's "
                "banners moving in the wind like a very expensive weather "
                "forecast."
            ),
        ),
        # Mule's palace ------------------------------------------------------
        "major_domo_desk": Object(
            key="major_domo_desk",
            names=["desk", "major-domo's desk", "majordomo desk", "palace desk"],
            short="major-domo's desk",
            location="mule_palace",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A desk of dark wood, polished to a mirror shine. It contains "
                "an appointment book, a bottle opener, and a small framed "
                "motto: SERVICE IS ETERNAL. The drawer is locked, but the lock "
                "looks decorative."
            ),
        ),
        "mule_portrait": Object(
            key="mule_portrait",
            names=["portrait", "mule portrait", "painting", "picture of the mule"],
            short="portrait of the Mule",
            location="mule_palace",
            fixed=True,
            takeable=False,
            readable=(
                "The portrait shows a thin, pale man with a high forehead and "
                "eyes that are difficult to look at directly. The artist has "
                "given him the expression of a man who has just heard a joke he "
                "does not intend to laugh at.\n\n"
                "A brass plate reads: THE MULE — LIBERATOR OF KALGAN. Beneath "
                "it, in different lettering: HE PREFERS TO BE CALLED 'SIR'. "
                "Beneath that, in pencil: HE PREFERS A LOT OF THINGS."
            ),
            desc="A portrait of the Mule, hung where the casino's lucky wheel used to be.",
        ),
        "palace_bell": Object(
            key="palace_bell",
            names=["bell", "service bell", "desk bell"],
            short="service bell",
            location="mule_palace",
            fixed=True,
            takeable=False,
            on_press=palace_bell_press,
            desc="A small silver bell. It has been polished so often that it looks nervous.",
        ),
        # Hall of Triumphs ---------------------------------------------------
        "trophy_case": Object(
            key="trophy_case",
            names=["trophy case", "glass case", "case", "display case"],
            short="glass trophy case",
            location="trophy_room",
            fixed=True,
            takeable=False,
            container=True,
            open=False,
            openable=True,
            locked=True,
            unlock_key="trophy_key",
            on_open=trophy_case_open,
            desc=(
                "A glass case with a brass lock and a small plaque that reads: "
                "THE MULE'S COLLECTION — PLEASE DO NOT TOUCH, BREATHE ON, OR "
                "OTHERWISE IMPROVE. Inside, on a black velvet cushion, lies the "
                "Visi-Sonor."
            ),
        ),
        "visi_sonor": Object(
            key="visi_sonor",
            names=["visi-sonor", "visi sonor", "sonor", "instrument", "musical instrument"],
            short="Visi-Sonor",
            location="trophy_case",
            on_take=visi_sonor_take,
            on_use_with=visi_sonor_use,
            desc=(
                "The Visi-Sonor is a curved, many-keyed instrument with no "
                "strings and no obvious place to blow into. Its surface is "
                "covered in small lights that pulse very slowly, like the "
                "thoughts of a machine that has decided to keep them to "
                "itself."
            ),
        ),
        "throne": Object(
            key="throne",
            names=["throne", "mule's throne", "chair"],
            short="the Mule's throne",
            location="trophy_room",
            fixed=True,
            takeable=False,
            desc=(
                "A chair built to look like a throne and to feel like a "
                "dentist's waiting room. The Mule apparently used it once, "
                "decided it was uncomfortable, and had it moved to the trophy "
                "hall, where it could be uncomfortable in private."
            ),
        ),
        "trophy_plaque": Object(
            key="trophy_plaque",
            names=["plaque", "brass plaque", "sign"],
            short="brass plaque",
            location="trophy_room",
            fixed=True,
            takeable=False,
            readable=(
                "THE HALL OF TRIUMPHS\n\n"
                "This collection commemorates the Mule's victories, the "
                "generosity of his subjects, and the remarkable number of "
                "objects that have been donated to the cause without their "
                "owners being consulted.\n\n"
                "THE MULE THANKS YOU FOR YOUR CONTRIBUTION."
            ),
            desc="A brass plaque, polished to the point of smugness.",
        ),
        # Hangar -------------------------------------------------------------
        "yacht": Object(
            key="yacht",
            names=["yacht", "bayta", "the bayta", "ship", "foundation yacht"],
            short="the Bayta",
            location="kalgan_hangar",
            fixed=True,
            takeable=False,
            desc=(
                "The Bayta is a small Foundation yacht with a clean lines, a "
                "single jump drive, and the sort of hull that has never been "
                "asked to survive a war. She is fuelled, provisioned, and "
                "waiting in berth seven. BOARD YACHT when you are ready to "
                "leave."
            ),
        ),
        "crates": Object(
            key="crates",
            names=["crates", "cargo", "boxes", "supplies"],
            short="cargo crates",
            location="kalgan_hangar",
            fixed=True,
            takeable=False,
            desc=(
                "Cargo crates stamped with the Mule's insignia and the words "
                "PROPERTY OF THE LIBERATION. Several have been opened. One "
                "contains nothing but packing material and a note that says "
                "THANK YOU FOR YOUR CONTRIBUTION."
            ),
        ),
        "fuel_line": Object(
            key="fuel_line",
            names=["fuel line", "hose", "fuel hose"],
            short="fuel line",
            location="kalgan_hangar",
            fixed=True,
            takeable=False,
            desc="A thick fuel line coiled beside the Bayta. It is warm, which is either normal or a reason to leave sooner.",
        ),
        # Yacht --------------------------------------------------------------
        "locker": Object(
            key="locker",
            names=["locker", "storage locker", "cupboard", "cabinet"],
            short="storage locker",
            location="yacht_bayta",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A storage locker set into the rear bulkhead. It contains "
                "emergency equipment, a glowlamp, a blaster, and the ship's "
                "documentation. The documentation is in a folder labeled "
                "CREDENTIALS, which is the sort of label that makes bureaucracy "
                "feel almost helpful."
            ),
        ),
        "glowlamp": Object(
            key="glowlamp",
            names=["glowlamp", "glow lamp", "lamp", "light", "torch", "flashlight"],
            short="glowlamp",
            location="locker",
            on_take=glowlamp_take,
            desc=(
                "A heavy hand lamp with a cracked casing and a beam strong "
                "enough to embarrass a small star. It is the only thing aboard "
                "that looks designed for Trantor."
            ),
        ),
        "blaster": Object(
            key="blaster",
            names=["blaster", "gun", "weapon", "pistol", "toran's blaster"],
            short="blaster",
            location="locker",
            on_use_with=blaster_use_with,
            desc=(
                "A small, efficient blaster of Foundation manufacture. It has "
                "two settings: OFF and REGRET. The safety is on. The Guide "
                "suggests leaving it that way until the plot requires "
                "otherwise."
            ),
        ),
        "credentials": Object(
            key="credentials",
            names=["credentials", "foundation credentials", "id", "identity card", "papers", "card"],
            short="Foundation credentials",
            location="locker",
            desc=(
                "A slim folder containing your Foundation identity papers. "
                "They identify you as Bayta Darell, citizen of Terminus, "
                "trader's wife, and person of no particular importance. The "
                "last part is, the Guide notes, often the most useful."
            ),
        ),
        "nav_computer": Object(
            key="nav_computer",
            names=["nav computer", "navigation computer", "computer", "console", "course", "nav"],
            short="nav computer",
            location="yacht_bayta",
            fixed=True,
            takeable=False,
            on_set=nav_set,
            on_use=nav_use,
            desc=(
                "A compact navigation console with a screen full of stars and "
                "a cursor waiting for instructions. A label on the casing "
                "reads: SET COURSE TO <DESTINATION>. The computer has been "
                "programmed by someone who believed in clear instructions and "
                "had never met a user."
            ),
        ),
        "launch_lever": Object(
            key="launch_lever",
            names=["launch lever", "lever", "throttle", "launch control", "launch"],
            short="launch lever",
            location="yacht_bayta",
            fixed=True,
            takeable=False,
            on_pull=launch_pull,
            on_use=launch_use,
            desc=(
                "A heavy lever under a safety cover. PULL LEVER to launch. The "
                "cover has been engraved with the words DO NOT PULL UNTIL THE "
                "COURSE IS SET, which is the closest the ship's designer ever "
                "came to poetry."
            ),
        ),
        "pilot_seat": Object(
            key="pilot_seat",
            names=["pilot seat", "seat", "chair"],
            short="pilot's seat",
            location="yacht_bayta",
            fixed=True,
            takeable=False,
            desc="A pilot's seat worn into the shape of someone who has spent a lot of time saying 'hold on'.",
        ),
        "viewport": Object(
            key="viewport",
            names=["viewport", "window", "screen"],
            short="viewport",
            location="yacht_bayta",
            fixed=True,
            takeable=False,
            desc=(
                "The viewport currently shows whichever port the Bayta is "
                "parked in. It is very good at showing ports and very bad at "
                "showing what is about to happen."
            ),
        ),
        "ship_log": Object(
            key="ship_log",
            names=["ship log", "log", "logbook", "flight log"],
            short="ship's log",
            location="yacht_bayta",
            fixed=True,
            takeable=False,
            readable=(
                "BAYTA — FLIGHT LOG\n\n"
                "Kalgan to Terminus: uneventful.\n"
                "Terminus to Kalgan: honeymoon.\n"
                "Kalgan to ???: pending.\n\n"
                "A note in Toran's hand: 'If we have to run, Trantor is the "
                "oldest library in the Galaxy. Ebling Mis is there. He will "
                "know what the Mule is looking for, or he will know someone who "
                "does. After that, we improvise.'\n\n"
                "Another note, in Bayta's hand: 'We are very good at "
                "improvising. It is the only thing we packed.'"
            ),
            desc="The Bayta's flight log, half filled with ordinary journeys and one very large blank.",
        ),
        # Trantor ------------------------------------------------------------
        "rubble": Object(
            key="rubble",
            names=["rubble", "debris", "mound", "collapse", "ruins"],
            short="mountain of rubble",
            location="trantor_ruins",
            fixed=True,
            takeable=False,
            on_search=rubble_search,
            desc=(
                "A mountain of broken dome, twisted girders, and the remains of "
                "a statue that may once have been an Emperor. Somewhere under "
                "it, according to the Guide's more optimistic footnote, is a "
                "stair."
            ),
        ),
        "stair": Object(
            key="stair",
            names=["stair", "stairs", "staircase", "way down"],
            short="stair into the Library",
            location="trantor_ruins",
            fixed=True,
            takeable=False,
            hidden=True,
            desc=(
                "A spiral stair descends into the metal skin of Trantor. "
                "Emergency globes glow at intervals, lighting the way down to "
                "the Imperial Library."
            ),
        ),
        "fallen_statue": Object(
            key="fallen_statue",
            names=["statue", "fallen statue", "emperor", "monument"],
            short="fallen statue",
            location="trantor_ruins",
            fixed=True,
            takeable=False,
            readable=(
                "The statue's face has been worn away by weather and, more "
                "recently, by people who needed something to throw. A plaque at "
                "its base reads: TO THE ETERNAL GLORY OF THE EMPIRE. Beneath "
                "it, someone has scratched: IT WAS NICE WHILE IT LASTED."
            ),
            desc="A fallen statue of an Emperor, face down in the dust of his capital.",
        ),
        # Imperial Library ---------------------------------------------------
        "catalogue": Object(
            key="catalogue",
            names=["catalogue", "catalog", "card catalogue", "index", "card index"],
            short="card catalogue",
            location="library_atrium",
            fixed=True,
            takeable=False,
            readable=(
                "IMPERIAL LIBRARY — CARD CATALOGUE\n\n"
                "Drawer 1: A—AM. Drawer 2: AN—AZ. Drawer 3: B—BA. ...\n"
                "Drawer 3,142: PSYCHOHISTORY — SELDON, H. — RESTRICTED.\n"
                "Drawer 3,143: PSYCHOHISTORY — SECOND FOUNDATION — SEE ALSO: "
                "WISHFUL THINKING; POLITICAL SCIENCE; FICTION.\n\n"
                "A handwritten card in Drawer 3,143 reads: 'The answer is not "
                "in the catalogue. The catalogue is in the answer. Ask Mis. He "
                "has been asking for forty years.'"
            ),
            desc="A card catalogue the size of a small building, its drawers labelled in a hand that predates the Empire.",
        ),
        "archive_door": Object(
            key="archive_door",
            names=["archive door", "door", "sealed door", "restricted door"],
            short="archive door",
            location="library_atrium",
            fixed=True,
            takeable=False,
            desc=(
                "A tall door of dark metal, sealed with a lock that looks more "
                "bureaucratic than mechanical. A small plate reads: RESTRICTED "
                "ARCHIVE — FOUNDATION CREDENTIALS REQUIRED. The caretaker has "
                "the only other key, and the caretaker has opinions."
            ),
        ),
        "plaque": Object(
            key="plaque",
            names=["plaque", "brass plaque", "library plaque", "sign"],
            short="library plaque",
            location="library_atrium",
            fixed=True,
            takeable=False,
            readable=(
                "THE IMPERIAL LIBRARY OF TRANTOR\n\n"
                "Founded in the reign of Emperor Aburanis. Rebuilt after the "
                "fire of 2,143. Rebuilt after the fire of 4,902. Rebuilt after "
                "the sack of Trantor, although nobody is entirely sure by whom.\n\n"
                "SILENCE IS REQUESTED. SO IS OPTIMISM, BUT WE ARE LESS "
                "STRICT ABOUT THAT."
            ),
            desc="A brass plaque that has survived several empires and at least three fires.",
        ),
        "reading_desk": Object(
            key="reading_desk",
            names=["reading desk", "desk", "table"],
            short="reading desk",
            location="library_atrium",
            fixed=True,
            takeable=False,
            surface=True,
            desc="A long reading desk with green lamps, brass fittings, and a small sign that says QUIET PLEASE. The sign has been amended in pencil to say QUIET PLEASE, THE UNIVERSE IS TRYING TO THINK.",
        ),
        # Restricted archive ------------------------------------------------
        "star_atlas": Object(
            key="star_atlas",
            names=["star atlas", "atlas", "star chart", "charts", "map"],
            short="Imperial star atlas",
            location="library_archive",
            fixed=True,
            takeable=False,
            readable=(
                "IMPERIAL STAR ATLAS — VOLUME XVII: THE CENTRAL WORLDS\n\n"
                "TRANTOR (STAR'S END): the capital of the Galactic Empire, "
                "population forty billion, surface entirely urbanised, location "
                "of the Imperial Library and the Imperial Palace. Current "
                "status: depopulated, ruined, administratively closed.\n\n"
                "TAZENDA: minor oligarchy, twenty-seven inhabited worlds, "
                "agricultural, strategically insignificant. Local legend claims "
                "that 'Tazenda' is a corruption of 'Star's End'. Imperial "
                "scholars regard this as a folk etymology and a very old joke.\n\n"
                "ROSSEM: agricultural world in the Tazendian sphere. Population "
                "small. Exports: grain, furs, and silence.\n\n"
                "A note in Mis's hand: 'The joke is on the scholars. Star's End "
                "is not a place at the edge. It is the place at the centre. The "
                "oldest joke in the Galaxy is a set of coordinates.'"
            ),
            on_read=star_atlas_read,
            desc="A huge star atlas open to the central worlds. The paper smells of dust and old certainties.",
        ),
        "mis_notes": Object(
            key="mis_notes",
            names=["notes", "mis's notes", "papers", "research", "equations"],
            short="Mis's notes",
            location="library_archive",
            fixed=True,
            takeable=False,
            readable=(
                "The notes are a blizzard of equations, arrows, and insults "
                "directed at the Imperial Census Bureau. One page is headed "
                "STAR'S END — CANDIDATE WORLDS and contains a list that has been "
                "crossed out, rewritten, and finally reduced to two words: "
                "TRANTOR. CENTRE.\n\n"
                "Another page reads: 'The Mule is not an accident. He is a "
                "single individual with a talent that psychohistory cannot "
                "model. The Second Foundation must have a plan for him. If they "
                "do not, then the Plan is not a plan. It is a hope with "
                "footnotes.'"
            ),
            desc="Ebling Mis's research notes, organised by a system known only to Ebling Mis.",
        ),
        "worktable": Object(
            key="worktable",
            names=["worktable", "table", "desk"],
            short="archive worktable",
            location="library_archive",
            fixed=True,
            takeable=False,
            surface=True,
            desc="A worktable buried under notes, cold coffee, and the remains of several meals that were abandoned mid-thought.",
        ),
        "film_books": Object(
            key="film_books",
            names=["film books", "film books", "books", "microfilm", "records"],
            short="film books",
            location="library_archive",
            fixed=True,
            takeable=False,
            desc=(
                "Racks of film books, the compact memory of the Empire. Each "
                "one contains a small library. Most of them are covered in dust. "
                "A few have been pulled out recently and left open, as if "
                "someone has been reading very fast and very desperately."
            ),
        ),
        "coffee_pot": Object(
            key="coffee_pot",
            names=["coffee", "coffee pot", "pot", "caffeine"],
            short="coffee pot",
            location="library_archive",
            fixed=True,
            takeable=False,
            desc=(
                "A coffee pot that has been kept warm since before the Mule "
                "took Kalgan. The coffee inside has achieved a state that is "
                "either very strong or legally alive."
            ),
        ),
        # Rossem -------------------------------------------------------------
        "tazendian_ship": Object(
            key="tazendian_ship",
            names=["tazendian ship", "patrol ship", "ship", "patrol craft"],
            short="Tazendian patrol ship",
            location="rossem_landing",
            fixed=True,
            takeable=False,
            desc=(
                "A stubby patrol craft assembled from spare parts and "
                "self-respect. It is not a warship. It is the sort of ship a "
                "small empire sends to remind a poor world that it is still an "
                "empire, which is cheaper than sending a fleet."
            ),
        ),
        "landing_beacon": Object(
            key="landing_beacon",
            names=["beacon", "landing beacon", "light", "tower"],
            short="landing beacon",
            location="rossem_landing",
            fixed=True,
            takeable=False,
            desc="A landing beacon blinking into the grey sky. It has been blinking for a long time and has the air of a lighthouse keeper who has stopped expecting ships.",
        ),
        "proclamation": Object(
            key="proclamation",
            names=["proclamation", "notice", "announcement", "poster"],
            short="Tazendian proclamation",
            location="rossem_village",
            fixed=True,
            takeable=False,
            readable=(
                "BY ORDER OF THE GOVERNOR OF ROSSEM\n\n"
                "1. All citizens will cooperate with the representatives of "
                "Tazenda.\n"
                "2. All rumors concerning the so-called 'Second Foundation' are "
                "false and will be reported to the governor.\n"
                "3. All visitors from the Foundation will present themselves at "
                "the governor's compound for registration.\n"
                "4. The tax on grain remains unchanged, because the governor is "
                "a reasonable man and the harvest has been poor.\n\n"
                "A handwritten note at the bottom reads: THE GOVERNOR IS A "
                "REASONABLE MAN. THE MULE IS NOT. — A FRIEND."
            ),
            desc="A proclamation nailed to the community board, already curling at the edges.",
        ),
        "well": Object(
            key="well",
            names=["well", "water well", "village well"],
            short="village well",
            location="rossem_village",
            fixed=True,
            takeable=False,
            desc="A stone well with a wooden roof and a bucket on a rope. The water is cold, honest, and probably the only thing in the village that has never been taxed.",
        ),
        "community_board": Object(
            key="community_board",
            names=["board", "community board", "notice board"],
            short="community board",
            location="rossem_village",
            fixed=True,
            takeable=False,
            desc="A board for proclamations, lost animals, and the occasional poem. The proclamation takes up most of it. Someone has pinned a recipe for turnip soup beside it, either as an act of defiance or as a comment on the occupation.",
        ),
        "governor_hill": Object(
            key="governor_hill",
            names=["hill", "governor's compound", "compound", "governor's house"],
            short="governor's compound",
            location="rossem_village",
            fixed=True,
            takeable=False,
            desc=(
                "The governor's compound sits on the hill above the village, "
                "all white walls and a flag that has been designed to be seen "
                "from a distance and trusted from none. Soldiers move around it "
                "with the nervous efficiency of men who have been told that the "
                "Mule is watching."
            ),
        ),
        "supply_cart": Object(
            key="supply_cart",
            names=["cart", "supply cart", "wagon"],
            short="supply cart",
            location="rossem_village",
            fixed=True,
            takeable=False,
            desc="A farm cart loaded with grain sacks and a broken wheel. It is the only vehicle in the village, and it is currently being used as a seat.",
        ),
        # Farmhouse ----------------------------------------------------------
        "table": Object(
            key="table",
            names=["table", "farmhouse table", "kitchen table"],
            short="farmhouse table",
            location="rossem_farmhouse",
            fixed=True,
            takeable=False,
            surface=True,
            desc="A scarred wooden table. It has hosted meals, arguments, births, deaths, and now a psychohistorical crisis.",
        ),
        "fire": Object(
            key="fire",
            names=["fire", "fireplace", "hearth"],
            short="fireplace",
            location="rossem_farmhouse",
            fixed=True,
            takeable=False,
            desc="A small fire in a stone hearth. It is doing its best, which is all anyone can ask of a fire on Rossem.",
        ),
        "window": Object(
            key="window",
            names=["window", "farmhouse window"],
            short="window",
            location="rossem_farmhouse",
            fixed=True,
            takeable=False,
            desc="A small window full of dark fields and the running lights of the Mule's ships.",
        ),
        "mis_chair": Object(
            key="mis_chair",
            names=["chair", "mis's chair", "wooden chair"],
            short="Ebling Mis's chair",
            location="rossem_farmhouse",
            fixed=True,
            takeable=False,
            desc="A wooden chair with a broken back. Ebling Mis has been sitting in it for three hours and has not noticed.",
        ),
        # Items created by events -------------------------------------------
        "exit_pass": Object(
            key="exit_pass",
            names=["exit pass", "departure pass", "pass", "permit", "papers"],
            short="departure pass",
            location=None,
            desc=(
                "A stiff card stamped with the Mule's seal and the words "
                "DEPARTURE AUTHORISED. It is the sort of document that makes "
                "one feel important and slightly criminal at the same time."
            ),
        ),
        "trophy_key": Object(
            key="trophy_key",
            names=["trophy key", "key", "small key", "brass key"],
            short="trophy key",
            location=None,
            desc=(
                "A small brass key, warm from the major-domo's pocket. It opens "
                "the glass case in the Hall of Triumphs. It also opens the "
                "question of what the Mule values enough to lock up."
            ),
        ),
    }

    npcs: dict[str, NPC] = {
        "toran": NPC(
            key="toran",
            names=["toran", "toran darell", "husband", "torie"],
            short="Toran Darell",
            location="kalgan_promenade",
            desc=(
                "Toran Darell is a broad, calm man with the expression of "
                "someone who has already checked the exits and is now checking "
                "your face. He is a Foundation trader, a good pilot, and a "
                "husband who has recently discovered that honeymoons are not "
                "exempt from galactic history."
            ),
            topics={
                "kalgan": "The Mule took Kalgan in a night. No battle. The casinos didn't even close.",
                "yacht": "Hangar 7. The Bayta is fuelled. We need a departure pass from the palace major-domo.",
                "magnifico": "The clown is terrified of something. It isn't us.",
                "trantor": "Ebling Mis is on Trantor, in the Imperial Library. Star's End. He knows the answers.",
                "second foundation": "The Foundation says it doesn't exist. The Foundation also says the Empire will send help.",
            },
            on_talk=toran_talk,
            on_ask=toran_topics,
        ),
        "desk_clerk": NPC(
            key="desk_clerk",
            names=["clerk", "desk clerk", "receptionist", "hotel clerk", "front desk"],
            short="Desk Clerk",
            location="hotel_lobby",
            desc=(
                "A thin, tired man in a uniform pressed by someone who has "
                "stopped caring. He watches the Mule's guards with the "
                "expression of a man who has learned to count them without "
                "moving his eyes."
            ),
            topics={
                "palace": "Staff entrance only. The major-domo runs the door and the departure passes.",
                "uniform": "There is a bellhop uniform in your wardrobe. Your husband packed it. I did not ask.",
                "hangar": "Hangar 7. The Bayta. Beautiful ship. Shame about the pass.",
                "wine": "The minibar has a bottle of Terminus Reserve. The major-domo has a weakness.",
                "mule": "Smaller than you expect. Quieter. He reads people like unfinished pages.",
            },
            on_talk=clerk_talk,
            on_ask=clerk_topics,
        ),
        "major_domo": NPC(
            key="major_domo",
            names=["major-domo", "majordomo", "major domo", "domo", "palace official", "servant"],
            short="Major-Domo",
            location="mule_palace",
            desc=(
                "A thin, immaculate man with the eyes of someone who has "
                "counted every spoon in the palace and found the tally wanting. "
                "He guards the Mule's appointments, the Mule's trophies, and the "
                "Mule's supply of good wine with equal severity."
            ),
            topics={
                "visi-sonor": "The clown's instrument is in the Hall of Triumphs. The Mule values it.",
                "pass": "Departure passes are issued by me, to people who have completed their business.",
                "trophy": "The Hall of Triumphs is closed. The Mule's trophies are not for hotel staff.",
                "wine": "The major-domo's eyes flick to the bottle and away, with professional discipline.",
                "mule": "The Mule is not a man to be discussed by staff. I have a pension and a good memory.",
            },
            on_talk=major_domo_talk,
            on_ask=major_domo_topics,
            on_give=major_domo_give,
        ),
        "dockmaster": NPC(
            key="dockmaster",
            names=["dockmaster", "dock master", "hangar guard", "mechanic", "guard"],
            short="Dockmaster Veln",
            location="kalgan_hangar",
            desc=(
                "A weathered woman with grease under her nails and a clipboard "
                "that has seen service in three wars and one customs dispute. "
                "She looks at your pass, then at you, then at the pass again."
            ),
            topics={
                "yacht": "The Bayta is small, fast, and built for people who expect to survive their mistakes.",
                "pass": "Keep it on you. The hangar guards collect them as souvenirs.",
                "trantor": "Old Imperial lanes still work. Star's End. Nothing there but metal and libraries.",
                "mule": "He came in a night. Didn't bomb the casinos. That's what frightens me.",
            },
            on_talk=dockmaster_talk,
            on_ask=dockmaster_topics,
        ),
        "magnifico": NPC(
            key="magnifico",
            names=["magnifico", "magnifico giganticus", "clown", "bobo", "the clown", "mule's clown"],
            short="Magnifico",
            location="kalgan_promenade",
            desc=(
                "A small clown with a long nose, sad brown eyes, and clothes "
                "tailored for a smaller clown and then left in the rain. He "
                "looks like a man who has been running for a long time and has "
                "forgotten which direction is away."
            ),
            topics={
                "visi-sonor": "The Visi-Sonor shows you what you are feeling before you have decided to feel it.",
                "mule": "The Mule is a bad dream. The kind you cannot wake from because it has your shoes.",
                "foundation": "A world of great magic. Fires that consume planets. Secrets of mighty strength.",
                "second foundation": "A story for children. A story to make the dark feel smaller.",
                "kalgan": "The Mule's palace is north. The major-domo likes wine. Everyone likes wine.",
            },
            on_talk=magnifico_talk,
            on_ask=magnifico_topics,
            on_give=magnifico_give,
        ),
        "caretaker": NPC(
            key="caretaker",
            names=["caretaker", "librarian", "archivist", "index", "old librarian"],
            short="The Caretaker",
            location="library_atrium",
            desc=(
                "A small, ancient person wrapped in several libraries' worth of "
                "cardigans. They regard you over the top of a catalogue drawer "
                "with the calm of someone who has survived the sack of Trantor "
                "and several overdue notices."
            ),
            topics={
                "archive": "The restricted archive is east. It requires Foundation credentials.",
                "library": "The Library survived because books are heavy and looters are lazy.",
                "seldon": "Hari Seldon consulted here. He reserved the same desk for forty years.",
                "second foundation": "There is no Second Foundation. There is a restricted archive and a rumour.",
            },
            on_talk=caretaker_talk,
            on_ask=caretaker_topics,
            on_show=caretaker_show,
        ),
        "mis": NPC(
            key="mis",
            names=["mis", "ebling mis", "ebling", "doctor mis", "dr mis", "scientist", "psychohistorian"],
            short="Ebling Mis",
            location="library_archive",
            desc=(
                "A large, untidy man in a stained jacket, smoking a cigar that "
                "violates at least three library regulations. His eyes are "
                "bloodshot, his notes are everywhere, and he has the "
                "single-mindedness of a man who has decided that the universe "
                "is a problem to be solved before dinner."
            ),
            topics={
                "tazenda": "A name in an old atlas. Rossem is a name in a newer one.",
                "star's end": "The centre of the Galaxy. Trantor. The clue was a joke, and the joke was on the scholars.",
                "second foundation": "The Plan's insurance policy. Psychologists at the other end of the Galaxy.",
                "mule": "A single individual outside the equations. Psychohistory cannot predict him.",
                "visi-sonor": "The instrument focuses the mind. Without it I am a clever man with a headache.",
            },
            on_talk=mis_talk,
            on_ask=mis_topics,
            on_attack=mis_attack,
        ),
        "elder": NPC(
            key="elder",
            names=["elder", "elders", "old man", "spokesman", "farmer"],
            short="The Elder",
            location="rossem_village",
            desc=(
                "A brown, weathered man with hands like old roots and the "
                "careful eyes of someone who has spent his life pretending not "
                "to notice armies. He stands by the well as if he has been "
                "standing there since before the Empire."
            ),
            topics={
                "tazenda": "Tazenda rules twenty-seven worlds. Or it says it does.",
                "mule": "The Mule's ships did not bomb us. They landed, asked questions, and left. That is worse.",
                "second foundation": "We do not talk about the Second Foundation. The last man who did was taken to the compound.",
                "rossem": "Rossem is a poor world. Poor worlds are good at keeping secrets.",
                "governor": "The governor lives on the hill. The taxes come every year. The soldiers come when he is afraid.",
            },
            on_talk=elder_talk,
            on_ask=elder_topics,
        ),
    }

    return World(
        act=3,
        title="The Mule",
        subtitle="Kalgan, Trantor, and Rossem, 300 Foundation Era",
        protagonist="Bayta Darell",
        start_room="kalgan_promenade",
        intro=(
            "You are Bayta Darell, on your honeymoon. The honeymoon is on "
            "Kalgan, the Galaxy's pleasure planet, which was until last week "
            "ruled by a warlord and is now ruled by something called the Mule. "
            "The casinos are still open. The beaches are still warm. The "
            "banners are new.\n\n"
            "Your husband Toran is checking the exits. A clown on the beach is "
            "trying not to be noticed. Your yacht, the Bayta, is fuelled and "
            "waiting in Hangar 7, but the Mule's palace controls the departure "
            "passes, and the palace controls almost everything else.\n\n"
            "Somewhere at the centre of the Galaxy, in the ruins of Trantor, "
            "an old psychohistorian is looking for the Second Foundation. The "
            "Mule is looking for it too. The Guide suggests that you find it "
            "first, or at least find a good seat.\n\n"
            "You have a towel. The Guide considers this a promising start."
        ),
        rooms=rooms,
        objects=objects,
        npcs=npcs,
        max_score=100,
        guide_keys=["KALGAN", "THE MULE"],
        hints=act3_hints,
        on_start=act3_on_start,
        on_turn=act3_on_turn,
        on_enter=act3_on_enter,
        on_say=act3_on_say,
        on_command=act3_on_command,
        epilogue=act3_epilogue,
        ending_title="THE UNANSWERED QUESTION",
    )


