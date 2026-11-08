"""Act I — The Psychohistorians.

Gaal Dornick arrives on Trantor, is swept up by Hari Seldon's trial, and
chooses the right ship into exile.  The act is deliberately compact: one
city, one conspiracy, and a suitcase with strong opinions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..model import Exit, NPC, Object, Room, World

if TYPE_CHECKING:  # pragma: no cover
    from ..engine import Game


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

PASSWORD_PHRASES = {"don't panic", "dont panic", "do not panic"}


def _norm(text: str) -> str:
    return " ".join(text.lower().replace("\u2019", "'").split()).strip(" .!")


def _both_cubes(g: "Game", extra: str | None = None) -> None:
    carried = {
        key
        for key, loc in g.state.obj_loc.items()
        if loc == "player" and key in ("prime_radiant", "decoy_cube")
    }
    if extra == "prime_radiant":
        carried.add("prime_radiant")
    if extra == "decoy_cube":
        carried.add("decoy_cube")
    if {"prime_radiant", "decoy_cube"} <= carried and not g.has("both_cubes_seen"):
        g.set_flag("both_cubes_seen")
        g.say(
            "You now hold both cubes. One is warm and hums in prime numbers. The "
            "other is cold and has the moral texture of a warranty. The Guide "
            "suggests keeping track of which is which."
        )


def towel_receive(g: "Game", towel: Object, obj: Object) -> None:
    if obj.key == "prime_radiant" and not g.has("cube_hidden"):
        g.set_flag("cube_hidden")
        g.award_once("hide_cube", 5, "Hid the Prime Radiant in a towel. The oldest security system.")
        g.say(
            "The Prime Radiant settles into the folds of the towel. Its humming "
            "drops to a polite murmur, like a mathematician who has been asked to "
            "wait in the corridor."
        )
        g.say(
            "The towel now has the approximate weight and moral authority of a "
            "small constitutional crisis."
        )
    return None


def _open_old_wing(g: "Game", trigger: str) -> None:
    if g.has("old_wing_open"):
        g.say("The old wing arch is already open. It creaks politely as you approach.")
        return
    g.set_flag("old_wing_open")
    g.award_once("password", 3, "A password worth three points and several centuries.")
    g.unlock_guide("PSYCHOHISTORY")
    g.say(
        "The words hang in the air like a badly tuned chord. Somewhere inside the "
        "statue, a very old mechanism decides that this is close enough to the "
        "password it was given in a more optimistic century."
    )
    g.say(
        "A service arch at the edge of the plaza grinds open. Beyond it, a corridor "
        "smells of dust, ozone, and academic tenure."
    )


# ---------------------------------------------------------------------------
# Spaceport
# ---------------------------------------------------------------------------

def suitcase_take(g: "Game", obj: Object) -> None:
    if not g.has("suitcase_taken"):
        g.set_flag("suitcase_taken")
        g.award(5, "Luggage recovered from an Imperial carousel.")
        g.say(
            "The suitcase is heavier than a week's clothes and lighter than a "
            "lifetime of regrets. A small tag reads: PROPERTY OF G. DORNICK. "
            "PLEASE DO NOT LOSE. THE GALAXY HAS ENOUGH PROBLEMS."
        )
    return None


def letter_read(g: "Game", obj: Object) -> None:
    g.award_once("seldon_letter", 5, "A letter from Hari Seldon.")
    g.unlock_guide("PSYCHOHISTORY")
    return None


def pedestal_use(g: "Game", obj: Object, target: object) -> bool:
    if target is None:
        g.say(
            "The security pedestal has a slot the exact shape of an Imperial visa, "
            "and the exact personality of a mid-level bureaucrat."
        )
        g.say(g.ui.dim("Try: USE VISA ON PEDESTAL."))
        return True
    if getattr(target, "key", None) != "visa":
        g.say(
            "The pedestal scans the object, emits a disappointed beep, and displays "
            "a notice: UNRECOGNISED DOCUMENT. SEE ALSO: YOUR FAILURE TO FOLLOW "
            "INSTRUCTIONS."
        )
        return True
    if g.has("security_cleared"):
        g.say("The pedestal has already stamped your visa. It is now sulking in standby mode.")
        return True
    g.set_flag("security_cleared")
    g.award_once("visa_stamp", 5, "A visa stamped by the only machine on Trantor with job security.")
    g.say(
        "The pedestal reads your visa, stamps it with a sound like a small legal "
        "execution, and prints a receipt. The receipt says KEEP THIS RECEIPT. "
        "There is no space to write what for."
    )
    g.say("A gate at the north end of the arrival hall clicks open.")
    return True


def itinerary_read(g: "Game", obj: Object) -> None:
    g.say(
        g.ui.dim(
            "The itinerary is printed on paper so thin it is already apologising. "
            "Reservations: Luxor Hotel, Imperial Sector. Occupation: mathematician. "
            "Purpose of visit: attending a lecture by Hari Seldon. Risk assessment: "
            "pending."
        )
    )
    return True


# ---------------------------------------------------------------------------
# Taxi queue
# ---------------------------------------------------------------------------

def fare_machine_use(g: "Game", obj: Object, target: object) -> bool:
    if target is None:
        g.say(
            "The fare machine displays a fare, a surcharge, a toll, a tax, and a "
            "line item labelled MISC. It accepts credit chips because cash is for "
            "people with simpler planets."
        )
        g.say(g.ui.dim("Try: USE CREDIT CHIP ON FARE MACHINE."))
        return True
    if getattr(target, "key", None) != "credit_chip":
        g.say(
            "The fare machine rejects the object with a noise normally reserved "
            "for bad poetry. It wants a credit chip."
        )
        return True
    if g.has("fare_paid"):
        g.say("The fare is already paid. The machine prints another receipt anyway, because it can.")
        return True
    g.set_flag("fare_paid")
    g.award_once("taxi_fare", 5, "Public transport: the glue of civilisation.")
    g.say(
        "The credit chip vanishes into the machine. The machine thinks about it "
        "for a moment, then issues a receipt, a seat assignment, and a warning "
        "about the driver's opinions."
    )
    g.say("The taxi door unfolds. The queue behind you applauds the existence of a paying customer.")
    return True


def taxi_use(g: "Game", obj: Object, target: object) -> bool:
    g.say(
        "The taxi is a battered ground-effect vehicle with the words IMPERIAL "
        "TRANSPORT painted over an older slogan about the joys of standing in line."
    )
    g.say(g.ui.dim("If the fare is paid, BOARD TAXI. Otherwise, examine the fare machine."))
    return True


# ---------------------------------------------------------------------------
# Hotel
# ---------------------------------------------------------------------------

def hotel_enter(g: "Game", first: bool) -> None:
    if first:
        g.award_once("hotel_arrival", 5, "Arrival at the Luxor Hotel, where the carpet is thicker than the law.")
        g.say(
            "The taxi deposits you beneath the Luxor's famous chandelier, a structure "
            "the size of a small moon and considerably more expensive to maintain. "
            "The doorman looks at your suitcase and then at you, establishing the "
            "order of importance."
        )


def clerk_show(g: "Game", npc: NPC, obj: Object) -> bool | None:
    if obj.key != "seldon_letter":
        return None
    if g.has("key_card_given"):
        g.say(
            "The clerk has already given you a key card. He suggests, with the "
            "delicacy of a man who has seen everything, that you stop asking."
        )
        return True
    g.set_flag("key_card_given")
    g.state.obj_loc["key_card"] = "player"
    g.unlock_guide("TRANTOR")
    g.say(
        "The clerk reads the letter, then reads it again, then reads the signature "
        "a third time. His expression passes through several grades of Imperial "
        "service before settling on 'I have never seen this letter in my life.'"
    )
    g.say(
        "He produces a key card. 'Suite fourteen,' he says. 'The elevator is "
        "temperamental. The guest is not. Please do not mention the water pressure.'"
    )
    g.say("He hands you the key card, then looks around to make sure no one is watching him be helpful.")
    return True


def clerk_talk(g: "Game", npc: NPC) -> bool | None:
    g.say(
        "The clerk's name badge says WELCOME TO THE LUXOR. His face says I HAVE "
        "BEEN WELCOMING PEOPLE TO THE LUXOR FOR ELEVEN YEARS."
    )
    g.say(
        "He is, however, one of the few people on Trantor who understands that "
        "a guest holding a letter from Hari Seldon is either important, in danger, "
        "or both. He has decided that both is the safer assumption."
    )
    return True


def clerk_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("room", "suite", "key", "key card", "my room"):
        g.say(
            "The clerk points at the elevator. 'Fourteenth floor. The card opens the "
            "suite and, if you are lucky, the minibar. The minibar is a metaphor.'"
        )
        return True
    if text in ("seldon", "hari seldon", "professor"):
        g.say(
            "The clerk lowers his voice. 'Seldon is at Streeling University. Has a "
            "little office behind the old wing. The Commission pretends not to know "
            "where it is, which is how you can tell they do.'"
        )
        return True
    if text in ("trantor", "planet", "city"):
        g.say(
            "The clerk gestures at the ceiling. 'Everything above us is city. "
            "Everything below us is also city. The difference is the rent.'"
        )
        return True
    if text in ("commission", "police", "safety"):
        g.say(
            "The clerk's smile becomes professionally unavailable. 'The Commission "
            "of Public Safety is here to protect the public from safety. I would "
            "not discuss it near the potted plants. They are wired.'"
        )
        return True
    return None


def holo_use(g: "Game", obj: Object, target: object) -> bool:
    if not g.has("holo_played"):
        g.set_flag("holo_played")
        g.award_once("holo", 10, "A message from the future, delivered by a machine with poor lighting.")
        g.say(
            "The projector coughs, clears several virtual throats, and produces a "
            "life-sized image of a man who looks as if he has been folded and "
            "unfolded by a committee."
        )
        g.say(
            "'Good evening,' says Hari Seldon, or possibly a recording of Hari "
            "Seldon, or possibly a legal entity representing the estate of Hari "
            "Seldon. 'If you are watching this, the Empire is in more trouble than "
            "usual. If you are watching this in a hotel room, it is also in more "
            "trouble than usual, but with better carpets.'"
        )
        g.say(
            "'Find the old wing at Streeling. The door listens for the first rule "
            "of hitchhiking. Do not trust the Commission. And whatever you do, do "
            "not tell them which cube is real.'"
        )
        g.say("The image folds itself back into the projector with a sigh of cheap phosphors.")
        return True
    g.say(
        "The projector replays the message from the beginning. Hari Seldon has "
        "the same expression, the same warning, and slightly worse resolution."
    )
    return True


def library_card_take(g: "Game", obj: Object) -> None:
    g.award_once("library_card", 2, "A library card: the most dangerous document in the room.")
    g.say(
        "The card is warm from the drawer and bears the seal of the Imperial "
        "Library. Under RULES it says QUIET PLEASE. Under FINES it says QUITE."
    )
    return None


def overdue_book_read(g: "Game", obj: Object) -> None:
    g.say(
        g.ui.dim(
            "The book is titled A HISTORY OF THE GALACTIC EMPIRE, VOLUME 12: "
            "DECLINE AND FALL (SELECTED HIGHLIGHTS). The due date is stamped "
            "forty years ago. A handwritten note reads: 'Sorry. The Empire fell "
            "while I was renewing.'"
        )
    )
    return True


# ---------------------------------------------------------------------------
# Plaza
# ---------------------------------------------------------------------------

def student_talk(g: "Game", npc: NPC) -> bool | None:
    g.say(
        "The student is sitting on the base of the statue with the air of someone "
        "who has discovered that the universe is made of problems and has decided "
        "to major in them."
    )
    g.say(
        "'You're Dornick, aren't you? The mathematician from Synnax. Everyone in "
        "the department is talking about you, which on Trantor means three people "
        "and a vending machine.'"
    )
    return True


def student_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("statue", "inscription", "writing", "monument"):
        g.say(
            "'The statue is supposed to commemorate the first settlers of Streeling. "
            "The inscription used to say something about courage and curiosity. "
            "Then the Commission sanded off the parts that sounded political. Now "
            "it says DON'T ... and the rest is weathering.'"
        )
        g.say("He looks at you meaningfully. 'Some passwords survive even bad maintenance.'")
        return True
    if text in ("password", "old wing", "door", "arch", "guide"):
        g.set_flag("password_hint")
        g.say(
            "'The old maintenance arch listens for the first rule of hitchhiking. "
            "Not the second rule, not the third. The first one.' He taps the cover "
            "of a small book sticking out of his pocket. It has large, friendly "
            "letters on it."
        )
        g.say("'Say it. Don't shout it. The arch is sensitive, and so is the librarian.'")
        return True
    if text in ("seldon", "hari seldon", "psychohistory", "plan"):
        g.say(
            "'Seldon is behind the old wing. The Commission is pretending he is not, "
            "which is the closest thing to job security a professor can get. He has "
            "been expecting someone. He is always expecting someone; it is very "
            "annoying to be around.'"
        )
        return True
    if text in ("library", "archive", "card"):
        g.say(
            "'The library has an archive behind the reading room. You need an "
            "Imperial Library card, which the Commission issues only to people they "
            "are not currently arresting. Good luck with that.'"
        )
        return True
    if text in ("commission", "police", "chen"):
        g.say(
            "'Commissioner Linge Chen runs the Commission of Public Safety. He has "
            "the face of a man who has never been wrong in public. If you meet him, "
            "answer the question he asks, not the one you wish he had asked.'"
        )
        return True
    return None


def statue_read(g: "Game", obj: Object) -> None:
    g.say(
        "The inscription is carved into a slab of imitation marble. The original "
        "text has been sanded away in strategic places, leaving:"
    )
    g.say(g.ui.cyan("    IN MEMORY OF THE FIRST SETTLERS OF STREELING"))
    g.say(g.ui.cyan("    WHO FACED THE DARK WITH COURAGE, CURIOSITY, AND A GOOD"))
    g.say(g.ui.cyan("    DON'T ..."))
    g.say(g.ui.dim("(The rest has been removed by the Commission of Public Safety, which regards punctuation as a gateway crime.)"))
    return True


def plaza_panic(g: "Game") -> bool:
    if g.room().key != "streeling_plaza":
        return False
    _open_old_wing(g, "panic")
    return True


# ---------------------------------------------------------------------------
# Library and archive
# ---------------------------------------------------------------------------

def librarian_give(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key != "overdue_book":
        g.say(
            "The librarian examines the offered object, then examines you. 'The "
            "library accepts donations,' she says, 'but not of whatever that is.'"
        )
        return True
    g.state.obj_loc[obj.key] = None
    g.award_once("overdue_book", 2, "Returned a book only forty years late. The fine is waived.")
    g.say(
        "The librarian takes the book, reads the due date, and makes a small "
        "noise that is either amusement or a shelving decision."
    )
    g.say(
        "'Forty years,' she says. 'That's nothing. We have a first edition of the "
        "Encyclopedia Galactica that was returned after the Empire it described "
        "stopped existing. I waived the fine. It was a matter of professional "
        "courtesy.'"
    )
    g.say("She stamps the book RETURNED and puts it on a cart. The cart immediately collapses.")
    return True


def librarian_show(g: "Game", npc: NPC, obj: Object) -> bool | None:
    if obj.key == "library_card":
        g.say(
            "The librarian glances at the card. 'Archive door is behind the reading "
            "room. The lock is old, the card is older, and the cataloguing system "
            "is from a period when hope was still fashionable. Try OPEN ARCHIVE DOOR.'"
        )
        return True
    return None


def librarian_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("archive", "archive door", "card"):
        g.say(
            "'The archive holds the things the Empire decided were too true to "
            "display. Old newspapers, census records, and a very complete collection "
            "of apologies from officials who were later executed. The door opens "
            "with an Imperial Library card.'"
        )
        return True
    if text in ("seldon", "psychohistory", "plan"):
        g.say(
            "'Seldon's people have been copying records for years. They think I "
            "don't notice. I notice everything except the return dates.' She points "
            "at the archive door. 'The truth is in there. So is the heating duct.'"
        )
        return True
    if text in ("book", "overdue", "fine"):
        g.say(
            "'A book is overdue when it is late. A book is a classic when it is "
            "late enough. The distinction is largely administrative.'"
        )
        return True
    if text in ("trantor", "empire", "library"):
        g.say(
            "'The Imperial Library survived the sack of Trantor because looters "
            "dislike carrying books and libraries have excellent basements. We are "
            "the memory of a civilization that has forgotten us. Please keep your "
            "voice down; the memory is napping.'"
        )
        return True
    return None


def data_tape_read(g: "Game", obj: Object) -> None:
    g.award_once("data_tape", 5, "Hard evidence: the Commission's least favourite genre.")
    g.set_flag("data_tape_read")
    g.unlock_guide("ENCYCLOPEDIA GALACTICA")
    return None


def archive_door_open(g: "Game", obj: Object) -> bool | None:
    if g.state.obj_locked.get("archive_door", True):
        g.say(
            "The archive door is locked. A small brass plate reads: AUTHORISED "
            "PERSONNEL ONLY. The brass has been polished by generations of people "
            "who were not authorised personnel."
        )
        return True
    g.say(
        "The archive door swings inward with the sound of a committee adjourning. "
        "Cold air and the smell of old paper drift out."
    )
    return True


def old_wing_enter(g: "Game", first: bool) -> None:
    if first:
        g.say(
            "The corridor is lit by tubes that flicker in a pattern suggesting "
            "either faulty wiring or Morse code. Dust covers the floor except for "
            "a narrow path worn by someone who comes here often and does not want "
            "to be followed."
        )
        g.say("At the far end, a door carries a hand-lettered sign: H. SELDON — KNOCK FIRST. THE MATH IS AT A DELICATE STAGE.")


def office_leave(g: "Game") -> bool:
    if g.has("briefed") and not g.has("arrested"):
        g.set_flag("arrested")
        g.say(
            "You step out of Seldon's office and into a wall of blue uniforms. "
            "The Commission of Public Safety has been waiting with the patience of "
            "an organisation that bills by the hour."
        )
        g.say(
            "A voice from the front says, 'Dr Dornick. The Commission would like a "
            "word. Several words. Possibly a trial.'"
        )
        g.teleport("trial_chamber", first=True)
        return True
    return False


# ---------------------------------------------------------------------------
# Seldon's office
# ---------------------------------------------------------------------------

def seldon_talk(g: "Game", npc: NPC) -> bool | None:
    if not g.has("briefed"):
        g.set_flag("briefed")
        g.award_once("seldon", 15, "Hari Seldon explained the Plan. Your odds improved.")
        g.unlock_guide("PSYCHOHISTORY")
        g.unlock_guide("THE PLAN")
    return None


def seldon_desc(g: "Game") -> str:
    return (
        "Hari Seldon is smaller than his reputation and older than his "
        "photographs. He looks at you as if you are a term in an equation he has "
        "already solved, which is either flattering or alarming depending on your "
        "tolerance for mathematics.\n\n"
        "'You are Dornick,' he says. 'The Synnax papers. Good. I need someone who "
        "can do arithmetic and keep a secret, preferably in that order. The "
        "Commission is about to arrest me, the trial will be a formality, and the "
        "exile will be the point. I am arranging transport. You are coming.'\n\n"
        "He gestures at the desk. 'The Commission will search you. They will find "
        "whatever you leave visible. Take both cubes, hide the warm one, and give "
        "them the cold one. A towel is traditional.'"
    )


def seldon_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("psychohistory", "math", "mathematics", "plan"):
        g.say(
            "'Psychohistory predicts crowds, not people. I can tell you what forty "
            "billion people will do next year. I cannot tell you what one "
            "commissioner will do at lunch. That is why lunch is dangerous.'"
        )
        return True
    if text in ("trial", "commission", "chen", "court"):
        g.say(
            "'Linge Chen will offer you a choice between confession and relevance. "
            "Refuse both. Answer his question with a no. When he demands evidence "
            "of your loyalty, give him a cube. Not the warm one. The cold one.'"
        )
        return True
    if text in ("cube", "prime radiant", "radiant", "decoy", "evidence"):
        g.say(
            "Seldon opens the desk drawer. Inside are two cubes that look, to the "
            "untrained eye, exactly alike. 'The Prime Radiant is warm and hums in "
            "prime numbers. The decoy is cold and hums in slogans. Chen's scanner "
            "is good, but his vanity is better. Give him the decoy and hide the "
            "real one. A towel is traditional.'"
        )
        return True
    if text in ("towel", "hide", "hiding"):
        g.say(
            "'Put the Prime Radiant in your towel. The Commission's scanner has "
            "been calibrated to detect psychohistorical radiation, not laundry. "
            "There is a lesson about bureaucracy in that, but I have a trial to "
            "attend.'"
        )
        return True
    if text in ("terminus", "exile", "ship"):
        g.say(
            "'Terminus. A small planet at the edge of the Galaxy. No metals, no "
            "native life, excellent isolation. The Encyclopedia Galactica will be "
            "compiled there, and in a hundred years the Encyclopedists will "
            "discover that history has plans of its own. Board the ship with the "
            "Encyclopedia's name on it. Not the Imperial one.'"
        )
        return True
    if text in ("mule", "mutant", "future"):
        g.say(
            "Seldon's face does something complicated. 'The Plan has a blind spot. "
            "It cannot see individuals. If an individual ever becomes large enough "
            "to cast a shadow across history, the Plan will need help it does not "
            "know it has. But that is three hundred years away, and you have a "
            "trial tomorrow.'"
        )
        return True
    return None


def prime_take(g: "Game", obj: Object) -> None:
    _both_cubes(g, "prime_radiant")
    return None


def decoy_take(g: "Game", obj: Object) -> None:
    _both_cubes(g, "decoy_cube")
    return None


def prime_read(g: "Game", obj: Object) -> None:
    g.say(
        "The Prime Radiant's surface crawls with equations in a script that seems "
        "to be doing mathematics and having opinions about the results. The cube "
        "is warm. It hums in primes: two, three, five, seven, eleven —"
    )
    g.say("You put it down before it reaches the really large ones.")
    return True


def decoy_read(g: "Game", obj: Object) -> None:
    g.say(
        "The cube is cold. Its equations are impressive, but they keep repeating "
        "the phrase BUY MORE CUBES in a font usually reserved for warranties. A "
        "tiny label on the base reads: REPLICA — FOR DISPLAY ONLY."
    )
    return True


# ---------------------------------------------------------------------------
# Trial
# ---------------------------------------------------------------------------

def trial_enter(g: "Game", first: bool) -> None:
    if first:
        g.say(
            "The trial chamber is a perfect circle of polished stone, designed to "
            "make the accused feel that the universe is watching from every "
            "direction. Above the bench hangs the Imperial Sunburst, recently "
            "dusted."
        )
        g.say(
            "Commissioner Linge Chen does not shout. He has people for that. He "
            "simply looks at you with the expression of a man reading a report he "
            "has already decided to file."
        )


def trial_answer(g: "Game", text: str) -> bool:
    if g.room().key != "trial_chamber":
        return False
    low = _norm(text)
    if g.has("trial_done"):
        g.say("The trial is over. Chen is already drafting the press release. It is mostly adjectives.")
        return True
    if low in ("no", "n", "never", "not guilty", "i do not", "i don't"):
        g.set_flag("trial_no")
        g.award_once("trial_no", 5, "You declined to confess. The Constitution sends its regards.")
        g.say(
            "'No,' you say, and the word lands on the polished floor with a sound "
            "that is almost respectable. Chen's pen stops. The stenographer types "
            "it twice to be sure."
        )
        g.say(
            "Chen smiles without involving the rest of his face. 'A denial. How "
            "refreshing. The Commission has not heard one since Tuesday.'"
        )
        return True
    if low in ("yes", "y", "guilty", "i confess", "confess"):
        g.death(
            "You confess to spreading psychohistorical alarm. The Commission is so "
            "pleased that it expedites your execution to avoid the paperwork of a "
            "trial. The Empire is efficient in small things."
        )
        return True
    return False


def chen_talk(g: "Game", npc: NPC) -> bool | None:
    g.say(
        "Commissioner Linge Chen is immaculate. His uniform has no medals, which "
        "is how you know he has real power. He regards you the way a surgeon "
        "regards a minor but interesting inflammation."
    )
    return True


def chen_topics(g: "Game", npc: NPC, topic: str) -> bool | None:
    text = _norm(topic)
    if text in ("charges", "crime", "trial", "accusation"):
        g.say(
            "'The charge is spreading psychohistorical alarm. In practice, this "
            "means predicting the Empire will fall. The Empire finds predictions "
            "of its fall more objectionable than the fall itself, which is a "
            "remarkably inefficient way to run a civilization.'"
        )
        return True
    if text in ("seldon", "hari seldon"):
        g.say(
            "'Seldon is a mathematician with a talent for publicity. He has "
            "predicted the fall of the Empire on a schedule convenient to his "
            "lecture tour. We are giving him a planet. It is a very small planet.'"
        )
        return True
    if text in ("evidence", "data", "tape", "cube", "radiant"):
        g.say(
            "'The Commission is always interested in evidence. Evidence is how we "
            "know what we have already decided. If you have something to show, show "
            "it. If you have something to give, give it. Do not waste the court's "
            "time with a towel.'"
        )
        return True
    if text in ("towel", "towel"):
        g.say("'A towel,' Chen says, 'is not evidence. It is a lifestyle.'")
        return True
    if text in ("terminus", "exile", "ship"):
        g.say(
            "'Exile is a mercy. The Emperor believes in mercy, provided it is "
            "administered far from the capital and does not appear in the budget.'"
        )
        return True
    return None


def chen_show(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key == "data_tape":
        g.award_once("trial_tape", 5, "The Commission's own records, entered into evidence.")
        g.say(
            "You hand over the data tape. Chen's aide inserts it into the court "
            "reader. The screen fills with shipping manifests, requisition orders, "
            "and a memo describing the trial as a 'routine narrative adjustment'."
        )
        g.say(
            "Chen reads the memo twice. 'A forgery,' he says, without conviction. "
            "The stenographer records the lack of conviction, which is the most "
            "honest thing that will happen in this room."
        )
        return True
    if obj.key == "prime_radiant":
        g.death(
            "You display the real Prime Radiant. Its equations glow across the "
            "courtroom, and every instrument in the room begins to hum in prime "
            "numbers. Chen does not need a trial after that. He has a confession "
            "with a luminous signature."
        )
        return True
    if obj.key == "decoy_cube":
        g.say("Chen glances at the decoy. 'Evidence is given,' he says, 'not exhibited like a school project.'")
        return True
    if obj.key == "towel":
        if g.has("cube_hidden"):
            g.say(
                "Chen studies the towel with the suspicion of a man who has been "
                "handed laundry in a courtroom. His scanner reports: COTTON, FIBRE, "
                "TRACE AMOUNTS OF REASONABLE FORETHOUGHT. He waves it away."
            )
        else:
            g.say("Chen declines to inspect the towel. 'The court has enough problems,' he says.")
        return True
    return False


def chen_give(g: "Game", npc: NPC, obj: Object) -> bool:
    if obj.key == "prime_radiant":
        g.death(
            "You give Chen the real Prime Radiant. He holds it up to the light, "
            "feels its warmth, and smiles a smile that has been waiting in a drawer "
            "for exactly this occasion. The trial ends, and so do you."
        )
        return True
    if obj.key == "decoy_cube":
        if g.has("trial_done"):
            g.say("Chen already has a cube. He does not collect them.")
            return True
        real_loc = g.state.obj_loc.get("prime_radiant")
        concealed = real_loc == "towel" and g.is_carried("towel")
        in_other_carried = (
            real_loc in g.world.objects
            and real_loc != "towel"
            and g.is_carried(real_loc)
        )
        if real_loc == "player" or in_other_carried:
            g.death(
                "You hand over the decoy. Chen's scanner sweeps you once, then "
                "again. It finds a second cube: warm, humming in prime numbers, and "
                "extremely illegal. Chen does not look surprised. He looks "
                "scheduled."
            )
            return True
        if not concealed and g.is_carried("prime_radiant"):
            g.death(
                "You hand over the decoy, but the real Prime Radiant is still in "
                "your luggage. Chen's scanner finds it in the lining of your "
                "suitcase. The Commission thanks you for the evidence and for the "
                "convenient confession."
            )
            return True
        g.set_flag("trial_done")
        g.state.obj_loc[obj.key] = "chen"
        g.award_once("decoy", 10, "The Commission accepted the wrong cube. History exhaled.")
        g.unlock_guide("THE PLAN")
        g.say(
            "You place the cold cube in Chen's palm. He turns it over, examines the "
            "equations, and nods to the technician. The scanner confirms: "
            "PSYCHOHISTORICAL DEVICE, CLASS THREE, NON-FUNCTIONAL."
        )
        g.say(
            "Chen's expression does not change, but something behind it closes like "
            "a door. 'The Commission accepts this evidence,' he says. 'The accused "
            "will be exiled to Terminus. The Empire is merciful.'"
        )
        g.say(
            "The stenographer types the word MERCIFUL, then quietly deletes the "
            "exclamation mark. Some habits are hard to break."
        )
        g.unlock_guide("ENCYCLOPEDIA GALACTICA")
        return True
    if obj.key == "data_tape":
        g.say("'Evidence is shown,' Chen says. 'Possession is a separate charge. The Commission is flexible about which one comes first.'")
        return True
    g.say(
        "Chen looks at the offered object as if it has personally wasted thirty "
        "seconds of Imperial history. 'The Commission accepts your gesture,' he "
        "says. 'It does not accept the object.'"
    )
    return True


# ---------------------------------------------------------------------------
# Launch bay
# ---------------------------------------------------------------------------

def manifest_read(g: "Game", obj: Object) -> None:
    g.award_once("manifest", 2, "Reading the manifest: a forgotten art with a measurable return.")
    g.unlock_guide("ENCYCLOPEDIA GALACTICA")
    return None


def encyclopedia_board(g: "Game", obj: Object, target: object) -> bool:
    if g.has("boarded"):
        return True
    g.set_flag("boarded")
    g.award_once("board", 11, "You boarded the correct ship. The Guide is astonished.")
    g.say(
        "You walk up the ramp of the Encyclopedia Galactica. The ship is ugly in "
        "the way that reliable things are ugly: welded, patched, and held together "
        "by maintenance schedules and mutual respect."
    )
    g.say(
        "Behind you, the launch bay doors begin to close. A Commission officer "
        "shouts something about paperwork. The ship's steward, a man with the "
        "bearing of a retired librarian, hands you a towel and a form."
    )
    g.say(
        "The form is titled ASSUMPTION OF RESPONSIBILITY FOR THE NEXT THOUSAND "
        "YEARS. There is no box to tick. There is only a line for your signature, "
        "and beneath it, in very small print: DON'T PANIC."
    )
    g.say(
        "The Encyclopedia Galactica rises from Trantor on a pillar of atomic fire. "
        "Below, forty billion people continue their lives, unaware that the "
        "history they are living has already been filed under 'previous editions'."
    )
    g.finish_act()
    return True


def wrong_ship(g: "Game", obj: Object, target: object) -> bool:
    if obj.key == "imperial_glory":
        g.death(
            "You board the Imperial Glory. The crew recognises you from the trial "
            "and is delighted to have a guest with such a flexible definition of "
            "'exile'. The ship returns to Trantor, where the Commission has "
            "prepared a smaller, more private trial."
        )
    else:
        g.death(
            "You board the grain freighter. The captain explains that the cargo is "
            "almost entirely fertiliser and that passengers are expected to earn "
            "their passage. The next stop is Anacreon, where nobody has heard of "
            "you and nobody is likely to."
        )
    return True


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------

def act1_hints(g: "Game") -> str:
    room = g.room().key

    if room == "trial_chamber":
        if not g.has("trial_no"):
            return (
                "Chen is waiting for an answer. The word he least expects is a "
                "simple NO. Try SAY NO."
            )
        if not g.has("cube_hidden"):
            return (
                "The real Prime Radiant is warm and hums in primes. Put it in your "
                "towel before Chen searches you: PUT PRIME RADIANT IN TOWEL."
            )
        if not g.has("trial_done"):
            return (
                "Show Chen the data tape if you have it, then give him the cold "
                "decoy cube. GIVE DECOY CUBE TO CHEN."
            )
        return "The launch bay door is open. Go through it and read the manifest."

    if room == "launch_bay" and not g.has("boarded"):
        return (
            "Read the manifest, then board the ship whose name matches the "
            "Encyclopedia Galactica. The Imperial Glory goes back to Trantor."
        )

    if not g.has("security_cleared"):
        return (
            "The security pedestal wants your visa. Try USE VISA ON PEDESTAL. Your "
            "suitcase is probably still going round the carousel."
        )
    if g.state.obj_loc.get("suitcase") == "carousel" and not g.is_carried("suitcase"):
        return "TAKE SUITCASE from the carousel. It contains a letter worth reading."
    if not g.has("awarded:seldon_letter") and g.has("suitcase_taken"):
        return "OPEN SUITCASE, then READ the letter from Hari Seldon."

    if room == "taxi_queue" and not g.has("fare_paid"):
        return "The taxi wants a credit chip. USE CREDIT CHIP ON FARE MACHINE, then BOARD TAXI."

    if room == "hotel_lobby" and not g.has("key_card_given"):
        return "The clerk can help. SHOW SELDON LETTER TO CLERK."

    if room == "hotel_corridor":
        if g.state.obj_locked.get("room_door", True):
            return "The suite door is locked. OPEN DOOR (your key card should do the rest)."
        return "Your suite is north. The door is unlocked."

    if room == "hotel_room":
        if not g.has("holo_played"):
            return "The holo projector is worth a look. USE PROJECTOR."
        if not g.is_carried("library_card") and g.state.obj_loc.get("library_card") == "hotel_drawer":
            return "OPEN DRAWER, then TAKE the library card. The overdue book is also worth returning."

    if not g.has("old_wing_open"):
        return (
            "The old wing at Streeling opens for the first rule of hitchhiking. "
            "Read the statue, ask the student about passwords, then SAY \"DON'T PANIC\" "
            "in the plaza."
        )
    if not g.has("briefed"):
        return "Enter the old wing and talk to Hari Seldon in his office."

    if not g.is_carried("data_tape") and not g.has("awarded:data_tape"):
        return (
            "The library archive may contain evidence. You need the library card "
            "from the hotel drawer to open the archive door."
        )

    return "Look around, read everything, and do not give Chen the warm cube."


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------

def build() -> World:
    rooms: dict[str, Room] = {
        "spaceport": Room(
            key="spaceport",
            name="Imperial Spaceport, Trantor",
            desc=(
                "You stand in the arrival hall of the Imperial Spaceport, a cavern "
                "of polished metal and recycled gravity. Forty billion people live "
                "on this planet, and every one of them appears to be ahead of you "
                "in the queue.\n\n"
                "A luggage carousel grinds through its circuit, carrying one "
                "battered suitcase and the faint smell of Synnax. Beyond a security "
                "gate, a taxi rank waits. Beyond that, the capital of the Galaxy "
                "continues in every direction, including down."
            ),
            brief="The arrival hall hums with announcements nobody listens to.",
            coords=(0, 0),
            map_label="Spaceport",
            exits={
                "north": Exit(
                    dest="taxi_queue",
                    label="security gate",
                    condition=lambda g: g.has("security_cleared"),
                    blocked="A security pedestal blocks the gate. It wants your visa, or possibly your soul, but mostly your visa.",
                ),
            },
        ),
        "taxi_queue": Room(
            key="taxi_queue",
            name="Taxi Rank",
            desc=(
                "The taxi rank is a narrow platform above a river of moving light. "
                "Ground cars arrive, swallow passengers, and depart with the "
                "resigned efficiency of machines that have seen everything.\n\n"
                "A fare machine stands at the head of the queue, displaying a price "
                "that has been adjusted upward for weather, distance, and the "
                "continued existence of the Empire."
            ),
            brief="Taxis come and go. The fare machine does not.",
            coords=(0, 1),
            map_label="Taxi",
            exits={
                "south": Exit(dest="spaceport", label="spaceport"),
                "taxi": Exit(
                    dest="hotel_lobby",
                    label="taxi",
                    condition=lambda g: g.has("fare_paid"),
                    blocked="The taxi driver looks at you, then at the fare machine, then back at you. The message is clear.",
                ),
            },
        ),
        "hotel_lobby": Room(
            key="hotel_lobby",
            name="Lobby, the Luxor Hotel",
            desc=(
                "The Luxor Hotel is the sort of place where the carpet costs more "
                "than the staff and the chandelier has its own maintenance crew. "
                "The desk clerk stands beneath a sign that says WELCOME, and "
                "another, smaller sign that says NO REFUNDS.\n\n"
                "To the west, a revolving door opens onto Streeling Plaza. To the "
                "east, the elevator waits with the patience of a machine that has "
                "heard every excuse."
            ),
            brief="The lobby glitters, professionally.",
            coords=(1, 1),
            map_label="Luxor",
            on_enter=hotel_enter,
            exits={
                "entrance": Exit(dest="taxi_queue", label="entrance"),
                "west": Exit(dest="streeling_plaza", label="plaza"),
                "elevator": Exit(
                    dest="hotel_corridor",
                    label="elevator",
                    condition=lambda g: g.has("key_card_given"),
                    blocked="The elevator requires a key card. The clerk is watching you pretend not to need one.",
                ),
                "up": Exit(
                    dest="hotel_corridor",
                    hidden=True,
                    condition=lambda g: g.has("key_card_given"),
                    blocked="The elevator requires a key card.",
                ),
            },
        ),
        "hotel_corridor": Room(
            key="hotel_corridor",
            name="Fourteenth Floor Corridor",
            desc=(
                "The corridor is carpeted in a shade of red that was fashionable "
                "three emperors ago. Doors line both sides, each with a number and "
                "a small plaque explaining that the minibar is a privilege, not a "
                "right.\n\n"
                "Suite fourteen waits at the north end. The elevator is behind you."
            ),
            brief="A quiet corridor with expensive carpet and inexpensive lighting.",
            coords=(1, 2),
            map_label="Corridor",
            exits={
                "elevator": Exit(dest="hotel_lobby", label="elevator"),
                "down": Exit(dest="hotel_lobby", hidden=True),
                "north": Exit(
                    dest="hotel_room",
                    label="suite door",
                    condition=lambda g: not g.state.obj_locked.get("room_door", True),
                    blocked="The suite door is locked. The key card from the clerk should open it.",
                ),
            },
        ),
        "hotel_room": Room(
            key="hotel_room",
            name="Suite Fourteen",
            desc=(
                "Suite fourteen is aggressively comfortable. The bed is large "
                "enough to have its own weather system, the window offers a view of "
                "another building's window, and a holo projector waits on the desk "
                "like a small, guilty secret.\n\n"
                "A drawer has been left slightly open, as if the previous guest "
                "departed in a hurry or the furniture is curious."
            ),
            brief="A hotel suite designed to make you forget which planet you are on.",
            coords=(1, 3),
            map_label="Suite",
            exits={"south": Exit(dest="hotel_corridor", label="corridor")},
        ),
        "streeling_plaza": Room(
            key="streeling_plaza",
            name="Streeling Plaza",
            desc=(
                "Streeling Plaza is a rare patch of open ground on Trantor: a "
                "rectangle of grass, a statue, and enough sky to remind people that "
                "skies used to be larger. Students cross it in knots, arguing about "
                "politics, tenure, and whose turn it is to buy coffee.\n\n"
                "A statue of the first settlers stands at the centre, its inscription "
                "partly sanded away. At the plaza's northern edge, the university "
                "library rises in layers of grey stone. At the eastern edge, the "
                "Luxor Hotel shines like a expensive mistake."
            ),
            brief="Students argue beneath a damaged statue. The library waits north.",
            coords=(0, 2),
            map_label="Plaza",
            exits={
                "east": Exit(dest="hotel_lobby", label="hotel"),
                "north": Exit(dest="library", label="library"),
                "old wing": Exit(
                    dest="old_wing",
                    label="old wing arch",
                    condition=lambda g: g.has("old_wing_open"),
                    blocked="A service arch is sealed by an old security field. A small plate reads: SPEAK, FRIEND, AND ENTER. The plate has been amended in pen: PASSWORD REQUIRED.",
                ),
            },
        ),
        "library": Room(
            key="library",
            name="Streeling University Library",
            desc=(
                "The library smells of paper, dust, and the quiet authority of "
                "things that have outlasted their authors. Shelves climb toward a "
                "ceiling lost in shadow. A reading room occupies the centre, lit by "
                "lamps designed to make everything look like a primary source.\n\n"
                "The librarian presides from a desk near the returns cart. Behind "
                "her, an archive door carries a brass plate and the accumulated "
                "disapproval of several centuries."
            ),
            brief="The library is quiet, vast, and not entirely convinced you have a card.",
            coords=(0, 3),
            map_label="Library",
            exits={
                "south": Exit(dest="streeling_plaza", label="plaza"),
                "archive": Exit(
                    dest="archive",
                    label="archive door",
                    condition=lambda g: not g.state.obj_locked.get("archive_door", True),
                    blocked="The archive door is locked. A brass plate suggests an Imperial Library card.",
                ),
            },
        ),
        "archive": Room(
            key="archive",
            name="Library Archive",
            desc=(
                "The archive is colder than the reading room and considerably more "
                "honest. Metal shelves hold records the Empire has decided not to "
                "display: shipping manifests, census returns, and boxes labelled "
                "MISCELLANEOUS TRUTHS.\n\n"
                "A data tape sits on a reading table beneath a lamp. In the corner, "
                "a cube of compressed paperwork hums faintly with bureaucratic "
                "resentment."
            ),
            brief="Old records, cold air, and a data tape waiting to be read.",
            coords=(-1, 3),
            map_label="Archive",
            exits={"west": Exit(dest="library", label="reading room")},
        ),
        "old_wing": Room(
            key="old_wing",
            name="The Old Wing",
            desc=(
                "The old wing is a corridor the university forgot to renovate and "
                "the Commission forgot to inspect. Its walls are lined with "
                "photographs of professors who have been dead long enough to become "
                "buildings.\n\n"
                "At the far end, a door carries a hand-lettered sign: H. SELDON — "
                "KNOCK FIRST. THE MATH IS AT A DELICATE STAGE. Behind you, the "
                "plaza glows through the arch."
            ),
            brief="Dust, old photographs, and the sound of mathematics through a door.",
            coords=(0, 4),
            map_label="Old Wing",
            on_enter=old_wing_enter,
            exits={
                "south": Exit(dest="streeling_plaza", label="plaza"),
                "north": Exit(dest="seldon_office", label="Seldon's office"),
            },
        ),
        "seldon_office": Room(
            key="seldon_office",
            name="Hari Seldon's Office",
            desc=(
                "The office is small, crowded, and organised according to a theory "
                "of history that has not yet been published. Papers cover the desk "
                "in strata. A blackboard carries equations that appear to be "
                "arguing with each other.\n\n"
                "Hari Seldon stands by the window, looking out at a city that fills "
                "the horizon and then keeps going. He does not seem surprised to "
                "see you."
            ),
            brief="Seldon's office: paper, chalk, and the future under review.",
            coords=(0, 5),
            map_label="Office",
            exits={
                "south": Exit(
                    dest="old_wing",
                    label="corridor",
                    on_use=office_leave,
                ),
            },
        ),
        "trial_chamber": Room(
            key="trial_chamber",
            name="Trial Chamber, Commission of Public Safety",
            desc=(
                "The trial chamber is a perfect circle of polished stone. Every seat "
                "faces the centre. The Imperial Sunburst hangs above the bench, "
                "recently dusted and carefully lit.\n\n"
                "Commissioner Linge Chen sits behind the bench with a folder, a "
                "pen, and the expression of a man who has already written the "
                "verdict and is merely waiting for the accused to catch up."
            ),
            brief="A circular room designed to make truth feel optional.",
            coords=(-1, 5),
            map_label="Trial",
            on_enter=trial_enter,
            exits={
                "launch bay": Exit(
                    dest="launch_bay",
                    label="launch bay door",
                    condition=lambda g: g.has("trial_done"),
                    blocked="The door is sealed until the Commission finishes with you. Chen is still holding his pen.",
                ),
            },
        ),
        "launch_bay": Room(
            key="launch_bay",
            name="Imperial Launch Bay 7",
            desc=(
                "Launch Bay 7 is a cathedral of engineering with the acoustics of a "
                "warehouse. Three ships wait on their pads, attended by crews who "
                "have the look of people being paid by the hour and charged by the "
                "breath.\n\n"
                "A manifest board stands near the passenger gate. Beyond it, the "
                "ships crouch under the floodlights: one battered freighter, one "
                "sleek Imperial courier, and one grain hauler with a defiantly "
                "agricultural smell."
            ),
            brief="Three ships, one manifest, and a great deal of engine noise.",
            coords=(0, 6),
            map_label="Launch Bay",
        ),
    }

    objects: dict[str, Object] = {
        # Starting inventory -------------------------------------------------
        "visa": Object(
            key="visa",
            names=["visa", "imperial visa", "travel document", "document"],
            short="visa",
            location="player",
            desc=(
                "A stiff rectangle of Imperial plastic bearing your name, your "
                "photograph, and a holographic seal that has never worked properly. "
                "Occupation: mathematician. Purpose of visit: attending a lecture. "
                "Suspicion level: not yet calculated."
            ),
        ),
        "itinerary": Object(
            key="itinerary",
            names=["itinerary", "travel itinerary", "ticket", "reservation"],
            short="itinerary",
            location="player",
            readable=True,
            on_read=itinerary_read,
            desc="A folded itinerary from the Imperial Travel Bureau. It is already out of date.",
        ),
        "watch": Object(
            key="watch",
            names=["watch", "wristwatch", "timepiece"],
            short="watch",
            location="player",
            desc=(
                "An ordinary wristwatch. It keeps Imperial Standard Time, which is "
                "always 9:15 on Trantor because the planet has decided that "
                "time zones are a provincial affectation."
            ),
        ),
        "towel": Object(
            key="towel",
            names=["towel", "guide towel", "my towel"],
            short="towel",
            location="player",
            container=True,
            open=True,
            wearable=True,
            on_receive=towel_receive,
            desc=(
                "A large, reasonably clean towel. It is the most important object "
                "you own, according to a book you have not finished reading. It can "
                "be worn, folded, used as a pillow, or employed to conceal a "
                "psychohistorical device from an Imperial scanner. The Guide "
                "recommends all four, preferably in that order."
            ),
        ),
        # Spaceport ----------------------------------------------------------
        "carousel": Object(
            key="carousel",
            names=["carousel", "luggage carousel", "conveyor"],
            short="luggage carousel",
            location="spaceport",
            fixed=True,
            takeable=False,
            container=True,
            open=True,
            transparent=True,
            desc=(
                "The carousel rotates with the dignity of a machine that has been "
                "insulted by luggage for decades. Most of the bags have already been "
                "claimed. One suitcase remains."
            ),
        ),
        "suitcase": Object(
            key="suitcase",
            names=["suitcase", "luggage", "bag", "case"],
            short="suitcase",
            location="carousel",
            container=True,
            open=False,
            openable=True,
            on_take=suitcase_take,
            desc=(
                "A sturdy suitcase with a dent in one corner and a tag identifying "
                "it as yours. It is closed. It contains everything you brought from "
                "Synnax and several things you did not."
            ),
        ),
        "credit_chip": Object(
            key="credit_chip",
            names=["credit chip", "chip", "credit", "money", "credits"],
            short="credit chip",
            location="suitcase",
            desc=(
                "A thin disc of metal and encoded optimism. The balance is enough "
                "for a taxi, a hotel room, and one emergency purchase of something "
                "fried."
            ),
        ),
        "primer": Object(
            key="primer",
            names=["primer", "guidebook", "book", "pamphlet", "hitchhiker's guide"],
            short="primer",
            location="suitcase",
            readable=(
                "The cover says THE HITCHHIKER'S GUIDE TO THE GALAXY in large, "
                "friendly letters. Beneath that, someone has written in pen: "
                "NOW WITH 12% MORE FOUNDATION. The introduction begins: 'Space is "
                "big. You will not believe how vastly, hugely, mind-bogglingly big "
                "it is. Neither will the Empire, which is why it keeps losing "
                "planets.'\n\n"
                "A bookmark points to the entry on towels."
            ),
            desc="A battered copy of the Hitchhiker's Guide, much travelled and lightly annotated.",
        ),
        "seldon_letter": Object(
            key="seldon_letter",
            names=["letter", "seldon letter", "note", "message"],
            short="letter from Hari Seldon",
            location="suitcase",
            readable=(
                "Dear Dr Dornick,\n\n"
                "Welcome to Trantor. I apologise for the weather, the government, "
                "and the food, in reverse order of importance.\n\n"
                "Come to Streeling University and find the old wing. The arch "
                "listens for the first rule of hitchhiking. Do not tell the "
                "Commission where you are going. Do not trust anyone who offers you "
                "a seat on a committee.\n\n"
                "Bring a towel.\n\n"
                "H. Seldon\n\n"
                "P.S. If the Commission arrests you, answer NO and give them the cold "
                "cube."
            ),
            on_read=letter_read,
            desc="A letter from Hari Seldon, folded twice and already slightly improbable.",
        ),
        "security_pedestal": Object(
            key="security_pedestal",
            names=["pedestal", "security pedestal", "scanner", "security scanner"],
            short="security pedestal",
            location="spaceport",
            fixed=True,
            takeable=False,
            on_use=pedestal_use,
            on_use_with=pedestal_use,
            desc=(
                "A waist-high pillar of grey metal with a document slot, a scanning "
                "lens, and a small screen displaying the words PLEASE HAVE YOUR VISA "
                "READY. Beneath that, in smaller letters: HAVE IT READY AGAIN. "
                "BUREAUCRACY IS A PROCESS."
            ),
        ),
        # Taxi ---------------------------------------------------------------
        "fare_machine": Object(
            key="fare_machine",
            names=["fare machine", "machine", "meter", "fare meter"],
            short="fare machine",
            location="taxi_queue",
            fixed=True,
            takeable=False,
            on_use=fare_machine_use,
            on_use_with=fare_machine_use,
            desc=(
                "A squat machine with a slot for credit chips and a screen that "
                "displays the fare in a font designed to discourage questions. A "
                "sticker reads: EXACT CHANGE ONLY. Another sticker, older, reads: "
                "EXACT CHANGE WAS A MISTAKE."
            ),
        ),
        "taxi": Object(
            key="taxi",
            names=["taxi", "cab", "ground car", "car"],
            short="taxi",
            location="taxi_queue",
            fixed=True,
            takeable=False,
            on_use=taxi_use,
            desc=(
                "A ground-effect taxi with a yellow stripe and a driver who has "
                "mastered the art of looking at passengers through the mirror "
                "without making eye contact."
            ),
        ),
        "queue_sign": Object(
            key="queue_sign",
            names=["sign", "queue sign", "notice"],
            short="queue sign",
            location="taxi_queue",
            fixed=True,
            takeable=False,
            readable=(
                "IMPERIAL TRANSPORT AUTHORITY\n\n"
                "TAXIS ARRIVE EVERY 90 SECONDS.\n"
                "PASSENGERS MUST PAY IN ADVANCE.\n"
                "THE EMPIRE THANKS YOU FOR YOUR PATIENCE.\n\n"
                "A handwritten addition reads: THE EMPIRE HAS NEVER WAITED FOR "
                "ANYTHING IN ITS LIFE."
            ),
            desc="A sign explaining the rules of the queue in three languages and no useful detail.",
        ),
        # Hotel --------------------------------------------------------------
        "chandelier": Object(
            key="chandelier",
            names=["chandelier", "light", "lights"],
            short="chandelier",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            desc=(
                "The chandelier is a triumph of engineering and a crime against "
                "taste. It contains more lights than the average inhabited system "
                "and is cleaned by a specialist team that has signed a very long "
                "non-disclosure agreement."
            ),
        ),
        "potted_plant": Object(
            key="potted_plant",
            names=["plant", "potted plant", "fern", "flowerpot"],
            short="potted plant",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            desc=(
                "A large ornamental plant. Its leaves are suspiciously glossy. A "
                "small label reads: GENUINE ARTIFICIAL FOLIAGE. The plant has been "
                "wired for sound, surveillance, and, on alternate Thursdays, "
                "background music."
            ),
        ),
        "front_desk": Object(
            key="front_desk",
            names=["desk", "front desk", "reception desk", "counter"],
            short="front desk",
            location="hotel_lobby",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A slab of dark wood so polished that it reflects your future "
                "mistakes. A bell sits on it with a small sign: RING FOR SERVICE. "
                "A second sign, beneath it, reads: RINGING DOES NOT GUARANTEE "
                "SERVICE."
            ),
        ),
        "key_card": Object(
            key="key_card",
            names=["key card", "keycard", "room key", "key"],
            short="key card",
            location=None,
            desc=(
                "A thin plastic card encoded with the privileges of Suite Fourteen. "
                "It opens the suite door, the minibar, and, on a good day, the "
                "elevator. On a bad day it opens only a conversation with the clerk."
            ),
        ),
        "room_door": Object(
            key="room_door",
            names=["door", "suite door", "room door"],
            short="suite door",
            location="hotel_corridor",
            fixed=True,
            takeable=False,
            container=True,
            open=False,
            openable=True,
            locked=True,
            unlock_key="key_card",
            desc="A door marked 14 in tasteful brass. It is locked, which is the hotel's way of pretending it cares.",
        ),
        "elevator_door": Object(
            key="elevator_door",
            names=["elevator", "elevator door", "lift"],
            short="elevator",
            location="hotel_corridor",
            fixed=True,
            takeable=False,
            desc=(
                "The elevator doors are polished to a mirror finish. Your reflection "
                "looks tired, which is unfair, because it has not done any of the "
                "travelling."
            ),
        ),
        "holo_projector": Object(
            key="holo_projector",
            names=["holo projector", "projector", "holo", "holovision"],
            short="holo projector",
            location="hotel_room",
            fixed=True,
            takeable=False,
            on_use=holo_use,
            desc=(
                "A compact holo projector with a cracked casing and a label reading "
                "COMPLIMENTARY SERVICE. In smaller type: COMPLIMENTARY DOES NOT "
                "MEAN FREE."
            ),
        ),
        "hotel_drawer": Object(
            key="hotel_drawer",
            names=["drawer", "nightstand", "desk drawer"],
            short="drawer",
            location="hotel_room",
            container=True,
            open=False,
            openable=True,
            desc=(
                "A drawer in the nightstand. It sticks slightly, as if the hotel is "
                "reluctant to let go of anything, including other people's property."
            ),
        ),
        "library_card": Object(
            key="library_card",
            names=["library card", "library pass", "card", "pass"],
            short="library card",
            location="hotel_drawer",
            on_take=library_card_take,
            desc=(
                "An Imperial Library card with a photograph that makes you look "
                "like a suspect and a signature that makes you look guilty. The "
                "back lists privileges: READING ROOM, ARCHIVE, QUIET."
            ),
        ),
        "overdue_book": Object(
            key="overdue_book",
            names=["overdue book", "library book", "book", "volume"],
            short="overdue book",
            location="hotel_drawer",
            on_read=overdue_book_read,
            readable=(
                "A HISTORY OF THE GALACTIC EMPIRE, VOLUME 12. The due date is "
                "stamped forty years ago. Inside the front cover, a handwritten "
                "note reads: 'Sorry. The Empire fell while I was renewing.'"
            ),
            desc="A library book with a due date old enough to vote.",
        ),
        "bed": Object(
            key="bed",
            names=["bed", "mattress", "pillow"],
            short="bed",
            location="hotel_room",
            fixed=True,
            takeable=False,
            desc=(
                "The bed is enormous and immaculately made. A small card on the "
                "pillow reads: SLEEP IS A LUXURY. THE MINIBAR IS NOT."
            ),
        ),
        "window": Object(
            key="window",
            names=["window", "view"],
            short="window",
            location="hotel_room",
            fixed=True,
            takeable=False,
            desc=(
                "The window looks out onto another building's window, where someone "
                "is looking back at you through a window. Trantor has forty billion "
                "people and not quite enough view to go around."
            ),
        ),
        # Plaza and library --------------------------------------------------
        "statue": Object(
            key="statue",
            names=["statue", "monument", "inscription", "plaque"],
            short="statue",
            location="streeling_plaza",
            fixed=True,
            takeable=False,
            readable=True,
            on_read=statue_read,
            desc=(
                "A bronze figure of a stern settler pointing toward the future, or "
                "possibly toward the library. The inscription below has been partly "
                "sanded away by the Commission of Public Safety, which objects to "
                "history with opinions."
            ),
        ),
        "bench": Object(
            key="bench",
            names=["bench", "seat"],
            short="bench",
            location="streeling_plaza",
            fixed=True,
            takeable=False,
            desc=(
                "A stone bench worn smooth by generations of students. Someone has "
                "carved a formula into the armrest, and someone else has carved a "
                "reply that is unprintable in a family guide."
            ),
        ),
        "reading_desk": Object(
            key="reading_desk",
            names=["reading desk", "desk", "table"],
            short="reading desk",
            location="library",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "A long reading desk lit by green-shaded lamps. It has the "
                "concentrated silence of a place where people have spent entire "
                "lives arguing with footnotes."
            ),
        ),
        "card_catalogue": Object(
            key="card_catalogue",
            names=["card catalogue", "catalogue", "catalog", "drawers"],
            short="card catalogue",
            location="library",
            fixed=True,
            takeable=False,
            container=True,
            open=True,
            transparent=True,
            desc=(
                "A wooden card catalogue with thousands of tiny drawers. The "
                "labels are handwritten, which means they are either trustworthy "
                "or the result of a very long argument."
            ),
        ),
        "archive_door": Object(
            key="archive_door",
            names=["archive door", "door", "archive"],
            short="archive door",
            location="library",
            fixed=True,
            takeable=False,
            container=True,
            open=False,
            openable=True,
            locked=True,
            unlock_key="library_card",
            on_open=archive_door_open,
            desc="A heavy door marked ARCHIVE. The brass plate is polished by the hands of authorised personnel and the elbows of everyone else.",
        ),
        "returns_cart": Object(
            key="returns_cart",
            names=["returns cart", "cart", "trolley"],
            short="returns cart",
            location="library",
            fixed=True,
            takeable=False,
            desc=(
                "A wheeled cart piled with returned books. One volume is ticking "
                "gently. The librarian has placed a sign on it: OVERDUE, DO NOT "
                "SHAKE."
            ),
        ),
        "data_tape": Object(
            key="data_tape",
            names=["data tape", "tape", "recording", "evidence"],
            short="data tape",
            location="archive",
            readable=(
                "The tape contains shipping manifests, requisition orders, and a "
                "memo from the Commission of Public Safety describing Seldon's trial "
                "as a 'routine narrative adjustment'. It is signed by an undersecretary "
                "who has since been promoted, which is the closest the Empire comes "
                "to an admission of guilt."
            ),
            on_read=data_tape_read,
            desc=(
                "A sealed data tape labelled COMMISSION INTERNAL — NOT FOR "
                "CIRCULATION. Someone has circled NOT and written 'especially not' "
                "in pen."
            ),
        ),
        "archived_cube": Object(
            key="archived_cube",
            names=["archived cube", "cube", "paperwork", "box"],
            short="archived cube",
            location="archive",
            fixed=True,
            takeable=False,
            desc=(
                "A cube of compressed paperwork, roughly the size of a small "
                "refrigerator. A label reads: MISCELLANEOUS TRUTHS, VOLUMES 1–9,000. "
                "It hums with the trapped resentment of a billion forms."
            ),
        ),
        "shelves": Object(
            key="shelves",
            names=["shelves", "shelf", "records"],
            short="shelves",
            location="archive",
            fixed=True,
            takeable=False,
            desc=(
                "Metal shelves stretch into the dimness, loaded with records no one "
                "has requested in decades. Somewhere in the middle distance, a box "
                "is labelled PLANS FOR THE FUTURE — DO NOT OPEN UNTIL NECESSARY."
            ),
        ),
        "old_photographs": Object(
            key="old_photographs",
            names=["photographs", "photos", "pictures", "portraits"],
            short="old photographs",
            location="old_wing",
            fixed=True,
            takeable=False,
            desc=(
                "Row after row of professors, each wearing the expression of someone "
                "who has just discovered that the universe is more complicated than "
                "the grant application suggested."
            ),
        ),
        "dead_terminal": Object(
            key="dead_terminal",
            names=["terminal", "dead terminal", "computer", "screen"],
            short="dead terminal",
            location="old_wing",
            fixed=True,
            takeable=False,
            on_use=lambda g, o, t: g.say(
                "You wake the terminal. It displays: SYSTEM LAST USED 41 YEARS AGO. "
                "PLEASE ENTER PASSWORD. You type DON'T PANIC. It displays: PASSWORD "
                "EXPIRED. PLEASE CONTACT YOUR SYSTEM ADMINISTRATOR, WHO IS ALSO "
                "EXPIRED."
            )
            or True,
            desc="An ancient computer terminal. It is dead, but it is the sort of dead that might still answer a question.",
        ),
        # Seldon's office ----------------------------------------------------
        "desk": Object(
            key="desk",
            names=["desk", "seldon's desk", "table"],
            short="desk",
            location="seldon_office",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "Seldon's desk is covered in papers, coffee cups, and a small "
                "mountain of chalk dust. One drawer is closed. The desk has the "
                "look of a surface that has given up on being tidy and chosen to "
                "become history instead."
            ),
        ),
        "office_drawer": Object(
            key="office_drawer",
            names=["drawer", "desk drawer", "bottom drawer"],
            short="drawer",
            location="seldon_office",
            container=True,
            open=False,
            openable=True,
            desc=(
                "The desk drawer is closed. A label, in Seldon's handwriting, reads: "
                "CUBES — DO NOT GIVE THE WARM ONE TO THE COMMISSION. Beneath that, "
                "smaller: OR THE COLD ONE, IF YOU ARE FEELING DRAMATIC."
            ),
        ),
        "prime_radiant": Object(
            key="prime_radiant",
            names=["prime radiant", "radiant", "real cube", "warm cube", "cube"],
            short="Prime Radiant",
            location="office_drawer",
            on_take=prime_take,
            on_read=prime_read,
            readable=True,
            desc=(
                "The Prime Radiant is a cube of dull metal that is warm to the "
                "touch and hums in prime numbers. Equations crawl across its surface "
                "in lines too small to read and too important to ignore. This is the "
                "real thing."
            ),
        ),
        "decoy_cube": Object(
            key="decoy_cube",
            names=["decoy cube", "decoy", "cold cube", "replica", "cube"],
            short="decoy cube",
            location="office_drawer",
            on_take=decoy_take,
            on_read=decoy_read,
            readable=True,
            desc=(
                "A cube of dull metal that is cold to the touch. Its equations look "
                "convincing until one notices that they repeat the phrase BUY MORE "
                "CUBES. A tiny label on the base reads: REPLICA — FOR DISPLAY ONLY."
            ),
        ),
        "paperweight": Object(
            key="paperweight",
            names=["paperweight", "stone", "weight", "rock"],
            short="paperweight",
            location="seldon_office",
            fixed=True,
            takeable=False,
            desc=(
                "A lump of concrete from the original Streeling foundation. It is "
                "engraved with the words THIS STONE HELD UP THE FIRST BUILDING. It "
                "is now holding up a stack of papers about the second building."
            ),
        ),
        "blackboard": Object(
            key="blackboard",
            names=["blackboard", "chalkboard", "equations", "board"],
            short="blackboard",
            location="seldon_office",
            fixed=True,
            takeable=False,
            readable=(
                "The blackboard is covered in equations. In the lower right corner, "
                "someone has written: IF YOU CAN READ THIS, THE PLAN IS ON SCHEDULE. "
                "Below that, in different handwriting: IF YOU CAN READ THIS, PLEASE "
                "ERASE THE BOARD BEFORE THE COMMISSION ARRIVES."
            ),
            desc="A blackboard covered in the mathematics of history and the history of mathematics.",
        ),
        # Trial --------------------------------------------------------------
        "trial_bench": Object(
            key="trial_bench",
            names=["bench", "judge's bench", "desk"],
            short="judge's bench",
            location="trial_chamber",
            fixed=True,
            takeable=False,
            surface=True,
            desc=(
                "The bench is black stone with a thin gold line around the edge. It "
                "is designed to make whoever sits behind it look permanent. In "
                "Chen's case, it works."
            ),
        ),
        "evidence_screen": Object(
            key="evidence_screen",
            names=["screen", "evidence screen", "display"],
            short="evidence screen",
            location="trial_chamber",
            fixed=True,
            takeable=False,
            desc=(
                "A blank screen waits to display evidence. Its screensaver is the "
                "Imperial Sunburst, rotating slowly, as if the Empire has nothing "
                "better to do with its remaining centuries."
            ),
        ),
        # Launch bay ---------------------------------------------------------
        "manifest": Object(
            key="manifest",
            names=["manifest", "shipping manifest", "board", "clipboard"],
            short="manifest",
            location="launch_bay",
            fixed=True,
            takeable=False,
            readable=(
                "IMPERIAL LAUNCH BAY 7 — DEPARTURES\n\n"
                "EGS ENCYCLOPEDIA GALACTICA — destination TERMINUS. Charter: "
                "Foundation. Cargo: scholars, equipment, and one very large "
                "encyclopedia. Passenger berths: available.\n\n"
                "ISS IMPERIAL GLORY — destination TRANTOR. Returning officers and "
                "prisoners. Passenger berths: not for you.\n\n"
                "MV GRAIN OF TRUTH — destination ANACREON. Cargo: fertiliser. "
                "Passenger berths: none. The captain is willing to negotiate.\n\n"
                "A handwritten note at the bottom reads: THE ONE WITH THE "
                "ENCYCLOPEDIA ON THE SIDE. NOT THE SHINY ONE."
            ),
            on_read=manifest_read,
            desc="A departure manifest listing three ships, two destinations, and one obvious choice.",
        ),
        "encyclopedia": Object(
            key="encyclopedia",
            names=["encyclopedia", "encyclopedia galactica", "freighter", "ship", "foundation ship"],
            short="Encyclopedia Galactica",
            location="launch_bay",
            fixed=True,
            takeable=False,
            on_use=encyclopedia_board,
            desc=(
                "A squat, welded freighter with ENCYCLOPEDIA GALACTICA painted "
                "along its flank in letters large enough to be read from orbit. It "
                "is not beautiful. It is the sort of ship that gets things done, "
                "usually by outlasting the things that are trying to stop it."
            ),
        ),
        "imperial_glory": Object(
            key="imperial_glory",
            names=["imperial glory", "glory", "courier", "imperial ship"],
            short="Imperial Glory",
            location="launch_bay",
            fixed=True,
            takeable=False,
            on_use=wrong_ship,
            desc=(
                "A sleek Imperial courier with polished fins and a hull that has "
                "never been used to carry anything more dangerous than a senior "
                "officer's ego. Its destination board reads TRANTOR — RETURNING "
                "OFFICERS."
            ),
        ),
        "freighter": Object(
            key="freighter",
            names=["grain of truth", "freighter", "grain ship", "hauler"],
            short="Grain of Truth",
            location="launch_bay",
            fixed=True,
            takeable=False,
            on_use=wrong_ship,
            desc=(
                "A grain hauler with a hull the colour of old porridge. The name "
                "GRAIN OF TRUTH is painted on the side, beneath a faded slogan: "
                "AGRICULTURE FEEDS THE GALAXY. The smell suggests it also feeds "
                "something else."
            ),
        ),
        "launch_control": Object(
            key="launch_control",
            names=["launch control", "control tower", "console"],
            short="launch control",
            location="launch_bay",
            fixed=True,
            takeable=False,
            desc=(
                "A glass booth full of screens and people who are paid to worry. "
                "One of them is eating a sandwich. The Guide respects this."
            ),
        ),
    }

    npcs: dict[str, NPC] = {
        "clerk": NPC(
            key="clerk",
            names=["clerk", "receptionist", "hotel clerk", "desk clerk"],
            short="clerk",
            location="hotel_lobby",
            desc=(
                "The clerk's name badge says WELCOME TO THE LUXOR. His face says I "
                "HAVE BEEN WELCOMING PEOPLE TO THE LUXOR FOR ELEVEN YEARS. He is, "
                "however, one of the few people on Trantor who understands that a "
                "guest holding a letter from Hari Seldon is either important, in "
                "danger, or both. He has decided that both is the safer assumption."
            ),
            topics={
                "room": "The elevator is behind the desk. The key card opens Suite Fourteen.",
                "seldon": "Seldon is at Streeling. The Commission pretends not to know where.",
                "trantor": "Everything above us is city. Everything below us is also city.",
                "commission": "The Commission of Public Safety is here to protect the public from safety.",
            },
            on_ask=clerk_topics,
            on_show=clerk_show,
        ),
        "student": NPC(
            key="student",
            names=["student", "graduate student", "young man", "man", "boy"],
            short="student",
            location="streeling_plaza",
            desc=(
                "The student is sitting on the base of the statue with the air of "
                "someone who has discovered that the universe is made of problems "
                "and has decided to major in them. He is holding a copy of the "
                "Hitchhiker's Guide and pretending it is a textbook."
            ),
            topics={
                "statue": "The inscription lost its most important word. The arch still remembers it.",
                "password": "The old arch listens for the first rule of hitchhiking. Say it, don't shout it.",
                "seldon": "Seldon is behind the old wing. The Commission pretends he is not.",
                "library": "The archive needs an Imperial Library card. The Commission issues them to people it is not arresting.",
                "commission": "Linge Chen runs the Commission. He has never been wrong in public.",
            },
            on_ask=student_topics,
        ),
        "librarian": NPC(
            key="librarian",
            names=["librarian", "archivist", "old woman", "woman", "miss"],
            short="librarian",
            location="library",
            desc=(
                "The librarian is a small, precise woman with grey hair and the "
                "expression of someone who has outlasted several empires, two "
                "cataloguing systems, and a revolution in microfilm. She regards "
                "you over a pair of glasses that have been repaired with tape and "
                "defiance."
            ),
            topics={
                "archive": "The archive door opens with an Imperial Library card. The truth is in there, along with the heating duct.",
                "seldon": "Seldon's people have been copying records for years. They think I don't notice.",
                "book": "A book is overdue when it is late. A book is a classic when it is late enough.",
                "library": "We are the memory of a civilization that has forgotten us. Keep your voice down.",
            },
            on_ask=librarian_topics,
            on_give=librarian_give,
            on_show=librarian_show,
        ),
        "seldon": NPC(
            key="seldon",
            names=["seldon", "hari seldon", "professor", "hari"],
            short="Hari Seldon",
            location="seldon_office",
            desc=seldon_desc,
            topics={
                "psychohistory": "Psychohistory predicts crowds, not people. I can tell you what forty billion will do; I cannot tell you what one commissioner will order for lunch.",
                "trial": "Chen will offer you a choice between confession and relevance. Refuse both. Answer NO.",
                "cube": "The warm cube is real. The cold cube is the decoy. Give Chen the cold one.",
                "towel": "Put the real cube in your towel. The Commission scans for radiation, not laundry.",
                "terminus": "A small planet at the edge of the Galaxy. Board the ship with the Encyclopedia's name on it.",
                "mule": "The Plan has a blind spot: a single individual large enough to cast a shadow across history. That is three hundred years away. You have a trial tomorrow.",
            },
            on_ask=seldon_topics,
            on_talk=seldon_talk,
        ),
        "chen": NPC(
            key="chen",
            names=["chen", "linge chen", "commissioner", "commissioner chen"],
            short="Commissioner Linge Chen",
            location="trial_chamber",
            desc=(
                "Commissioner Linge Chen is immaculate. His uniform has no medals, "
                "which is how you know he has real power. He regards you the way a "
                "surgeon regards a minor but interesting inflammation: with "
                "professional curiosity and a schedule."
            ),
            topics={
                "charges": "The charge is spreading psychohistorical alarm. In practice, that means predicting the Empire will fall.",
                "seldon": "Seldon is a mathematician with a talent for publicity. We are giving him a very small planet.",
                "evidence": "If you have something to show, show it. If you have something to give, give it. Do not waste the court's time with a towel.",
                "terminus": "Exile is a mercy, provided it is administered far from the capital and does not appear in the budget.",
            },
            on_ask=chen_topics,
            on_show=chen_show,
            on_give=chen_give,
        ),
        "guard": NPC(
            key="guard",
            names=["guard", "officer", "soldier", "commission officer"],
            short="Commission guard",
            location="trial_chamber",
            desc=(
                "The guard is young, immaculate, and carefully trained not to have "
                "opinions. The training is not entirely successful: his eyes keep "
                "drifting toward the door, as if he would like to be elsewhere when "
                "history happens."
            ),
            topics={
                "trial": "The guard says nothing. His posture says: I am not paid enough for this.",
                "chen": "Another nothing. The guard's jaw tightens.",
                "door": "The guard glances at the launch bay door, then at Chen, then at the floor.",
            },
        ),
    }

    def on_say(g: "Game", text: str) -> bool | None:
        if trial_answer(g, text):
            return True
        if _norm(text) in PASSWORD_PHRASES and g.room().key == "streeling_plaza":
            _open_old_wing(g, "say")
            return True
        return None

    def on_command(g: "Game", verb: str, cmd: object) -> bool | None:
        if verb == "panic" and g.room().key == "streeling_plaza":
            _open_old_wing(g, "panic")
            return True
        if verb in ("yes", "no") and g.room().key == "trial_chamber":
            trial_answer(g, verb)
            return True
        return None

    return World(
        act=1,
        title="The Psychohistorians",
        subtitle="Trantor, 12,020 Era Galactica",
        protagonist="Gaal Dornick",
        start_room="spaceport",
        intro=(
            "You are Gaal Dornick, a young mathematician from the provincial world "
            "of Synnax. You have come to Trantor because Hari Seldon invited you, "
            "and because the alternative was staying home and explaining to your "
            "neighbours why the Galactic Empire is about to fall.\n\n"
            "The Empire is not supposed to fall. It has lasted twelve thousand "
            "years, covered forty million worlds, and produced a bureaucracy of "
            "such exquisite complexity that even its own ministers are not entirely "
            "sure which department they work for. But Seldon has done the math. "
            "The math is not optimistic.\n\n"
            "You have a visa, a suitcase somewhere on a carousel, and a towel. The "
            "Guide considers this a complete survival kit. The Guide has never been "
            "to Trantor."
        ),
        rooms=rooms,
        objects=objects,
        npcs=npcs,
        max_score=100,
        guide_keys=["TRANTOR", "PSYCHOHISTORY"],
        hints=act1_hints,
        on_say=on_say,
        on_command=on_command,
        epilogue=(
            "The Encyclopedia Galactica carries Gaal Dornick away from Trantor and "
            "toward a small planet at the edge of the Galaxy. Behind him, the "
            "Empire continues to be magnificent, enormous, and slightly late. "
            "Ahead of him, a thousand years of history are waiting to be edited."
        ),
    )

