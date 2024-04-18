import pytest
from donbot.vc.vote_counter import VoteCounter
from donbot.data_loading import PhaseDataset

archive_path = "data/archive.txt"
transitions_path = "data/transitions.tsv"
posts_path = "data/posts/"

dataset = PhaseDataset(archive_path, transitions_path, posts_path)
data_indices = list(range(len(dataset)))
data_labels = dataset.item_labels()

def test_phase_dataset():
    dataset = PhaseDataset(archive_path, transitions_path, posts_path)
    phase = dataset[1]
    assert phase["correct"] == ["Substrike22"]
    assert phase["posts"][0]["number"] == "470"


@pytest.mark.parametrize("data_index", data_indices, ids=data_labels)
def test_vote_extraction(data_index):
    phase = dataset[data_index]
    phase_events = phase["events"]
    votecounter = VoteCounter(
        slots=phase["phase_slots"],
        events=phase_events,
        lessOneForMislynch=phase["lessOneForMislynch"],
        doublevoters=phase["doublevoters"],
        flag_unmatched_votes=False,
    )

    # then we consider each post in the phase,
    # predicting the transition and lynch target if possible
    transition_start = 0
    transition_end = 0
    for post in phase["posts"]:
        if not votecounter.choice:
            # votecounter.process_events(post)
            votecounter.process_votes(post["user"], post["content"], post["number"])
        elif not transition_start:
            if post["user"] in phase["moderators"]:
                transition_start = int(post["number"])
        elif post["user"] in phase["moderators"]:
            transition_end = int(post["number"])
        else:
            break

    if phase["canPredictLynch"]:
        if votecounter.choice != phase["correct"]:
            for line in votecounter.votecount.votelog:
                print(line)
        assert votecounter.choice == phase["correct"]
    if phase["canPredictTransition"]:
        transition_range = list(range(transition_start, transition_end + 1))
        if int(phase["phase_end"]) not in transition_range:
            for line in votecounter.votecount.votelog:
                print(line)
        assert int(phase["phase_end"]) in transition_range


# {game_number: [post_number, post_number, ...]}
# ONLY includes posts that are *rightly* not matched to a player during normal processing
excluded_for_vote_unmatch_flagging = {
    '1091': [35, 131, 484]
}


@pytest.mark.parametrize("data_index", data_indices, ids=data_labels)
def test_unmatch_flagged_vote_extraction(data_index):

    phase = dataset[data_index]
    phase_events = phase["events"]
    votecounter = VoteCounter(
        slots=phase["phase_slots"],
        events=phase_events,
        lessOneForMislynch=phase["lessOneForMislynch"],
        doublevoters=phase["doublevoters"],
        flag_unmatched_votes=True,
    )

    # handling exclusions
    game_number = phase["number"]
    excluded_posts = []
    if game_number in excluded_for_vote_unmatch_flagging:
        excluded_posts = excluded_for_vote_unmatch_flagging[game_number]

    # then we consider each post in the phase,
    # predicting the transition and lynch target if possible
    transition_start = 0
    transition_end = 0
    for post in phase["posts"]:
        if not votecounter.choice:
            if int(post["number"]) in excluded_posts:
                continue
            # votecounter.process_events(post)
            votecounter.process_votes(post["user"], post["content"], post["number"])
        elif not transition_start:
            if post["user"] in phase["moderators"]:
                transition_start = int(post["number"])
        elif post["user"] in phase["moderators"]:
            transition_end = int(post["number"])
        else:
            break

    if phase["canPredictLynch"]:
        if votecounter.choice != phase["correct"]:
            for line in votecounter.votecount.votelog:
                print(line)
        assert votecounter.choice == phase["correct"]
    if phase["canPredictTransition"]:
        transition_range = list(range(transition_start, transition_end + 1))
        if int(phase["phase_end"]) not in transition_range:
            for line in votecounter.votecount.votelog:
                print(line)
        assert int(phase["phase_end"]) in transition_range
