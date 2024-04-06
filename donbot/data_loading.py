import string
import os
import json

NO_PUNCTUATION = str.maketrans(
    string.punctuation + string.ascii_letters,
    " " * len(string.punctuation + string.ascii_letters),
)


def load_game_data(data_path):
    with open(data_path, encoding="utf-8") as f:
        return f.read().split("\n\n\n")


def find_game_from_id(games, game_id):
    for game in games:
        if get_game_id(game) == game_id:
            return game
    raise ValueError(f"Game with id {game_id} not found in games")


def load_posts(posts_path, game_id):
    with open(os.path.join(posts_path, f"{game_id}.jsonl")) as f:
        return [json.loads(line) for line in f]


def load_transitions(data_path):
    with open(data_path) as f:
        transition_lines = f.read().split("\n")[3:]

    transitions = {}
    for line in transition_lines:
        line = line.strip().split("\t")
        if len(line) > 1:
            transitions[line[0]] = line[1:]
    return transitions


def get_game_transitions(game, all_transitions):
    return all_transitions[get_game_id(game)]


def get_game_thread(game):
    link = game[: game.find("\n")]
    thread_id = (
        link[link.find("&t=") + 3 :]
        if link.count("&") == 1
        else link[link.find("&t=") + 3 : link.rfind("&")]
    )
    return link, thread_id

def get_game_title(game):
    return game.split("\n")[1]

def get_game_id(game):
    title = get_game_title(game)
    return [i for i in title.translate(NO_PUNCTUATION).split() if i.isdigit()][0]

def get_moderators(game):
    return game.split("\n")[2][len("Moderator: ") :].split(", ")


def get_special_events(game):
    less_one_for_mislynch = False  # whether one less vote is needed for a mislynch
    events = {}  # events relevant for votecounting that happened on specific posts

    notes = game[: game.find("\n\n")].split("\n")[-1][len("Notes: ") :]
    for note in notes.split("; "):
        note = note.replace(" in post ", " on post ")
        if " on post " in note:
            postnumber = note.split(" on post ")[1].replace(";", "")
            postnumber = (
                postnumber[: postnumber.find(" but")]
                if "but" in postnumber
                else postnumber
            )
            if postnumber in events:
                events[postnumber].append(note.split(" on post ")[0])
            else:
                events[postnumber] = [note.split(" on post ")[0]]
        elif "one less for no lynch" in note.lower():
            less_one_for_mislynch = True
    return less_one_for_mislynch, events


def get_player_lines(game):
    return [
        line.split(", ") for line in game[game.find("\nPlayers\n") + 9 :].split("\n")
    ]


def get_players(player_lines):
    players = []
    for line in player_lines:
        players += line[0].split(" replaced ")
    return players


def get_slots(player_lines):
    return [line[0].split(" replaced ") for line in player_lines]


def get_doublevoters(player_lines):
    return [
        line[0].split(" replaced ")
        for line in player_lines
        if "double voter" in line[1].lower() or "doublevoter" in line[1].lower()
    ]


def get_factions(player_lines):
    slots = get_slots(player_lines)
    factions = {}
    for line in player_lines:
        if "town" in line[1].lower():
            factions[str(slots[-1])] = "TOWN"
        elif "serial" in line[1].lower() or "third party" in line[1].lower():
            factions[str(slots[-1])] = "OTHER"
        elif "werewolf" in line[1].lower() or "mafia" in line[1].lower():
            factions[str(slots[-1])] = "MAFIA"
        else:
            print(line[1].lower())
    return factions


def get_slot_fates(player_lines):
    """
    Extracts last day phase that each slot's vote helped decide the outcome.
    This is the phase they died, minus one if they were day-killed (not lynched).
    """
    fates = []
    for line in player_lines:
        if "survived" in line[-1].lower() or "endgamed" in line[-1].lower():
            fates.append(float("inf"))
        else:
            fate_phase = int(line[-1][line[-1].rfind(" ") + 1 :])
            # fate_modifier = 'killed day' in line[-1][:line[-1].rfind(' ')].lower()
            fates.append(max(0, fate_phase))
    return fates


def get_lynches(player_lines):
    slots = get_slots(player_lines)
    lynched = {}
    for line in player_lines:
        if "lynched" in line[-1].lower():
            fate_phase = int(line[-1][line[-1].rfind(" ") + 1 :])
            lynched[fate_phase] = slots[-1]
    return lynched


def parse_game_info(game, all_transitions):
    player_lines = get_player_lines(game)
    lessOneForMislynch, events = get_special_events(game)
    game_id = get_game_id(game)

    return {
        "slots": get_slots(player_lines),
        "players": get_players(player_lines),
        "fates": get_slot_fates(player_lines),
        "lynched": get_lynches(player_lines),
        "factions": get_factions(player_lines),
        "number": game_id,
        "thread": get_game_thread(game)[1],
        "transitions": get_game_transitions(game, all_transitions),
        "moderators": get_moderators(game),
        "doublevoters": get_doublevoters(player_lines),
        "events": events,
        "lessOneForMislynch": lessOneForMislynch,
    }


def get_prediction_target(game, day):
    canPredictTransition, canPredictLynch = True, True
    lynched = get_lynches(game)

    if (
        f"d{day} long twilight"
        in game[: game.find("\n\n")].split("\n")[-1][len("Notes: ") :].lower()
    ):
        canPredictTransition = False
    if (
        f"d{day} hammer after deadline"
        in game[: game.find("\n\n")].split("\n")[-1][len("Notes: ") :].lower()
    ):
        canPredictLynch = False
    if (
        f"d{day} no majority"
        in game[: game.find("\n\n")].split("\n")[-1][len("Notes: ") :].lower()
    ):
        correct = []
        canPredictTransition = False
    elif (
        f"d{day} no lynch"
        in game[: game.find("\n\n")].split("\n")[-1][len("Notes: ") :].lower()
    ):
        correct = "NO LYNCH"
    else:
        correct = lynched[day] if day in lynched else []

    return canPredictTransition, canPredictLynch, correct


class PhaseDataset:
    def __init__(
        self, game_archive_path, transitions_path, posts_path, include_hand_labels=True
    ):
        self.posts_path = posts_path
        self.include_hand_labels = include_hand_labels
        self.games = load_game_data(game_archive_path)
        self.all_transitions = load_transitions(transitions_path)
        self.labels = []
        self.phases = []
        for game in self.games:
            game_id = get_game_id(game)
            game_transitions = self.all_transitions[game_id]
            for day_index, end_point in enumerate(game_transitions):
                day = day_index + 1
                if len(game_transitions) < day + 1:
                    continue
                start_point = 0 if day == 1 else int(game_transitions[day - 1])
                self.phases.append((game_id, day, start_point, end_point))
                self.labels.append(f"Game {game_id}, Day {day}, Thread {get_game_thread(game)[1]}")

    def __len__(self):
        return len(self.phases)
    
    def item_labels(self):
        return self.labels

    def __getitem__(self, idx):
        print(f'{idx} testing...')
        game_id, day, start_point, end_point = self.phases[idx]
        game = find_game_from_id(self.games, game_id)
        game_thread = get_game_thread(game)[1]
        game_posts = load_posts(self.posts_path, game_thread)
        canPredictTransition, canPredictLynch, correct = get_prediction_target(
            game, day
        )
        phase_data = {
            **parse_game_info(game, self.all_transitions),
            "label": self.labels[idx],
            "day": day,
            "posts": game_posts[start_point:],
            "phase_start": start_point,
            "phase_end": end_point,
            "canPredictTransition": canPredictTransition,
            "canPredictLynch": canPredictLynch,
            "correct": correct,
        }

        phase_data['phase_slots'] = [
            slot
            for slot_index, slot in enumerate(phase_data["slots"])
            if phase_data["fates"][slot_index] >= day
        ]
        phase_data['phase_players'] = []
        for slot in phase_data['phase_slots']:
            phase_data['phase_players'] += slot
        
        return phase_data