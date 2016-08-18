import datetime
import copy
import json
import logging
import random
import sys

from pyvotecore.schulze_method import SchulzeMethod as Condorcet
from pyvotecore.schulze_npr import SchulzeNPR as Schulze
from pyvotecore.schulze_stv import SchulzeSTV
from pyvotecore.stv import STV

# This is the old custom Schulze code. For now we continue to use it by
# default, silently comparing with results from pyvotecore (canarying).
import schulze

logger = logging.getLogger(__name__)


class BallotContainer(object):
    """
    A container for ballots.

    Includes convenience methods for loading/saving ballots, saving
    or restoring internal state during analysis, and returning the list
    of ballots in a few different formats.
    """
    def __init__(self, ballots=None):
        """
        Ballots should be a list of lists of (rank, candidate) tuples.
        """
        self.ballots = ballots or []
        self.excluded = set([])
        self.candidates = self.get_candidates()
        self.collapse_gaps = True
        self.states = []

    def copy_state(self):
        """Return a copy of the internal state, so we can restore later."""
        return (copy.deepcopy(self.ballots), copy.deepcopy(self.excluded))

    def restore_state(self, state):
        self.ballots = copy.deepcopy(state[0])
        self.excluded = copy.deepcopy(state[1])
        self.candidates = self.get_candidates()

    def push_state(self):
        self.states.append(self.copy_state())
        return self

    def pop_state(self):
        self.restore_state(self.states.pop(-1))
        return self

    def __enter__(self):
        return self.push_state()

    def __exit__(self, *args, **kwargs):
        return self.pop_state()

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
        if filename == '-':
            json.dump(unicode_ballots, sys.stdout, encoding='utf-8', indent=1)
        else:
            with open(filename, 'w') as fd:
                json.dump(unicode_ballots, fd, encoding='utf-8', indent=1)

    def get_candidates(self):
        candidates = {}
        for ballot in self.ballots:
            for rank, candidate in ballot:
                if candidate not in self.excluded:
                    candidates[candidate] = 1
        return candidates.keys()

    def exclude_candidates(self, excluded):
        self.excluded |= set(excluded)
        self.candidates = self.get_candidates()
        return self

    def ballots_as_lists(self):
        for ballot in self.ballots:
            as_list = [candidate for rank, candidate in sorted(ballot)
                       if candidate not in self.excluded]
            if as_list:
                yield(as_list)

    def ballots_as_rankings(self):
        b = self.ballots_as_lists() if (self.collapse_gaps) else self.ballots
        for ballot in b:
            rankings = {}
            ranked = enumerate(ballot) if (self.collapse_gaps) else ballot
            for rank, candidate in ranked:
                if candidate not in self.excluded:
                    rankings[candidate] = rank
            yield(rankings)

    def hashes_with_counts(self, ballots):
        hashes = {}
        for ballot in ballots:
            bkey = repr(ballot)
            if bkey in hashes:
                hashes[bkey]["count"] += 1
            else:
                hashes[bkey] = {"count": 1, "ballot": ballot}
        return hashes.values()


class BallotAnalyzer(BallotContainer):
    """
    This class will analyze and return statistics about a set of ballots.
    """
    def _cands_and_stats(self):
        cands = sorted(self.get_candidates())
        return (cands, {
            'candidates': cands,
            'ballots': len(self.ballots),
        })

    def get_ballot_stats(self):
        cands, stats = self._cands_and_stats()
        lengths = {}
        for ballot in self.ballots:
            l = len(ballot)
            lengths[l] = lengths.get(l, 0) + 1
        stats['ballot_lengths'] = lengths
        stats['ballot_length_average'] = float(sum(
            (k * v) for k, v in lengths.iteritems())) / len(self.ballots)
        stats['ballot_length_most_common'] = max(
            (v, k) for k, v in lengths.iteritems())[1]
        return stats

    def get_candidate_rank_stats(self):
        cands, stats = self._cands_and_stats()
        ranks = [[0 for r in cands] for c in cands]
        stats['ranking_matrix'] = ranks
        for ballot in self.ballots:
            for rank, candidate in ballot:
                if candidate in cands:
                    ranks[cands.index(candidate)][int(rank)] += 1
        for ranking in ranks:
            r = sum(ranking)
            ranking.append(r)
        return stats

    def get_candidate_pairwise_stats(self):
        cands, stats = self._cands_and_stats()
        cmatrix = [[0 for c2 in cands] for c1 in cands]
        stats['pairwise_matrix'] = cmatrix
        for ranking in self.ballots_as_rankings():
            for i, c1 in enumerate(cands):
                for j, c2 in enumerate(cands):
                    if ranking.get(c1, 9999999) < ranking.get(c2, 9999999):
                        cmatrix[i][j] += 1
        return stats

    def get_duplicate_ballots(self, threshold=None, threshold_pct=None):
        if threshold_pct:
            threshold = float(threshold_pct) * len(self.ballots) / 100
        elif not threshold:
            threshold = 2

        cands, stats = self._cands_and_stats()
        stats['duplicate_threshold'] = threshold
        stats['duplicates'] = []
        for cbhash in self.hashes_with_counts(self.ballots_as_lists()):
            if cbhash.get("count", 1) >= threshold:
                stats['duplicates'].append(cbhash)
        stats['duplicates'].sort(key=lambda cbh: -cbh["count"])
        return stats

    def stats_as_text(self, stats):
        lines = [
            '<!-- Generated %ss --><html><head><meta charset="UTF-8"></head><body><pre>' % (
                datetime.datetime.now()),
            '',
            'Analyzed %d ballots with %d candidates.' % (
                stats['ballots'], len(stats['candidates']))]

        if 'ballot_lengths' in stats:
            bls = min(stats['ballot_lengths'].keys())
            bll = max(stats['ballot_lengths'].keys())
            blmc = stats['ballot_length_most_common']
            lines += ['', 'Ballots:',
                '   - Shortest ballot length: %d (%d ballots=%d%%)' % (
                    bls,
                    stats['ballot_lengths'][bls],
                    stats['ballot_lengths'][bls] * 100 / stats['ballots']),
                '   - Average ballot length: %.2f' % (
                    stats['ballot_length_average'],),
                '   - Longest ballot length: %d (%d ballots=%d%%)' % (
                    bll,
                    stats['ballot_lengths'][bll],
                    stats['ballot_lengths'][bll] * 100 / stats['ballots']),
                '   - Most common ballot length: %d (%d ballots=%d%%)' % (
                    blmc,
                    stats['ballot_lengths'][blmc],
                    stats['ballot_lengths'][blmc] * 100 / stats['ballots']),
                '   - L/B: [%s]' % (' '.join(
                    '%d/%d' % (k, stats['ballot_lengths'][k])
                        for k in sorted(stats['ballot_lengths'].keys())))]

        if stats.get('duplicates'):
            lines += ['',
                'Frequent ballots: (>= %d occurrances, %d%%)' % (
                    stats['duplicate_threshold'],
                    (100 * stats['duplicate_threshold']) / stats['ballots'])]
            for dup in stats['duplicates']:
                lines += ['   - %(count)d times: %(ballot)s' % dup]

        if stats.get('ranking_matrix'):
            rm = stats['ranking_matrix']
            lines += ['',
                'Rankings:',
                ' %16.16s  %s ANY' % ('CANDIDATE', ' '.join(
                    '%3.3s' % (i+1) for i in range(0, len(rm[0])-1)))]
            rls = []
            for i, candidate in enumerate(stats['candidates']):
                rls += [' %16.16s  %s' % (candidate, ' '.join(
                    '%3.3s' % v for v in rm[i]))]
            rls.sort(key=lambda l: -int(l.strip().split()[-1]))
            lines.extend(rls)

        if stats.get('pairwise_matrix'):
            pm = stats['pairwise_matrix']
            lines += ['',
                'Pairwise victories:',
                ' %16.16s  %s' % ('WINNER', ' '.join(
                    '%3.3s' % c for c in stats['candidates']))]
            for i, candidate in enumerate(stats['candidates']):
                lines += [' %16.16s  %s' % (candidate, ' '.join(
                    '%3.3s' % v for v in pm[i]))]

        lines += ['', '%s</pre></body></html>' % (' ' * 60,)]
        return '\n'.join(lines)


class BallotCounter(BallotAnalyzer):
    """
    This class contains the results of an election, making it easy to
    tally up the results using a few different methods.
    """
    VOTING_SYSTEMS = (
        ('condorcet', 'Condorcet'),
        ('schulze', 'Schulze, Ordered list'),
        ('schulze_old', 'Schulze, Ordered list (old)'),
        ('schulze_new', 'Schulze, Ordered list (new)'),
        ('schulze_both', 'Schulze, Ordered list (both)'),
        ('stcom', 'Steering Committee Election'),
        ('stv1', 'STV, Single winner'),
        ('stv2', 'STV, Two winners'),
        ('stv3', 'STV, Three winners'),
        ('stv4', 'STV, Four winners'),
        ('stv5', 'STV, Five winners'),
        ('stv10', 'STV, Ten winners'),
        ('stonethor', 'STV partition with Schulze ranking')
    )

    def system_name(self, system):
        return [n for m, n in self.VOTING_SYSTEMS if m == system][0]

    def schulze_results_old(self):
        candidates = self.candidates
        preference = schulze.rank_votes(self.ballots, candidates)
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)
        ordered_candidates = schulze.get_ordered_voting_results(strongest_paths)
        return [cand for cand in ordered_candidates]

    def schulze_results_new(self, winners=None):
        if winners is None:
            if self.ballots:
                winners = max(len(b) for b in self.ballots)
            else:
                winners = 1
        return Schulze(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                winner_threshold=min(winners, len(self.candidates)),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()['order']

    def schulze_results_both(self, winners=None):
        """Wrapper to canary new schulze code, comparing with old"""
        if self.excluded:
            logger.warning('Schulze old cannot exclude, using new only.')
            return self.schulze_results_new(winners=winners)

        old_style = self.schulze_results_old()
        new_style = self.schulze_results_new(winners=winners)
        if old_style != new_style:
            logger.warning('Schulze old result does not match schulze new!')
        else:
            logger.info('Schulze old and new match, hooray.')
        return old_style

    def schulze_stv_results(self, winners=None):
        if winners is None:
            winners = 1
        return sorted(list(SchulzeSTV(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                required_winners=min(winners, len(self.candidates)),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()['winners']))

    def stv_results(self, winners=None):
        if winners is None:
            winners = 1
        return list(STV(
                list(self.hashes_with_counts(self.ballots_as_lists())),
                required_winners=winners
            ).as_dict()['winners'])

    def condorcet_results(self):
        result = Condorcet(
                list(self.hashes_with_counts(self.ballots_as_rankings())),
                ballot_notation=Schulze.BALLOT_NOTATION_RANKING,
            ).as_dict()
        if not result.get('tied_winners'):
            return [result['winner']]
        else:
            return []

    def stcom_results(self, winners=None):
        """Icelandic Pirate party steering committee elections.

        Returns 10 or 11 members; the first five are the steering committee,
        the next five are the deputies (both selected using STV).  The 11th
        is the condorcet winner, if there is one. Note that the 11th result
        will be a duplicate.
        """
        result = self.schulze_results_new(winners=10)
        stcom = result[:5]
        deputies = result[5:]
        condorcet = self.condorcet_results()
        return sorted(stcom) + sorted(deputies) + condorcet

    def stonethor_results(self, partition=None, winners=None):
        """Experimental combined STV and Schulze method.

        Partition the candidate group using STV and then rank each
        partition separately using Schulze. The default partition is
        one quarter of the candidate count.
        """
        top = self.stv_results(winners=min(
            partition or (len(self.candidates) / 4),
            len(self.candidates)))
        bottom = list(set(self.get_candidates()) - set(top))
        if top:
            with self:
                top = self.exclude_candidates(bottom).schulze_results_new()
        if bottom and len(top) < winners:
            with self:
                bottom = self.exclude_candidates(top).schulze_results_new()
        return (top + bottom)[:winners]

    def results(self, method, winners=None, sysarg=None):
        assert(method in [system for system, name in self.VOTING_SYSTEMS])

        if method == 'schulze':
            return self.schulze_results_new(winners=(winners or sysarg))

        elif method == 'schulze_old':
            return self.schulze_results_old()

        elif method == 'schulze_both':
            return self.schulze_results_both(winners=(winners or sysarg))

        elif method == 'condorcet':
            return self.condorcet_results()

        elif method == 'stcom':
            return self.stcom_results()

        elif method.startswith('stv'):
            return self.stv_results(winners=int(method[3:] or 1))

        elif method == 'stonethor':
            return self.stonethor_results(winners=winners, partition=sysarg)

        else:
            raise Exception('Invalid voting method: %s' % method)

    def constrained_results(self, method, winners=None, below=None):
        results = self.results(method, winners=winners)
        if not below:
            return results

        constrained = ['' for i in range(0, len(results) * 2)]
        for candidate in results:
            position = max(0, below.get(candidate, 1) - 1)
            for p in range(position, len(constrained)):
                if not constrained[p]:
                   constrained[p] = candidate
                   break

        return [c for c in constrained if c]


if __name__ == "__main__":
    import sys
    import argparse

    # Configure logging
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    ap = argparse.ArgumentParser()
    ap.add_argument('-e', '--exclude', action='append',
        help="Candidate(s) to exclude when counting")
    ap.add_argument('-b', '--below', action='append',
        help="seat,candidate pairs, to constrain final ordering")
    ap.add_argument('--keep-gaps', action='store_true',
        help="Preserve gaps if ballots are not sequential")
    ap.add_argument('operation',
        help="Operation to perform (count)")
    ap.add_argument('system',
        help="Counting system to use (schulze, stv5, ...)")
    ap.add_argument('filenames', nargs='+',
        help="Ballot files to read")
    args = ap.parse_args()

    system = args.system
    if ':' in system:
        system, sysarg = system.split(':')
        sysarg = int(sysarg)
    else:
        sysarg = None

    bc = BallotCounter()
    for fn in args.filenames:
        bc.load_ballots(fn)

    if args.exclude:
        bc.exclude_candidates(args.exclude)

    bc.collapse_gaps = False if (args.keep_gaps) else True

    below = {}
    for sc in args.below or []:
        seat, candidate = sc.split(',')
        seat = int(seat)
        below[candidate] = seat

    if args.operation == 'count':
        print('Voting system:\n\t%s (%s)' % (bc.system_name(system), system))
        print('')
        print('Loaded %d ballots from:\n\t%s' % (
            len(bc.ballots), '\n\t'.join(args.filenames)))
        print('')
        if below:
            print(('Results(C):\n\t%s' % ', '.join(bc.constrained_results(
                system, sysarg=sysarg, below=below))).encode('utf-8'))
        else:
            print(('Results:\n\t%s' % ', '.join(bc.results(
                system, sysarg=sysarg))).encode('utf-8'))
        print('')

    if args.operation in ('analyze', ):
        stats = {}
        for method in (m.strip() for m in system.split(',')):
            if method == 'rankings':
                stats.update(bc.get_candidate_rank_stats())

            elif method == 'pairs':
                stats.update(bc.get_candidate_pairwise_stats())

            elif method == 'duplicates':
                stats.update(bc.get_duplicate_ballots(threshold_pct=5))

            elif method == 'ballots':
                stats.update(bc.get_ballot_stats())

            else:
                raise ValueError('Unknown analysis: %s' % method)

        if args.operation == 'analyze':
            print(bc.stats_as_text(stats).encode('utf-8'))

else:
    # Suppress errors in case logging isn't configured elsewhere
    logger.addHandler(logging.NullHandler())
