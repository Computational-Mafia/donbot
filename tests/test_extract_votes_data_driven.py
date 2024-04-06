import pytest
from donbot.vc import vote_extracter
from donbot.data_loading import PhaseDataset
from donbot.vc.vote_count import VoteCount

archive_path = "data/archive.txt"
transitions_path = "data/transitions.tsv"
posts_path = "data/posts/"

dataset = PhaseDataset(archive_path, transitions_path, posts_path)
data_indices = list(range(len(dataset)))
data_labels = dataset.item_labels()


@pytest.mark.parametrize("data_index", data_indices, ids=data_labels)
def test_vote_extraction(data_index):

    # load the phase data
    phase_data = dataset[data_index]

    # states of phase players and phase slots are mutable, so we make copies
    phase_slots = phase_data["phase_slots"].copy()
    phase_players = phase_data["phase_players"].copy()

    # initialize votecount and votecounter objects
    votecounter = vote_extracter.VoteExtracter(phase_players)
    votecount = VoteCount(
        phase_slots,
        meta={"correct": phase_data["correct"]},
        lessOneForMislynch=phase_data["lessOneForMislynch"],
        doublevoters=phase_data["doublevoters"],
    )
    
    # then we consider each post in the phase,
    for post in phase_data["posts"]:
        pass

        # first if the post is a special event, 
        # we update the votecount and votecounter objects accordingly
        # three types of events: killed, reset, voted

    
    
    # next we pass the post to the votecounter, and update the votecount object accordingly
    # after each update, we check if the votecount object has a majority
    # if so, we check if the votecounter object has the correct player as the lynch target
    # we also scan for the next moderator post to predict the transition
    # the test fails if the correct lynch target is not identified or if the transition is not predicted correctly AND we expect a correct prediction to be possible
    # we generate a final votecount and maintain a votelog throughout simulation for debugging purposes
