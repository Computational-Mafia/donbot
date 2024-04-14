import pytest
from donbot.vc.vote_counter import VoteCounter
from donbot.data_loading import PhaseDataset

archive_path = 'data/archive.txt'
transitions_path = 'data/transitions.tsv'
posts_path = 'data/posts/'

dataset = PhaseDataset(archive_path, transitions_path, posts_path)
data_indices = list(range(len(dataset)))
data_labels = dataset.item_labels()


def test_phase_dataset():
    dataset = PhaseDataset(archive_path, transitions_path, posts_path)
    phase = dataset[1]
    assert phase['correct'] == ["Substrike22"]
    assert phase['posts'][0]['number'] == '470'


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
            votecounter.process_votes(post['user'], post['content'], post['number'])
        elif not transition_start:
            if post['user'] in phase['moderators']:
                transition_start = int(post['number'])
        elif post['user'] in phase['moderators']:
            transition_end = int(post['number'])
        else:
            break

    if phase['canPredictLynch']: 
        if votecounter.choice != phase['correct']:
            for line in votecounter.votecount.votelog:
                print(line)
        assert votecounter.choice == phase['correct']
    if phase['canPredictTransition']:
        transition_range = list(range(transition_start, transition_end+1))
        if int(phase['phase_end']) not in transition_range:
            for line in votecounter.votecount.votelog:
                print(line)
        assert int(phase['phase_end']) in transition_range
