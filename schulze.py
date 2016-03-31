"""
Schulze STV voting implementation.
See https://en.wikipedia.org/wiki/Schulze_method
"""

from collections import defaultdict, OrderedDict
import random


def compute_strongest_paths(preference, candidates):
    """
    input: preference
        p[i,j] = number of voters that prefer candidate i to candidate j
    input: candidates
        ['candidate_1_id', 'candidate_2_1_id', ...]
    output:
        strongest_paths[i,j] = bottleneck number in the strongest path between i and j
    """
    strongest_paths = defaultdict(lambda: defaultdict(int))
    
    # Calculate the strongest paths between candidates
    for i in candidates:
        for j in candidates:
            if i != j:
                if preference[i][j] > preference[j][i]:
                    strongest_paths[i][j] = preference[i][j]
                else:
                    strongest_paths[i][j] = 0

    for i in candidates:
        for j in candidates:
            if i != j:
                for k in candidates:
                    if i != k and j != k:
                        #p[j,k] := max ( p[j,k], min ( p[j,i], p[i,k] ) )
                        strongest_paths[j][k] = max(strongest_paths[j][k], min(strongest_paths[j][i], strongest_paths[i][k]))

    return strongest_paths


def get_ordered_voting_results(strongest_paths):
    """
     strongest_paths: the strongest paths of each candidate.
     returns:
        ordered dictionary, ordered by how many wins a candidate had against other candidates
        key is candidate, value is list of candidates defeated by that candidate.
     """

    # We need to determine the ordering among the candidates by comparing their respective path strengths.
    # For all candidates, compare their path strengths in both directions, the candidate that has stronger path
    # wins the other candidate. Order them from the candidate that wins all others, to the one that wins none.
    wins = defaultdict(list)
    for ci in strongest_paths.iterkeys():
        for cj in strongest_paths.iterkeys():

            if ci == cj:
                continue

            if strongest_paths[ci][cj] > strongest_paths[cj][ci]:
                wins[ci].append(cj)

    # Create ordered results of candidates that actually won other candidates
    ordered_results = sorted(wins.items(), key=lambda x: len(x[1]), reverse=True)

    # Add any candidates that did not win anything in a random order
    stragglers = [c for c in strongest_paths.keys() if c not in wins]
    random.shuffle(stragglers)
    for straggler in stragglers:
        ordered_results.append((straggler, None))

    return OrderedDict(ordered_results)


def rank_votes(votes, candidates):
    """
    input: votes is a list of preference ordered votes
        vote = [(1,'a'), (2, 'b'), (2, 'd'), (2, 'x'), (100, 'y')]
    input: candidates is a list of candidate voting keys:
    candidates = ['a,' 'b,' 'c,' 'd,' 'x,' 'y']

    Note that candidate 'c' is not listed in the example vote. This means no vote for 'c'.

    output: A dictionary of preference counts for each candidate.
    preference = {
                    'a': {'a': 0, 'b': 1, 'c': 1, 'd,' 1, 'x,' 1, 'y': 1}, #place ahead of everyone
                    'b': {'b': 0, 'a': 0, 'c': 1, 'd,' 1, 'x,' 1, 'y': 1}, #not placed ahead of a, equal to d and x
                    'c': {'c': 0, 'b': 0, 'a': 0, 'd,' 0, 'x,' 0, 'y': 0}, #not placed ahead of anyone
                    'd': {'d': 0, 'b': 1, 'c': 1, 'a,' 0, 'x,' 1, 'y': 1}, #equal to b and x, ahead of y
                    'x': {'x': 0, 'b': 1, 'c': 1, 'd,' 1, 'a,' 0, 'y': 1}, #equal to b and d, ahead of y
                    'y': {'y': 0, 'b': 0, 'c': 1, 'd,' 0, 'x,' 0, 'a': 0}, #c got no vote
                    #'self' is always 0
                }
    """
    invalid_votes = list()
    #prepare the output - 0 set all candidates
    preference = defaultdict(lambda: defaultdict(int))

    for vote in votes:
        # make sure the votes are in order
        vote.sort()
        voted_candidates = set([x[1] for x in vote])

        # check for duplicate choices
        if len(voted_candidates) != len(vote):
            # duplicate choice, invalid!
            invalid_votes.append(vote)

        else:
            for i, choice in enumerate(vote):
                # resolve ties: [(1, 'a'), (2, 'c'), (2, 'e'), (3, 'b'), (5, 'd')] 'e' also gets a 'c' increment
                tied_candidates = [x[1] for x in vote if choice[0] == x[0]]
                not_voted_candidates = set(candidates)-voted_candidates
                # increment against all other candidates
                candidate = vote[i][1]

                opponents_to_increment = list(
                    set([x[1] for x in vote[i+1:]] + list(not_voted_candidates) + tied_candidates))

                increment_candidate(candidate, opponents_to_increment, preference)

    return preference


def increment_candidate(candidate, opponents, preference_dict):
    for opponent in opponents:
        if opponent in preference_dict[candidate]:
            preference_dict[candidate][opponent] += 1
        else:
            preference_dict[candidate][opponent] = 1

