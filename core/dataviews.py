from core.ajax.utils import jsonize
from django.urls import reverse
from election.models import Election
from issue.models import Issue

@jsonize
def recent_activity(request):

    # Names prefixed with "q_" to distinguish them as queries. We will be
    # returning the same data in JSON format, which we will call "issues" and
    # "elections".
    q_issues = Issue.objects.select_related('polity').recent().order_by('polity__id', '-deadline_votes')
    q_elections = Election.objects.prefetch_related(
        'electionvote_set',
        'candidate_set'
    ).select_related(
        'result'
    ).recent()

    issues = []
    for q_issue in q_issues:
        issues.append({
            # Web location for further info on the issue.
            'url': request.build_absolute_uri(
                reverse('issue', args=(q_issue.polity_id, q_issue.id))
            ),

            # The polity to which this issue belongs.
            'polity': q_issue.polity.name,

            # A unique identifier for formal reference. Example: 6/2019
            'log_number': '%d/%d' % (q_issue.issue_num, q_issue.issue_year),

            # The issue's name or title.
            'name': q_issue.name,

            # Options are: concluded/voting/accepting_proposals/discussion
            # Note that the state does not give the *result*, i.e. whether the
            # proposal was accepted or rejected, but rather where the issue is
            # currently in the decision-making process. Therefore "concluded"
            # only means that the issue has concluded, but does not tell us
            # *how* it concluded.
            'state': q_issue.issue_state(),

            # Translated, human-readable version of the issue state.
            'state_human_readable': q_issue.get_issue_state_display(),

            # A boolean indicating whether the issue has been approved or not.
            'majority_reached': q_issue.majority_reached(),

            # Translated, human-readable version of the result.
            'majority_reached_human_readable': q_issue.get_majority_reached_display(),

            # When the issue's fate is not determined by vote from within
            # Wasa2il, for example when a vote is made outside of Wasa2il but
            # still placed here for reference or historical reasons, or when
            # an issue is retracted without ever coming to a vote.
            #
            # Consider displaying only this value if it is non-null, and the
            # `majority_reached` value only if this is null.
            'special_process': q_issue.special_process,

            # Translated, human-readable version of the result.
            'special_process_human_readable': q_issue.get_special_process_display(),

            # Comment count.
            'comment_count': q_issue.comment_count,

            # Vote count.
            'vote_count': q_issue.votecount,
        })

    elections = []
    for q_election in q_elections:
        # See comments for issue above, which are more detailed but are mostly
        # applicable to this section as well.
        elections.append({
            'url': request.build_absolute_uri(reverse('election', args=(q_election.polity_id, q_election.id))),
            'polity': q_issue.polity.name,
            'name': q_election.name,
            'state': q_election.election_state(),
            'state_human_readable': q_election.get_election_state_display(),
            'candidate_count': q_election.candidate_set.count(),
            'vote_count': q_election.get_vote_count(),
        })

    return {
        'elections': elections,
        'issues': issues,
    }
