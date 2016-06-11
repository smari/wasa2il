# FIXME: Do we prefer proportional representation?
#from pyvotecore.schulze_pr import SchulzePR as Schulze
from pyvotecore.schulze_npr import SchulzeNPR as Schulze
from pyvotecore.stv import STV


class BallotCounter(object):
    """
    This class contains the results of an election, making it easy to
    tally up the results using a few different methods.
    """
    VOTING_SYSTEMS = (
        ('schulze', 'Schulze, Ordered list'),
        ('stv1', 'STV, Single winner'),
        ('stv2', 'STV, Two winners')
    )

    def __init__(self, ballots):
        """
        Ballots should be a list of lists of (rank, candidate) tuples.
        """
        self.ballots = ballots

    def ballots_as_lists(self):
        for ballot in self.ballots:
            yield([candidate for rank, candidate in sorted(ballot)])

    def ballots_as_rankings(self):
        for ballot in self.ballots:
            rankings = {}
            for rank, candidate in ballot:
                rankings[candidate] = rank
            yield(rankings)

    def hashes_with_counts(self, ballots):
        for ballot in ballots:
            yield {"count": 1, "ballot": ballot}

    def schulze_results(self, winners=None):
        if winners is None:
            winners = max(len(b) for b in self.ballots)
        return Schulze(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                winner_threshold=winners,
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()['order']

    def stv_results(self, winners=None):
        if winners is None:
            winners = 1
        return list(STV(
                list(self.hashes_with_counts(self.ballots_as_lists())),
                required_winners=winners
            ).as_dict()['winners'])

    def results(self, method, winners=None):
        assert(method in [system for system, name in self.VOTING_SYSTEMS])

        if method == 'schulze':
            return self.schulze_results(winners=winners)

        elif method == 'stv1':
            return self.stv_results(winners=1)

        elif method == 'stv2':
            return self.stv_results(winners=2)

        else:
            raise Exception('Invalid voting method: %s' % method)
