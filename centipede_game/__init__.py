from otree.api import *
import itertools # for randomizing participants into balanced groups

author = 'Adam Hardaker, Universitaet Kassel EBGo' \
    'Rachel Hayward, Universitaet Kassel EBGo'

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'centipede_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1 # starting with 1 for now to be simple
    NUM_TURNS_PER_PLAYER = 3 #each player makes 3 decisions per round
    # create payoffs. small/large pot? alternating
    # payoffs


class Subsession(BaseSubsession): # for initialization and group separation
    pass

# places people into treatment group for entire experiment
# def creating_session(subsession):
#     treatments = itertools.cycle([control, higher_fixed, higher_random])
#     if subsession.round_number == 1:
#         for player in subsession.get_players():
#             participant = player.participant
#             participant.treatment = next(treatments)
# #QUESTIONS: what is the participant <-> group relationship here?
# #are participants assigned to treatments or groups of participants (which I am aiming for)

class Group(BaseGroup):
    pass

# track current round (1-6, or 4)

# track current decision cycle or "turn" (how far along centipede we are, 1-6)

# assigns player roles to player 1 or 2 for each round

# Game logic: decisions made by players and resulting changes in game state

class Player(BasePlayer):
    pass

# role: player role (set by group)
# decisions made by player (pass or take)
# payoff: final payoff for player

# Functions



# setting the payoff that is on the table for both players
# def set_payoffs(group):
#     p1 = group.get_player_by_id(1)
#     p2 = group.get_player_by_id(2)



# PAGES
class Decision(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Decision, ResultsWaitPage, Results]
