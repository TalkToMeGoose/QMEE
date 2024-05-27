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
    NUM_ROUNDS = 1  # starting with 1 for now to be simple

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

def creating_session(subsession):
    subsession.group_randomly()

class Subsession(BaseSubsession):  # for initialization and group separation
    pass
    # def creating_session(subsession):
    #     subsession.group_randomly()  # for now
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


class Group(BaseGroup):
    node = models.IntegerField(initial=1)
    round_active = models.BooleanField(initial=True)
    round_outcome = models.IntegerField(initial=0)
    last_node = models.IntegerField(initial=1)

    # stop round when someone takes or continuing after last node, otherwise round_active remains true
    @staticmethod
    def stop_round(group: 'Group'):
        players = group.get_players()
        # takes = [p.take for p in players if p.take is not None]
        #
        # if any(takes):
        #     group.round_active = False
        #     group.last_node = group.node
        #     group.round_outcome = 1 if takes[0] else 2
        # elif group.node > C.NUM_NODES:
        #     group.round_active = False
        #     group.last_node = group.node

        # if len(takes) > 0 and takes[0]:
        #     group.round_active = False
        #     group.round_outcome = 1
        #     group.last_node = group.node
        # elif len(takes) > 1 and takes[1]:
        #     group.round_active = False
        #     group.round_outcome = 2
        #     group.last_node = group.node
        # elif group.node == C.NUM_NODES and not any(takes):
        #     group.round_active = False
        #     group.last_node = group.node
        pass

    @staticmethod
    def set_payoffs(group: 'Group'):
        players = group.get_players()  # gets list of players in the group
        takes = [p.take for p in players]  # checks if either player selected take
        for p in players:
            if group.node == C.NUM_NODES and not any(takes):  # if no takes
                if p.id_in_group == 1:
                    p.payoff = C.LARGE_PILES[-1]  # player 1 gets the large pile
                else:
                    p.payoff = C.SMALL_PILES[-1]
            elif group.node < C.NUM_NODES and any(takes):  # if someone takes
                if p.take:
                    p.payoff = C.LARGE_PILES[group.last_node - 1]  # player who took gets large pile
                else:
                    p.payoff = C.SMALL_PILES[group.last_node - 1]  # other player gets small pile

    @staticmethod
    def advance_node(group : 'Group'):
        group.node += 1 #advance to next node
        players = group.get_players()
        for p in players:
            p.take = None # reset take field for next decision
        print(f"Node advanced to: {group.node}. The round is {group.round_number}")
        print(f"Payoffs are now: {C.LARGE_PILES[group.node - 1]} & {C.SMALL_PILES[group.node - 1]}")

    # @staticmethod
    # def advance_round(group):
    #     if group.round_number < C.NUM_ROUNDS:
    #         group.round_active = True

class Player(BasePlayer):
    take = models.BooleanField(
        initial=False,
        label='',
        widget=widgets.RadioSelectHorizontal,
        blank=True,
        choices=[
            [True, 'Take'],
            [False, 'Pass'],
        ],
    )


class Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class WaitPage1(WaitPage):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    wait_for_all_groups = True


class Decision(Page):
    form_model = 'player'
    form_fields = ['take']

    @staticmethod
    def is_displayed(player: Player):  # display page to the appropriate player using even/odd round numbers
        return (
                (player.id_in_group == 1 and player.group.node % 2 != 0 and player.group.round_active) or
                (player.id_in_group == 2 and player.group.node % 2 == 0 and player.group.round_active)
        )

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            node=group.node,
            large_pile=C.LARGE_PILES[group.node - 1], # -1 to match the payoff list index under constants
            small_pile=C.SMALL_PILES[group.node - 1]
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.take:  # If the player decides to take
            player.group.stop_round(player.group)
            player.group.set_payoffs(player.group)
        elif player.group.node == C.NUM_NODES:  # If the last node is reached
            player.group.stop_round(player.group)
            player.group.set_payoffs(player.group)
        else:  # If the player decides to pass
            player.group.advance_node(player.group)


class WaitForDecision(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        pass


class Results(Page):  # shows payoffs for this round
    @staticmethod
    def is_displayed(player: Player):
        return not player.group.round_active

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            last_node=player.group.last_node,  # do i need player and group here?
            large_pile=C.LARGE_PILES[player.group.last_node - 1],
            small_pile=C.SMALL_PILES[player.group.last_node - 1],
            large_pile_pass=C.LARGE_PILES[-1],
            small_pile_pass=C.SMALL_PILES[-1]
        )

    # @staticmethod
    # def before_next_page(player: Player, timeout_happened):
    #     player.group.advance_round(player.group)


# class WaitPage3(WaitPage):
#     @staticmethod
#     def is_displayed(player: Player):
#         return player.round_number < C.NUM_ROUNDS  # page shows when


class ResultsCombined(Page):
    title_text = 'Combined Results'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    # @staticmethod
    # def vars_for_template(player : Player):
    #     all_players = player.in_all_rounds()
    #     combined_payoff =


page_sequence = [
    Welcome,
    WaitPage1,
    Decision,
    WaitForDecision,
    Results,
    #WaitPage3,  # waits for everyone and advances to next round
    # ResultsCombined
]
