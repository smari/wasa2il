import core.schulze
import random


def test_6_candidates_45_votes():
    # Candidate 'x' is someone no-one voted for but was eligible.
    # Otherwise, this test reflects the example on https://en.wikipedia.org/wiki/Schulze_method
    candidates = ['a', 'b', 'c', 'd', 'e', 'x']
    votes = [
        [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
        [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
        [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
        [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')],
        [(1, 'a'), (2, 'c'), (3, 'b'), (4, 'e'), (5, 'd')], #5
        [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
        [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
        [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
        [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')],
        [(1, 'a'), (2, 'd'), (3, 'e'), (4, 'c'), (5, 'b')], #5
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')],
        [(1, 'b'), (2, 'e'), (3, 'd'), (4, 'a'), (5, 'c')], #8
        [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')], #20
        [(1, 'c'), (2, 'a'), (3, 'b'), (4, 'e'), (5, 'd')], #3
        [(1, 'c'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'e')],
        [(1, 'c'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'e')], #2
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')],
        [(1, 'd'), (2, 'c'), (3, 'e'), (4, 'b'), (5, 'a')], #30
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')],
        [(1, 'c'), (2, 'a'), (3, 'e'), (4, 'b'), (5, 'd')], #7
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')], #40
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')],
        [(1, 'e'), (2, 'b'), (3, 'a'), (4, 'd'), (5, 'c')] #8
    ]

    # Randomize the votes
    random.shuffle(votes)

    # Create directed graph
    preference = schulze.rank_votes(votes, candidates)

    # Get the strongest paths of each candidate
    strongest_paths = schulze.compute_strongest_paths(preference, candidates)

    # Get final, ordered, results
    results = schulze.get_ordered_voting_results(strongest_paths)

    assert ", ".join(results.keys()) == "e, a, c, b, d, x"

    return results


def test_3_candidates_3_votes_cyclical():

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
    assert len(results) == 3

    # All path strengths should be equal, this is a tied vote!
    for sp in strongest_paths.itervalues():
        assert sum(sp.values()) == 4
