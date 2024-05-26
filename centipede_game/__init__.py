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
    NUM_ROUNDS = 1
    # create payoffs. small/large pot? alternating
    # payoffs


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

# Functions

# setting the payoff that is on the table for both players
# def set_payoffs(group):
#     p1 = group.get_player_by_id(1)
#     p2 = group.get_player_by_id(2)

# to set participants into permanent control/treatment1/treatment2
# group for the entire experiment
# def creating_session(subsession):
#     treatments = itertools.cycle([control, higher_fixed, higher_random])
#     if subsession.round_number == 1:
#         for player in subsession.get_players():
#             participant = player.participant
#             participant.treatment = next(treatments)
# #QUESTIONS: what is the participant <-> group relationship here?
# #are participants assigned to treatments or groups of participants (which I am aiming for)


# PAGES
class Decision(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
