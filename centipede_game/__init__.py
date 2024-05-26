from otree.api import *
import itertools  # for randomizing participants into balanced groups
import numpy as np
c = Currency

author = 'Adam Hardaker, Universitaet Kassel EBGo' \
    'Rachel Hayward, Universitaet Kassel EBGo'

doc = """
oTree App for the Centipede Game as in McKelvey and Palfrey (1992), An Experimental Study of the Centipede Game, 
Econometrica, 60(4): 803-836.
"""


class C(BaseConstants):
    NAME_IN_URL = 'centipede_game'
    PLAYERS_PER_GROUP = 2

    NUM_TURNS_PER_ROUND = 6  # number of decision points (i.e. turns) per round.
    # NOTE: each player thus takes (NUM_NODES_PER_GAME/2) turns
    NUM_ROUNDS = 1  # starting with 1 for now to be simple
    NUM_TURNS_TOTAL = NUM_TURNS_PER_ROUND * NUM_ROUNDS  # number of turns across all rounds

    # define starting and ending turns of each round
    FIRST_TURNS = np.arange(1, NUM_TURNS_TOTAL, NUM_TURNS_PER_ROUND)
    LAST_TURNS = np.arange(NUM_TURNS_PER_ROUND, NUM_TURNS_TOTAL + 1, NUM_TURNS_PER_ROUND)

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


class Subsession(BaseSubsession):  # for initialization and group separation

    # set initial round and turn numbers
    round = models.IntegerField(initial=1)
    # this may conflict with round_number below
    turn = models.IntegerField(initial=1)
    # this may conflict with for loop above


def creating_session(subsession):

    # from turn 1 to total number of turns
    for x in range(1, C.NUM_TURNS_TOTAL+1):
        # groups turns into rounds based on number of turns per round
        subsession.in_round(x).round = np.ceil(x/C.NUM_TURNS_PER_ROUND)  # do i need to make sure this is an integer?
        # determine position of total turn count within respective round
        subsession.in_round(x).turn = x - (np.ceil(x/C.NUM_TURNS_PER_ROUND)-1)*C.NUM_TURNS_PER_ROUND  # this too?

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
    def advance_round(subsession):    # should be referenced on html file as
        # after_all_players_arrive = 'advance_round' on last wait page
        for g in subsession.get_groups():
            if g.subsession.round < C.NUM_ROUNDS:
                g.in_round(g.round_number + 1).round_on = True


class Group(BaseGroup):
    round_on = models.BooleanField(initial=True)
    round_outcome = models.IntegerField(initial=0)
    last_turn_in_round = models.IntegerField(initial=1)

# stop round when someone takes
    def stop_round(group):
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

    # unsure about these rn
    take = models.BooleanField(
        label='',
        widget=widgets.RadioSelectHorizontal,
    )

# role: player role (set by group)
# decisions made by player (pass or take)
# payoff: final payoff for player

# Functions

# PAGES


class FirstPage(Page):
    def is_displayed(player):
        return player.round_number == 1


class Welcome(FirstPage):
    pass

# class Instructions(Firstpage):
#     def vars_for_template(self):
#         return dict(
#             turns = int(C.NUM_TURNS_TOTAL)
#             rounds_range = C.rounds_range,
#         )
# unsure how/if i will use this


class WaitPage1(WaitPage):

    def is_displayed(player):
        return player.round_number == 1

    wait_for_all_groups = True


class Decision(Page):

    form_model = 'player'
    form_fields = ['take']

    def is_displayed(player):
        group = player.group
        if player.id_in_group == 1 and player.round_number % 2 != 0 and group.round_on:
            return True
        elif player.id_in_group == 2 and player.round_number % 2 == 0 and group.round_on:
            return True
        else:
            return False

    def vars_for_template(player):
        return dict(
            round=player.subsession.round,
            turn=player.subsession.turn,
            LARGE_PILE=C.LARGE_PILES[player.subsession.turn - 1],
            SMALL_PILE=C.SMALL_PILES[player.subsession.turn - 1]
        )

    def before_next_page(group):
        return group.stop_round(), group.set_payoffs()


class WaitPage2(WaitPage):
    def after_all_players_arrive(self):
        pass


class Results(Page):
    @staticmethod
    def is_displayed(player):
        if player.round_number in C.LAST_TURNS:
            return True
        else:
            return False

    @staticmethod
    def vars_for_template(group):
        return dict(
            round=group.subsession.round,
            last_turn_in_round=group.last_turn_in_round,
            large_pile=C.LARGE_PILES[group.last_turn_in_round - 1],
            small_pile=C.SMALL_PILES[group.last_turn_in_round - 1],
            large_pile_pass=C.LARGE_PILES[-1],
            small_pile_pass=C.SMALL_PILES[-1]
        )


class WaitPage3(WaitPage):
    def is_displayed(player):
        if player.round_number in C.LAST_TURNS:
            return True
        else:
            return False
    wait_for_all_groups = True
    after_all_players_arrive = 'advance_round'


page_sequence = [
    Welcome,
    # Instructions,
    WaitPage1,
    Decision,
    WaitPage2,
    Results,
    WaitPage3
    ]
