import json
import os
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import CASCADE
from django.utils.translation import ugettext_lazy as _

from election.utils import BallotCounter


class ElectionQuerySet(models.QuerySet):
    def recent(self):
        return self.filter(deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ELECTION_DAYS))

class Election(models.Model):
    """
    An election is different from an issue vote; it's a vote
    on people. Users, specifically.
    """
    objects = ElectionQuerySet.as_manager()

    # Note: Not used for model field options (at least not yet), but rather
    # the get_election_state_display function below.
    ELECTION_STATES = (
        ('concluded', _('Concluded')),
        ('voting', _('Voting')),
        ('waiting', _('Waiting')),
        ('accepting_candidates', _('Accepting candidates')),
    )

    VOTING_SYSTEMS = BallotCounter.VOTING_SYSTEMS

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    polity = models.ForeignKey('polity.Polity', on_delete=CASCADE)
    voting_system = models.CharField(max_length=30, verbose_name=_('Voting system'), choices=VOTING_SYSTEMS)

    # Tells whether the election results page should show the winning
    # candidates as an ordered list or as a set of winners. Some voting
    # systems (most notably STV) do not typically give an ordered list where
    # one candidate is higher or lower than another one. It would be more
    # elegant to set this in a model describing the voting system in more
    # detail. To achieve that, the BallotCounter.VOTING_SYSTEMS list above
    # should to be turned into a proper Django model.
    results_are_ordered = models.BooleanField(default=True, verbose_name=_('Results are ordered'))

    # How many candidates will be publicly listed in the results of an
    # election. Officers still see entire list. Individual candidates can also
    # see where they ended up in the results.
    results_limit = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('How many candidates will be publicly listed in the results of an election')
    )

    deadline_candidacy = models.DateTimeField(verbose_name=_('Deadline for candidacies'))
    starttime_votes = models.DateTimeField(null=True, blank=True, verbose_name=_('Election begins'))
    deadline_votes = models.DateTimeField(verbose_name=_('Election ends'))

    # This allows one polity to host elections for one or more others, in
    # particular allowing access to elections based on geographical polities
    # without residency granting access to participate in all other polity
    # activities.
    voting_polities = models.ManyToManyField('polity.Polity', blank=True, related_name='remote_election_votes', verbose_name=_('Voting polities'))
    candidate_polities = models.ManyToManyField('polity.Polity', blank=True, related_name='remote_election_candidates', verbose_name=_('Candidate polities'))

    # Sometimes elections may depend on a user having been the organization's member for an X amount of time
    # This optional field lets the vote counter disregard members who are too new.
    deadline_joined_org = models.DateTimeField(null=True, blank=True, verbose_name=_('Membership deadline'))
    is_processed = models.BooleanField(default=False)

    instructions = models.TextField(null=True, blank=True, verbose_name=_('Instructions'))

    # These are election statistics;
    stats = models.TextField(null=True, blank=True, verbose_name=_('Statistics as JSON'))
    stats_publish_ballots_basic = models.BooleanField(default=False, verbose_name=_('Publish basic ballot statistics'))
    stats_publish_ballots_per_candidate = models.BooleanField(default=False, verbose_name=_('Publish ballot statistics for each candidate'))
    stats_publish_files = models.BooleanField(default=False, verbose_name=_('Publish advanced statistics (downloadable)'))

    class Meta:
        ordering = ['-deadline_votes']

    # An election can only be processed once, since votes are deleted during the process
    class AlreadyProcessedException(Exception):
        def __init__(self, message):
            super(Election.AlreadyProcessedException, self).__init__(message)

    class ElectionInProgressException(Exception):
        def __init__(self, message):
            super(Election.ElectionInProgressException, self).__init__(message)

    def save_ballots(self, ballot_counter):
        if settings.BALLOT_SAVEFILE_FORMAT is not None:
            try:
                filename = settings.BALLOT_SAVEFILE_FORMAT % {
                    'election_id': self.id,
                    'voting_system': self.voting_system}
                directory = os.path.dirname(filename)
                if not os.path.exists(directory):
                    os.mkdir(directory)
                ballot_counter.save_ballots(filename)
            except:
                import traceback
                traceback.print_exc()
                return False
        return True

    def load_archived_ballots(self):
        bc = BallotCounter()
        if settings.BALLOT_SAVEFILE_FORMAT is not None:
            try:
                filename = settings.BALLOT_SAVEFILE_FORMAT % {
                    'election_id': self.id,
                    'voting_system': self.voting_system}
                bc.load_ballots(filename)
            except:
                import traceback
                traceback.print_exc()
        return bc

    @transaction.atomic
    def process(self):
        if self.election_state() != 'concluded':
            raise Election.ElectionInProgressException('Election %s is still in progress!' % self)

        if self.is_processed:
            raise Election.AlreadyProcessedException('Election %s has already been processed!' % self)

        # "Flatten" the values of votes in an election. A candidate may be
        # removed from an election when voting has already started. When that
        # happens, ballots with that candidate may have a gap in their values,
        # for example [0, 1, 2, 4] , because the person with value 3 was
        # removed from the election. Here the ballot is "flattened" so that
        # gaps are eliminated and the values are made sequential, i.e.
        # [0, 1, 2, 3] and not [0, 1, 2, 4].
        votes = self.electionvote_set.order_by('user_id', 'value')
        last_user_id = 0
        for vote in votes:
            # Reset correct value every time we start processing a new user.
            if last_user_id != vote.user_id:
                correct_value = 0

            if vote.value != correct_value:
                vote.value = correct_value
                vote.save()

            correct_value += 1
            last_user_id = vote.user_id

        if self.candidate_set.count() == 0:
            # If there are no candidates, there's no need to calculate
            # anything. We're pretty confident in these being the results.
            ordered_candidates = []
            vote_count = 0
            save_failed = False

        else:
            ordered_candidates, ballot_counter = self.process_votes()
            vote_count = self.electionvote_set.values('user').distinct().count()

            # Save anonymized ballots to a file, so we can recount later
            save_failed = not self.save_ballots(ballot_counter)

            # Generate stats before deleting everything. This allows us to
            # analyze the voters as well as the ballots.
            self.generate_stats()

        try:
            election_result = ElectionResult.objects.get(election=self)
        except ElectionResult.DoesNotExist:
            election_result = ElectionResult.objects.create(election=self, vote_count=vote_count)

        election_result.rows.all().delete()
        order = 0
        for candidate in ordered_candidates:
            order = order + 1
            election_result_row = ElectionResultRow()
            election_result_row.election_result = election_result
            election_result_row.candidate = candidate
            election_result_row.order = order
            election_result_row.save()

        # Delete the original votes (for anonymity), we have the ballots elsewhere
        if not save_failed:
            self.electionvote_set.all().delete()

        self.is_processed = True
        self.save()

        if self.polity.push_on_election_end:
            # Doing this just to force the translation string creation:
            __ = _("Election results in election '%s' have been calculated.")
            push_send_notification_to_polity_users(self.polity.id, "Election results in election '%s' have been calculated.", [self.name])

    def generate_stats(self):
        ballot_counter = self.load_archived_ballots()
        if ballot_counter.ballots:
            stats = {}
            stats.update(ballot_counter.get_candidate_rank_stats())
            stats.update(ballot_counter.get_candidate_pairwise_stats())
            stats.update(ballot_counter.get_ballot_stats())
            self.stats = json.dumps(stats)
            return True
        else:
            return False

    def get_voters(self):
        if self.voting_polities.count() > 0:
            voters = User.objects.filter(polities__in=self.voting_polities.all())
        else:
            voters = self.polity.election_voters()

        if self.deadline_joined_org:
            return voters.filter(userprofile__joined_org__lt = self.deadline_joined_org)
        else:
            return voters

    def can_vote(self, user=None, user_id=None):
        return self.get_voters().filter(
            id=(user_id if (user_id is not None) else user.id)).exists()

    def get_potential_candidates(self):
        if self.candidate_polities.count() > 0:
            pcands = User.objects.filter(polities__in=self.candidate_polities.all())
        else:
            pcands = self.polity.election_potential_candidates()

        # NOTE: We ignore the deadline here, it's only meant to prevent
        #       manipulation of votes not prevent people from running for
        #       office or otherwise participating in things.

        return pcands

    def can_be_candidate(self, user=None, user_id=None):
        return self.get_potential_candidates().filter(
            id=(user_id if (user_id is not None) else user.id)).exists()

    def process_votes(self):
        if self.deadline_joined_org:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self, user__userprofile__joined_org__lt = self.deadline_joined_org)
        else:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self)

        votemap = {}
        for vote in votes:
            if not vote.user_id in votemap:
                votemap[vote.user_id] = []
            votemap[vote.user_id].append(vote)

        ballots = []
        for user_id in votemap:
            ballot = [(int(v.value), v.candidate) for v in votemap[user_id]]
            ballots.append(ballot)

        ballot_counter = BallotCounter(ballots)
        return ballot_counter.results(self.voting_system), ballot_counter

    def get_ordered_candidates_from_votes(self):
        return self.process_votes()[0]

    def __str__(self):
        return u'%s' % self.name

    def voting_start_time(self):
        if self.starttime_votes not in (None, ""):
            return max(self.starttime_votes, self.deadline_candidacy)
        return self.deadline_candidacy

    def election_state(self):
        # Short-hands.
        now = datetime.now()
        deadline_candidacy = self.deadline_candidacy
        deadline_votes = self.deadline_votes
        voting_start_time = self.voting_start_time()

        if deadline_votes < now:
            return 'concluded'
        elif voting_start_time < now:
            return 'voting'
        elif voting_start_time > now and deadline_candidacy < now:
            return 'waiting'
        elif deadline_candidacy > now:
            return 'accepting_candidates'
        else:
            # Should never happen.
            return 'unknown'

    def get_election_state_display(self):
        return dict(self.ELECTION_STATES)[self.election_state()].__str__()

    def get_stats(self, user=None, load_users=True, rename_users=False):
        """Load stats from the DB and convert to pythonic format.

        We expect stats to change over time, so the function provides
        reasonable defaults for everything we care about even if the
        JSON turns out to be incomplete. Changes to our stats logic will
        not require a schema change, but stats cannot readily be queried.
        Pros and cons...
        """
        stats = {
            'ranking_matrix': [],
            'pairwise_matrix': [],
            'candidates': [],
            'ballot_lengths': {},
            'ballots': 0,
            'ballot_length_average': 0,
            'ballot_length_most_common': 0}

        # Parse the stats JSON, if it exists.
        try:
            stats.update(json.loads(self.stats))
        except:
            pass

        # Convert ballot_lengths keys (back) to ints
        new_ballot_lengths = {}
        for k in stats['ballot_lengths'].keys():
            new_ballot_lengths[int(k)] = stats['ballot_lengths'][k]
        stats['ballot_lengths'] = new_ballot_lengths
        del new_ballot_lengths

        # Censor the statistics, if we only want to publish details about
        # the top N candidates.
        if self.results_limit:
            excluded = set([])
            if not user or not user.is_staff:
                excluded |= set(cand.user.username for cand in
                                self.get_winners()[self.results_limit:])
            if user and user.username in excluded:
                excluded.remove(user.username)
            stats = BallotCounter.exclude_candidate_stats(stats, excluded)

        # Convert usernames to users. Let's hope usernames never change!
        for i, c in enumerate(stats['candidates']):
            try:
                if not c:
                    pass
                elif load_users:
                    stats['candidates'][i] = User.objects.get(username=c)
                elif rename_users:
                    u = User.objects.get(username=c)
                    stats['candidates'][i] = '%s (%s)' % (u.get_name(), c)
            except:
                pass

        # Create more accessible representations of the tables
        stats['rankings'] = {}
        stats['victories'] = {}
        for i, c in enumerate(stats['candidates']):
            if stats.get('ranking_matrix'):
                stats['rankings'][c] = stats['ranking_matrix'][i]
            if stats.get('pairwise_matrix'):
                stats['victories'][c] = stats['pairwise_matrix'][i]

        return stats

    def get_formatted_stats(self, fmt, user=None):
        stats = self.get_stats(user=user, rename_users=True, load_users=False)
        if fmt == 'json':
            return json.dumps(stats, indent=1)
        elif fmt in ('text', 'html'):
            return BallotCounter.stats_as_text(stats)
        elif fmt in ('xlsx', 'ods'):
            return BallotCounter.stats_as_spreadsheet(fmt, stats)
        else:
            return None

    def get_winners(self):
        return [r.candidate for r in self.result.rows.select_related('candidate__user__userprofile').order_by('order')]

    def get_candidates(self):
        ctx = {}
        ctx["count"] = self.candidate_set.count()
        ctx["users"] = [{"username": x.user.username} for x in self.candidate_set.all()]
        return ctx

    def get_unchosen_candidates(self, user):
        if not user.is_authenticated or self.election_state() != 'voting':
            return Candidate.objects.filter(election=self)
        # votes = []
        votes = ElectionVote.objects.filter(election=self, user=user)
        votedcands = [x.candidate.id for x in votes]
        if len(votedcands) != 0:
            candidates = Candidate.objects.filter(election=self).exclude(id__in=votedcands).order_by('?')
        else:
            candidates = Candidate.objects.filter(election=self).order_by('?')

        return candidates

    def get_vote_count(self):
        if self.is_processed:
            return self.result.vote_count
        else:
            return self.electionvote_set.values("user").distinct().count()

    def has_voted(self, user, **constraints):
        if user.is_anonymous:
            return False
        return ElectionVote.objects.filter(
            election=self, user=user, **constraints).exists()

    def get_vote(self, user):
        votes = []
        if not user.is_anonymous:
            votes = ElectionVote.objects.filter(election=self, user=user).order_by("value")
        return [x.candidate for x in votes]

    def get_ballots(self):
        ballot_box = []
        for voter in self.electionvote_set.values("user").distinct():
            user = User.objects.get(pk=voter["user"])
            ballot = []
            for vote in user.electionvote_set.filter(election=self).order_by('value'):
                ballot.append(vote.candidate.user.username)
            ballot_box.append(ballot)
        random.shuffle(ballot_box)
        return ballot_box


class Candidate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    election = models.ForeignKey(Election, on_delete=CASCADE)

    def __lt__(self, other):
        # Make it possible to sort Candidates
        return str(self) < str(other)

    def __str__(self):
        return u'%s' % self.user.username


class ElectionVote(models.Model):
    election = models.ForeignKey(Election, on_delete=CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=CASCADE)
    value = models.IntegerField()

    class Meta:
        unique_together = (('election', 'user', 'candidate'),
                    ('election', 'user', 'value'))

    def __str__(self):
        return u'User %s has voted in election %s' % (self.user, self.election)


class ElectionResult(models.Model):
    election = models.OneToOneField('Election', related_name='result', on_delete=CASCADE)
    vote_count = models.IntegerField()


class ElectionResultRow(models.Model):
    election_result = models.ForeignKey('ElectionResult', related_name='rows', on_delete=CASCADE)
    candidate = models.OneToOneField('Candidate', related_name='result_row', on_delete=CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
