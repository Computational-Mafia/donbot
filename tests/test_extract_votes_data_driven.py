import pytest
from donbot.vc.vote_counter import VoteCounter
from donbot.data_loading import PhaseDataset
# import markdown2 as md

archive_path = 'data/archive.txt'
transitions_path = 'data/transitions.tsv'
posts_path = 'data/posts/'

dataset = PhaseDataset(archive_path, transitions_path, posts_path)
data_indices = list(range(len(dataset)))[:1]
data_labels = dataset.item_labels()


@pytest.mark.parametrize('data_index', data_indices, ids=data_labels)
def test_vote_extraction(data_index):

    phase = dataset[data_index]
    phase_events = phase['events']
    votecounter = VoteCounter(
        slots=phase['phase_slots'],
        events=phase_events,
        lessOneForMislynch=phase['lessOneForMislynch'],
        doublevoters=phase['doublevoters'],
    )
    
    # then we consider each post in the phase, 
    # predicting the transition and lynch target if possible
    transition_start = 0
    transition_end = 0
    for post in phase['posts']:
        if not votecounter.choice:
            # votecounter.process_events(post)
            votecounter.process_votes(post)
        elif not transition_start:
            if post['user'] in phase['moderators']:
                transition_start = post['number']
        elif not transition_end:
            if post['user'] in phase['moderators']:
                transition_end = int(post['number'])
        else:
            break

    if phase['canPredictLynch']: 
        assert votecounter.choice == phase['correct']
    if phase['canPredictTransition']:
        transition_range = list(range(transition_start, transition_end))
        assert int(phase['phase_end']) in transition_range
