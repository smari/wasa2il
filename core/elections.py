import json
import logging
import random

from pyvotecore.schulze_method import SchulzeMethod as Condorcet
from pyvotecore.schulze_npr import SchulzeNPR as Schulze
from pyvotecore.schulze_stv import SchulzeSTV as STV

# This is the old custom Schulze code. For now we continue to use it by
# default, silently comparing with results from pyvotecore (canarying).
import schulze

logger = logging.getLogger(__name__)


class BallotCounter(object):
    """
    This class contains the results of an election, making it easy to
    tally up the results using a few different methods.
    """
    VOTING_SYSTEMS = (
        ('condorcet', 'Condorcet'),
        ('schulze', 'Schulze, Ordered list'),
        ('schulze_old', 'Schulze, Ordered list (old)'),
        ('schulze_new', 'Schulze, Ordered list (new)'),
        ('stcom', 'Steering Committee Election'),
        ('stv1', 'STV, Single winner'),
        ('stv2', 'STV, Two winners'),
        ('stv3', 'STV, Three winners'),
        ('stv4', 'STV, Four winners'),
        ('stv5', 'STV, Five winners'),
        ('stv10', 'STV, Ten winners')
    )

    def __init__(self, ballots=None):
        """
        Ballots should be a list of lists of (rank, candidate) tuples.
        """
        self.ballots = ballots or []
        self.candidates = self.get_candidates()

    def system_name(self, system):
        return [n for m, n in self.VOTING_SYSTEMS if m == system][0]

    def load_ballots(self, filename):
        """Load ballots from disk"""
        with open(filename, 'r') as fd:
            self.ballots += json.load(fd, encoding='utf-8')
        self.candidates = self.get_candidates()
        return self

    def save_ballots(self, filename):
        """Save the ballots to disk.

        Ballots are shuffled before saving, to further anonymize the data
        (user IDs will already have been stripped).
        """
        unicode_ballots = []
        for ballot in self.ballots:
            unicode_ballots.append(
               [(rank, unicode(cand)) for rank, cand in ballot])
        random.shuffle(unicode_ballots)
        with open(filename, 'w') as fd:
            json.dump(unicode_ballots, fd, encoding='utf-8', indent=1)

    def get_candidates(self):
        candidates = {}
        for ballot in self.ballots:
            for rank, candidate in ballot:
                candidates[candidate] = 1
        return candidates.keys()

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

    def schulze_results_old(self):
        candidates = self.candidates
        preference = schulze.rank_votes(self.ballots, candidates)
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)
        ordered_candidates = schulze.get_ordered_voting_results(strongest_paths)
        return [cand for cand in ordered_candidates]

    def schulze_results_new(self, winners=None):
        if winners is None:
            winners = max(len(b) for b in self.ballots)
        return Schulze(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                winner_threshold=min(winners, len(self.candidates)),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()['order']

    def schulze_results(self, winners=None):
        """Wrapper to canary new schulze code, comparing with old"""
        old_style = self.schulze_results_old()
        new_style = self.schulze_results_new(winners=winners)
        if old_style != new_style:
            logger.warning('Schulze old result does not match schulze new!')
        else:
            logger.info('Schulze old and new match, hooray.')
        return old_style

    def stv_results(self, winners=None):
        if winners is None:
            winners = 1
        return sorted(list(STV(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                required_winners=min(winners, len(self.candidates)),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()['winners']))

    def condorcet_results(self):
        result = Condorcet(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()
        if not result.get('tied_winners'):
            return [result['winner']]
        else:
            return []

    def stcom_results(self):
        """Icelandic Pirate party steering committee elections.

        Returns 10 or 11 members; the first five are the steering committee,
        the next five are the deputies (both selected using STV).  The 11th
        is the condorcet winner, if there is one. Note that the 11th result
        will be a duplicate.
        """
        stcom = self.stv_results(winners=5)
        deputies = list(set(self.stv_results(winners=10)) - set(stcom))
        condorcet = self.condorcet_results()
        return sorted(stcom) + sorted(deputies) + condorcet

    def results(self, method, winners=None):
        assert(method in [system for system, name in self.VOTING_SYSTEMS])

        if method == 'schulze':
            return self.schulze_results(winners=winners)

        elif method == 'schulze_old':
            return self.schulze_results_old()

        elif method == 'schulze_new':
            return self.schulze_results_new(winners=winners)

        elif method == 'condorcet':
            return self.condorcet_results()

        elif method == 'stcom':
            return self.stcom_results()

        elif method.startswith('stv'):
            return self.stv_results(winners=int(method[3:] or 1))

        else:
            raise Exception('Invalid voting method: %s' % method)


if __name__ == "__main__":
    import sys

    # Configure logging
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    try:
        system = sys.argv[1]
        filenames = sys.argv[2:]
    except IndexError:
        print('Usage: %s <system> <ballot files ...>' % sys.argv[0])
        sys.exit(1)

    bc = BallotCounter()
    for fn in filenames:
        bc.load_ballots(fn)

    print('Voting system:\n\t%s (%s)' % (bc.system_name(system), system))
    print('')
    print('Loaded %d ballots from:\n\t%s' % (len(bc.ballots),
                                             '\n\t'.join(filenames)))
    print('')
    print('Results:\n\t%s' % ', '.join(bc.results(system)))
    print('')

else:
    # Suppress errors in case logging isn't configured elsewhere
    logger.addHandler(logging.NullHandler())
