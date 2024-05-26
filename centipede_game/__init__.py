from otree.api import *
import itertools # for randomizing participants into balanced groups
import numpy as np

author = 'Adam Hardaker, Universitaet Kassel EBGo' \
    'Rachel Hayward, Universitaet Kassel EBGo'

doc = """
oTree App for the Centipede Game as in McKelvey and Palfrey (1992), An Experimental Study of the Centipede Game, 
Econometrica, 60(4): 803-836.
"""


class C(BaseConstants):
    NAME_IN_URL = 'centipede_game'
    PLAYERS_PER_GROUP = 2

    NUM_TURNS_PER_ROUND = 6 # number of decision points (i.e. turns) per round.
    # NOTE: each player thus takes (NUM_NODES_PER_GAME/2) turns
    NUM_ROUNDS = 1 # starting with 1 for now to be simple
    NUM_TURNS_TOTAL = NUM_TURNS_PER_ROUND * NUM_ROUNDS # number of turns across all rounds

    # define starting and ending turns of each round
    FIRST_TURNS = np.arrange(1, NUM_TURNS_TOTAL, NUM_TURNS_PER_ROUND)
    LAST_TURNS = np.arrange(NUM_TURNS_PER_ROUND, NUM_TURNS_TOTAL + 1, NUM_TURNS_PER_ROUND)

    # create payoffs for turn 1 in all games, as well as multiplier
    LARGE_PILE = 4
    SMALL_PILE = 1
    MULTIPLIER = 2

    # create list for subsequent payoffs
    LARGE_PILES = []
    SMALL_PILES = []

    # create subsequent payoffs
    for turn in range(NUM_TURNS_PER_ROUND + 1):
        LARGE_PILES.append(LARGE_PILE * MULTIPLIER ** turn)
        SMALL_PILES.append(SMALL_PILE * MULTIPLIER ** turn)


class Subsession(BaseSubsession): # for initialization and group separation

    # set initial round and turn numbers
    round = models.IntegerField(initial=1)
    # this may conflict with round_number below
    turn = models.IntegerField(initial=1)
    # this may conflict with for loop above


def creating_session(subsession):

    # from turn 1 to total number of turns
    for x in range(1, C.NUM_TURNS_TOTAL+1)
        # groups turns into rounds based on number of turns per round
        subsession.in_round(x).round = np.ceil(x/C.NUM_TURNS_PER_ROUND)
        # determine position of total turn count within respective round
        subsession.in_round(x).turn = x - (np.ceil(x/C.NUM_TURNS_PER_ROUND)-1)*C.NUM_TURNS_PER_ROUND

    # # places people into treatment group for entire experiment
    # treatments = itertools.cycle([control, higher_fixed, higher_random])
    # if subsession.round_number == 1:
    #     for player in subsession.get_players():
    #         participant = player.participant
    #         participant.treatment = next(treatments)
# QUESTIONS: what is the participant <-> group relationship here?
# are participants assigned to treatments or groups of participants (which I am aiming for)

# shuffles players in groups randomly
# may take this out later to do treatment stuff
        if subsession.round_number in C.FIRST_TURNS:
            subsession.group_randomly()
        else:
            x = C.FIRST_TURNS[int(np.ceil(subsession.round_number / C.NUM_TURNS_PER_ROUND)) - 1]
            subsession.group_like_round(x)

# introduce logic to continue to next round
 def advance_game(subsession):
        for g in subsession.get_groups():
            if g.subsession.round < C.NUM_ROUNDS:
                g.in_round(g.round_number + 1).round_on = True

class Group(BaseGroup):

    round_on = models.BooleanField(initial=True)
    round_outcome = models.IntegerField(initial=0)
    last_turn_in_round = models.IntegerField(initial=1)

# stop game when someone takes
    def stop_game(group):
        players = group.get_players()
        takes = [p.take for p in players]
        if takes[0]:
            group.round_on = False
            group.round_outcome = 1
            group.last_turn_in_round = group.subsession.turn
        elif takes[1]:
            group.round_on = False
            group.round_outcome = 2
            group.last_turn_in_round = group.subsession.turn
        elif group.subsession.turn == C.NUM_TURNS_PER_ROUND and not any(takes):
            group.round_on = False
            group.last_turn_in_round = group.subsession.turn

        for group in group.in_rounds(group.round_number + 1, C.LAST_TURNS[group.subsession.round - 1]):
            group.round_on = group.in_round(group.round_number).round_on
            group.round_outcome = group.in_round(group.round_number).round_outcome
            group.last_turn_in_round = group.in_round(group.round_number).last_turn_in_round

 def set_payoffs(group):
        players = group.get_players()
        takes = [p.take for p in players]
        for p in group.get_players():
            if group.subsession.turn == C.NUM_TURNS_PER_ROUND and not any(takes):
                if p.id_in_group == 1:
                    p.payoff = c(C.LARGE_PILES[-1])
                else:
                    p.payoff = C.SMALL_PILES[-1]
            elif group.subsession.turn < C.NUM_TURNS_PER_ROUND and any(takes):
                if p.take:
                    p.payoff = c(C.LARGE_PILES[group.last_node - 1])
                else:
                    p.payoff = c(C.SMALL_PILES[group.last_node - 1])

# track current round (1-6, or 4)

# track current decision cycle or "turn" (how far along centipede we are, 1-6)

# assigns player roles to player 1 or 2 for each round

# Game logic: decisions made by players and resulting changes in game state

class Player(BasePlayer):

    #unsure about these rn
    take = models.BooleanField(
        label='',
        widget=widgets.RadioSelectHorizontal,

# role: player role (set by group)
# decisions made by player (pass or take)
# payoff: final payoff for player

# Functions

# PAGES
class Decision(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [Decision, ResultsWaitPage, Results]
