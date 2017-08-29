from django.test import TestCase
from election import schulze
import random


class SchulzeTest(TestCase):
    def test_6_candidates_45_votes(self):
        # Candidate 'x' is someone no-one voted for but was eligible.
        # Otherwise, this test reflects the example on
        # https://en.wikipedia.org/wiki/Schulze_method
        candidates = ['a', 'b', 'c', 'd', 'e', 'x']
        votes = [
            [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
            [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
            [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
            [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
            [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],  # 5
            [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
            [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
            [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
            [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
            [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],  # 5
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
            [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],  # 8
            [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')],  # 20
            [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')],  # 3
            [(1, 'c'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'e')],
            [(1, 'c'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'e')],  # 2
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
            [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],  # 30
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
            [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],  # 7
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],  # 40
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
            [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')]  # 8
        ]

        # Randomize the votes
        random.shuffle(votes)

        # Create directed graph
        preference = schulze.rank_votes(votes, candidates)

        # Get the strongest paths of each candidate
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)

        # Get final, ordered, results
        results = schulze.get_ordered_voting_results(strongest_paths)

        self.assertEqual(", ".join(results.keys()), "e, a, c, b, d, x")

    def test_3_candidates_3_votes_cyclical(self):

        candidates = ['x', 'y', 'z']
        votes = [
            [(1, 'x'), (2, 'y'), (3, 'z')],
            [(1, 'y'), (2, 'z'), (3, 'x')],
            [(1, 'z'), (2, 'x'), (3, 'y')]
        ]

        # Randomize the votes
        random.shuffle(votes)

        # Create directed graph
        preference = schulze.rank_votes(votes, candidates)

        # Get the strongest paths of each candidate
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)

        # Get final, ordered, results
        results = schulze.get_ordered_voting_results(strongest_paths)

        # We should only get 3 results, even if this is cyclical tied vote.
        self.assertEqual(len(results), 3)

        # All path strengths should be equal, this is a tied vote!
        for sp in strongest_paths.itervalues():
            self.assertEqual(sum(sp.values()), 4)


class SchulzeStatisticalTest(TestCase):
    def generate_vote(self, candidate_chances):
        """
        returns a list of vote choices, votes are picked based on each candidate's chances of being voted for.
        [(1, 'candidate_id'), (2, 'candidate_id'), (2, 'candidate_id'), ...]
        Votes are generated by determining how many candidates a voter wants to pick.
        At least one pass is made through the candidate_chance list (possibly picking more candidates than chosen but never
        more than are available)
        for each candidate, it is randomly determined if they will be picked that round. Every candidate picked in
        each round will have the same rank number.

        For example; candidate chances are:
        [(0.3103760707038792, 1), (0.3368433989455909, 0), (0.40308497270067967, 4), (0.6070980766930767, 2), (0.7710239099894114, 3)]
        Voter is determined to pick 3 candidates.
        In the first round each candidate is checked
        0.3103760707038792 rolls 0.1 and is picked at rank 1 (first round) - 2 remaining picks
        0.3368433989455909 rolls 0.9 and is not picked
        0.40308497270067967 rolls 0.3 and is picked at rank 1 - 1 remaining pick
        0.6070980766930767 rolls a 0.5 and is picked at rank 1 - 0 remaining picks but not all candidates have been checked
        0.7710239099894114 rolls a 0.6 and is picked at rank 1
        Vote returned is [(1, 1), (1, 4), (1, 2), (1,3)]
        """
        # vote for at least 1
        nr_to_vote_for = random.randint(1, len(candidate_chances))
        votes = []

        rank = 1
        while nr_to_vote_for > 0:
            for c in candidate_chances:
                if random.random() < c[0]:
                    votes.append((rank, c[1]))
                    nr_to_vote_for -= 1
                if rank > 1 and nr_to_vote_for == 0:
                    break
            rank += 1
        return votes

    def test_statistical(self, nr_candidates=10, nr_voters=1000):
        """
        Runs a statistical test of Shulze with nr_candidates and nr_voters.
        Each voter generates a set of choices (a vote) based on the chances of each candidate's
        randomly determined chance of winning.
        """
        candidates = list(range(nr_candidates))
        candidate_chances = [(random.random() / 2, c) for c in candidates]
        candidate_chances.sort()
        candidate_chances.reverse()

        voters = list(range(nr_voters))
        votes = [self.generate_vote(candidate_chances) for _ in voters]

        # Create directed graph
        preference = schulze.rank_votes(votes, candidates)

        # Get the strongest paths of each candidate
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)

        # Get final, ordered, results
        results = schulze.get_ordered_voting_results(strongest_paths)

        # Assert every candidate is within 1 seats of expected statistical outcome
        for place, candidate in enumerate(candidate_chances):
            expected_place = candidate_chances.index(candidate)
            self.assertIn(
                place,
                (expected_place, expected_place + 1, expected_place - 1)
            )

            print("candidate %s had %s%% chance of winning" % (
                candidate[1], candidate[0]))
            others = (0 if results[candidate[1]] is None
                                else len(results[candidate[1]]))
            print("candidate was ranked above %s other candidates" % (others))

"""
Example results from 50 candidates and 300,000 voters:
statistical_test(50, 300000)

candidate 26 had 0.483200948654 % chance of winning.
candidate was ranked above 49 other candidates
candidate 39 had 0.464021295542 % chance of winning.
candidate was ranked above 48 other candidates
candidate 15 had 0.431485774128 % chance of winning.
candidate was ranked above 47 other candidates
candidate 25 had 0.420753903532 % chance of winning.
candidate was ranked above 46 other candidates
candidate 42 had 0.419197158316 % chance of winning.
candidate was ranked above 44 other candidates
candidate 35 had 0.418901105954 % chance of winning.
candidate was ranked above 45 other candidates
candidate 13 had 0.401065556152 % chance of winning.
candidate was ranked above 43 other candidates
candidate 41 had 0.384035455262 % chance of winning.
candidate was ranked above 42 other candidates
candidate 7 had 0.380049427563 % chance of winning.
candidate was ranked above 41 other candidates
candidate 0 had 0.377967795101 % chance of winning.
candidate was ranked above 40 other candidates
candidate 34 had 0.371907686176 % chance of winning.
candidate was ranked above 39 other candidates
candidate 1 had 0.357778586501 % chance of winning.
candidate was ranked above 38 other candidates
candidate 14 had 0.34852486036 % chance of winning.
candidate was ranked above 37 other candidates
candidate 5 had 0.330212621555 % chance of winning.
candidate was ranked above 35 other candidates
candidate 37 had 0.3287223589 % chance of winning.
candidate was ranked above 36 other candidates
candidate 11 had 0.327884416543 % chance of winning.
candidate was ranked above 34 other candidates
candidate 29 had 0.325254931929 % chance of winning.
candidate was ranked above 33 other candidates
candidate 10 had 0.321070570805 % chance of winning.
candidate was ranked above 32 other candidates
candidate 31 had 0.31596922035 % chance of winning.
candidate was ranked above 31 other candidates
candidate 33 had 0.297191015742 % chance of winning.
candidate was ranked above 30 other candidates
candidate 17 had 0.287581522868 % chance of winning.
candidate was ranked above 29 other candidates
candidate 16 had 0.274060664402 % chance of winning.
candidate was ranked above 28 other candidates
candidate 44 had 0.258455488971 % chance of winning.
candidate was ranked above 27 other candidates
candidate 22 had 0.24412891209 % chance of winning.
candidate was ranked above 26 other candidates
candidate 8 had 0.237682466202 % chance of winning.
candidate was ranked above 25 other candidates
candidate 46 had 0.221566298556 % chance of winning.
candidate was ranked above 24 other candidates
candidate 30 had 0.219717021731 % chance of winning.
candidate was ranked above 22 other candidates
candidate 38 had 0.219333290245 % chance of winning.
candidate was ranked above 23 other candidates
candidate 4 had 0.216652418888 % chance of winning.
candidate was ranked above 21 other candidates
candidate 2 had 0.208006878111 % chance of winning.
candidate was ranked above 20 other candidates
candidate 19 had 0.171597247883 % chance of winning.
candidate was ranked above 19 other candidates
candidate 49 had 0.157472077345 % chance of winning.
candidate was ranked above 18 other candidates
candidate 28 had 0.149149256926 % chance of winning.
candidate was ranked above 17 other candidates
candidate 36 had 0.146031626084 % chance of winning.
candidate was ranked above 15 other candidates
candidate 3 had 0.143387827992 % chance of winning.
candidate was ranked above 16 other candidates
candidate 47 had 0.13546630016 % chance of winning.
candidate was ranked above 14 other candidates
candidate 45 had 0.124017754194 % chance of winning.
candidate was ranked above 13 other candidates
candidate 21 had 0.112630055751 % chance of winning.
candidate was ranked above 12 other candidates
candidate 18 had 0.102281073478 % chance of winning.
candidate was ranked above 11 other candidates
candidate 23 had 0.093419412524 % chance of winning.
candidate was ranked above 10 other candidates
candidate 20 had 0.0918015096321 % chance of winning.
candidate was ranked above 9 other candidates
candidate 12 had 0.0603144521346 % chance of winning.
candidate was ranked above 8 other candidates
candidate 48 had 0.0584980606429 % chance of winning.
candidate was ranked above 7 other candidates
candidate 6 had 0.0567705554887 % chance of winning.
candidate was ranked above 6 other candidates
candidate 27 had 0.0542038315661 % chance of winning.
candidate was ranked above 4 other candidates
candidate 43 had 0.0540082976788 % chance of winning.
candidate was ranked above 5 other candidates
candidate 40 had 0.0487528996791 % chance of winning.
candidate was ranked above 3 other candidates
candidate 32 had 0.0428817696832 % chance of winning.
candidate was ranked above 2 other candidates
candidate 24 had 0.0235691852838 % chance of winning.
candidate was ranked above 1 other candidates
candidate 9 had 0.0073776195401 % chance of winning.
candidate was ranked above 0 other candidates
[Finished in 37.9s]
"""
