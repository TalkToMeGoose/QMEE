from otree.api import *
import itertools  # for randomizing participants into balanced groups
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

    NUM_NODES = 6  # number of decision points ("nodes" or turns) per round. Essentially, how long the centipede is.
    # NOTE: each player thus takes (NUM_NODES/2) turns rach round
    NUM_ROUNDS = 2  # starting with 1 for now to be simple
    NUM_TURNS_TOTAL = NUM_NODES * NUM_ROUNDS  # number of turns across all rounds

    # create payoffs for turn 1 in all games, as well as multiplier
    LARGE_PILE = 4
    SMALL_PILE = 1
    MULTIPLIER = 2

    # create list for subsequent payoffs
    LARGE_PILES = []
    SMALL_PILES = []

    # create subsequent payoffs
    for node in range(NUM_NODES + 1):
        LARGE_PILES.append(LARGE_PILE * MULTIPLIER ** node)
        SMALL_PILES.append(SMALL_PILE * MULTIPLIER ** node)


class Subsession(BaseSubsession):  # for initialization and group separation

    # set initial round and turn numbers
   # round = models.IntegerField(initial=1) #commenting this out to try and fix. i think its unnecessary since its tracked by otree api
    turn = models.IntegerField(initial=1)
    # this may conflict with for loop above

def creating_session(subsession):
    pass #for now
    # maybe not needed
    # from turn 1 to total number of turns
    # for x in range(1, C.NUM_TURNS_TOTAL + 1):
    #     # groups turns into rounds based on number of turns per round
    #     subsession.round_number = int(np.ceil(x / C.NUM_NODES))
    #     # determine position of total turn count within respective round
    #     subsession.turn = x - (int(np.ceil(x / C.NUM_NODES)) - 1) * C.NUM_NODES
    #
    # # groups randomly the first round and holds those groups throughout
    # if subsession.round_number in C.FIRST_TURNS:
    #     subsession.group_randomly()
    # else:
    #     x = C.FIRST_TURNS[int(np.ceil(subsession.round_number / C.NUM_NODES)) - 1]
    #     subsession.group_like_round(x)

    # # FOR LATER: places people into treatment group for entire experiment
    # treatments = itertools.cycle([control, higher_fixed, higher_random])
    # if subsession.round_number == 1:
    #     for player in subsession.get_players():
    #         participant = player.participant
    #         participant.treatment = next(treatments)
    # QUESTIONS: what is the participant <-> group relationship here?
    # are participants assigned to treatments or groups of participants (which I am aiming for)

    # shuffles players in groups randomly
    # may take this out later to do treatment stuff

def advance_round(subsession):
    for g in subsession.get_groups():
        if g.subsession.round_number < C.NUM_ROUNDS:
            g.in_round(g.round_number + 1).round_active = True

class Group(BaseGroup):
    round_active = models.BooleanField(initial=True)
    round_outcome = models.IntegerField(initial=0)
    last_node = models.IntegerField(initial=1)

    # stop round when someone takes or continuing after last node
    @staticmethod
    def stop_round(group: 'Group'):
        players = group.get_players()
        takes = [p.take for p in players] # take function below this one
        if group.subsession.turn == C.NUM_NODES and not any(takes): # if no one take (i.e. players reach end)
            group.round_active = False
            group.last_node = group.subsession.turn
        elif takes[0]:
            group.round_active = False
            group.round_outcome = 1
            group.last_node = group.subsession.turn
        elif takes[1]:
            group.round_active = False
            group.round_outcome = 2
            group.last_node = group.subsession.turn

        for grp in group.in_rounds(group.round_number + 1, C.LAST_TURNS[group.subsession.round_number - 1]):
            grp.round_active = group.in_round(group.round_number).round_active
            grp.round_outcome = group.in_round(group.round_number).round_outcome
            grp.last_node = group.in_round(group.round_number).last_node


def set_payoffs(group: Group):
    players = group.get_players() # gets list of players in the group
    takes = [p.take for p in players] # checks if either player selected take
    for p in players:
        if group.subsession.turn == C.NUM_NODES and not any(takes): # if no takes
            if p.id_in_group == 1:
                p.payoff = C.LARGE_PILES[-1] # player 1 gets the large pile
            else:
                p.payoff = C.SMALL_PILES[-1]
        elif group.subsession.turn < C.NUM_NODES and any(takes): # if someone takes
            if p.take:
                p.payoff = C.LARGE_PILES[group.last_node - 1] # player who took gets large pile
            else:
                p.payoff = C.SMALL_PILES[group.last_node - 1] # other player gets small pile


class Player(BasePlayer):
    take = models.BooleanField(
        label='',
        widget=widgets.RadioSelectHorizontal,
    )

class Welcome(Page):
    @staticmethod
    def is_displayed(player : Player):
        return player.round_number == 1

class WaitPage1(WaitPage):

    @staticmethod
    def is_displayed(player : Player):
        return player.round_number == 1

    wait_for_all_groups = True

class Decision(Page):
    form_model = 'player'
    form_fields = ['take']

    @staticmethod
    def is_displayed(player: Player): # display page to the appropriate player using even/odd round numbers
        return (
                (player.id_in_group == 1 and player.round_number % 2 != 0 and player.group.round_active) or
                (player.id_in_group == 2 and player.round_number % 2 == 0 and player.group.round_active)
        )

    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        turn_index = subsession.turn - 1
        return dict(
            node=subsession.turn,
            large_pile=C.LARGE_PILES[turn_index],
            small_pile=C.SMALL_PILES[turn_index]
        )

@staticmethod
def before_next_page(player : Player, timeout_happened):
    player.group.stop_round()
    player.group.set_payoffs()

class WaitPage2(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        pass

class Results(Page): # shows payoffs for this round
    @staticmethod
    def is_displayed(player : Player):
        return not player.group.round_active

    @staticmethod
    def vars_for_template(player : Player):
        return dict(
            #round=player.subsession.round, # maybe works without this
            last_node=player.group.last_node, # do i need player and group here?
            large_pile=C.LARGE_PILES[player.group.last_node - 1],
            small_pile=C.SMALL_PILES[player.group.last_node - 1],
            large_pile_pass=C.LARGE_PILES[-1],
            small_pile_pass=C.SMALL_PILES[-1]
        )


class WaitPage3(WaitPage):
    @staticmethod
    def is_displayed(player : Player):
        if player.round_number in C.LAST_TURNS:
            return True
        else:
            return False

    wait_for_all_groups = True
    after_all_players_arrive = 'advance_round'

class CombinedResults(Page):
    @staticmethod
    def is_displayed(player : Player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [
    Welcome,
    WaitPage1,
    Decision,
    WaitPage2,
    Results,
    WaitPage3,
    CombinedResults
]