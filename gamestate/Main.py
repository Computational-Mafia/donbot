from GameState import GameState, Game
from Component import Component


def main():
    # Testing code
    """
    game = Game('large_normal_186')
    game.load_events()
    game.process_events()
    print(game.generate_vote_count(278))
    print('\nNow in RC style!\n')
    print(game.generate_vote_count(278, style='large_normal_186'))
    my_list = Component.create('players_list', game_state=game.game_state, post=game.game_state.post)
    print(my_list.generate())
    print('\nLiving Players:\n')
    my_list = Component.create('players_list', game_state=game.game_state, post=game.game_state.post, filter='living')
    print(my_list.generate())
    print('\nDead Players:\n')
    my_list = Component.create('players_list', game_state=game.game_state, post=game.game_state.post, filter='dead')
    print(my_list.generate())
    print('\nModkilled Players:\n')
    my_list = Component.create('players_list', game_state=game.game_state, post=game.game_state.post, filter='modkilled')
    print(my_list.generate())
    print('breakpoint')
    """

    game = Game('mini_theme_1974')
    game.load_events()
    game.process_events()
    for election in game.game_state.elections:
        for vc in election.vote_counts:
            print(game.generate_vote_count(vc, style='Micc') + '\n\n')
    print('breakpoint')

if __name__ == '__main__':
    main()
