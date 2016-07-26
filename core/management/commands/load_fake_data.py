# -*- coding: utf-8 -*-
#
# This comment will create fake polities, users, issues and elections to
# facilitate testing.
#
import random
import traceback
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.http import HttpRequest

from core.models import *
import core.ajax.document as doc_ajax
import core.ajax.issue as issue_ajax
import core.views


ADJECTIVES = ('Sad', 'Happy', 'Good', 'Evil', 'Liberal', 'Dadaist', 'Hungry')
THINGS = ('Chicken', 'Human', 'Automobile', 'Fish', 'Puppy', 'Kitten',
          'Infant', 'Lobster', 'Nature')
ACTIONS = ('Farming', 'Justice', 'Education', 'Welfare', 'Entertainment')
ACTACTS = ('Stop', 'Improve', 'Defuzz', 'Budget', 'Plan', 'Restrict',
           'Disarm', 'Avoid', 'Protest', 'Support')


def req(method, user, data, **kwargs):
    hr = HttpRequest()
    hr.REQUEST = data
    hr.method = 'GET' if (not data) else 'POST'
    hr.user = user
    return method(hr, **kwargs)


class Command(BaseCommand):

    def add_arguments(self, parser):
        for flag in ('users', 'topics', 'documents', 'elections',
                     'reset', 'full'):
            parser.add_argument('--%s' % flag, action='store_true', dest=flag)

    def handle(self, *args, **options):
        now = datetime.now()

        if not options.get('full'):
            print
            print 'NOTE: Creating small test data set, use --full for MOAR DATA.'
            print

        reset = False
        if options.get('reset'):
            yn = raw_input('Are you sure you want to delete precious data? [y/N] ')
            if yn.strip().lower() == 'y':
                reset = True
            else:
                return

        create_all = not (options.get('users', False) or
                          options.get('topics', False) or
                          options.get('elections', False) or
                          options.get('documents', False))

        userlist = [
            ('a', 'a@example.com', 'Alpha'),
            ('b', 'b@example.com', 'Beta'),
            ('c', 'c@example.com', 'Foo'),
            ('d', 'd@example.com', 'Baz')]
        userlist += [
            ('user%s' % i, 'user%s@example.com' % i, 'User %s' % i)
                for i in range(0, 1110)]
        if options.get('users') or create_all:
            if not options.get('full'):
                userlist = userlist[:20]
            print 'Generating %d users ...' % len(userlist)
            users = {}
            if reset:
                User.objects.all().delete()
            for u, email, name in userlist:
                try:
                    if len(u) == 1:
                        users[u] = User.objects.create_user(u, password=u)
                        print '   * Creating user "%s" with password "%s"' % (u, u)
                    else:
                        users[u] = User.objects.create_user(u)
                    users[u].email = email
                    users[u].save()
                    UserProfile(
                        user=users[u],
                        joined_org=now - timedelta(hours=random.randint(0, 24 * 5))
                        ).save()
                except IntegrityError:
                    # User already exists
                    users[u] = User.objects.get(email=email)

        print 'Generating/updating 4 polities of varying sizes ...'
        pollist = [
            ('d', 'The Big Polity',    'abc',  1000),
            ('c', 'The Medium Polity', 'abc',  100),
            ('b', 'The Small Polity',  'ab',   10),
            ('a', 'The Dinky Polity',  'a',    1)]
        if not options.get('full'):
            pollist = pollist[2:]
        topiclist = []
        for t1 in ADJECTIVES:
            for t2 in THINGS:
                for t3 in ACTIONS:
                    topiclist.append('%s %s %s' % (t1, t2, t3))
        polities = {}
        documents = {}
        for u, name, members, size in pollist:
            print '   + %s (size=%d)' % (name, size)
            usr = User.objects.get(username=u)
            try:
                p = Polity.objects.get(name=name)
                new = False
            except:
                p = Polity(name=name,
                           slug=name.lower().replace(' ', '-'),
                           description='A polity with about %d things' % size)
                p.created = now - timedelta(hours=random.randint(0, 24 * 5))
                p.created_by = usr
                p.modified_by = usr
                p.save()
                PolityRuleset(
                    polity=p,
                    name='Silly rules',
                    issue_quora=5,
                    issue_quora_percent=10,
                    issue_majority=50,
                    issue_discussion_time=24*3600,
                    issue_proposal_time=24*3600,
                    issue_vote_time=24*3600).save()
                new = True
            polities[u] = (p, size)

            if new or options.get('topics') or create_all:
                n = 1 + min(size//5, len(topiclist))
                print '       - Creating %d topics' % n
                if reset:
                    Topic.objects.filter(polity=p).delete()
                for topic in random.sample(topiclist, n):
                    Topic(name=topic,
                          polity=p,
                          created_by=usr).save()

            if new or options.get('users') or create_all:
                print '       - Adding ~%d users' % size
                for m in set([m for m in members] +
                             random.sample(users.keys(), size)):
                    try:
                        # User d is a member of no polities
                        if m != 'd':
                            p.members.add(users[m])
                    except:
                        pass

            if options.get('elections') or create_all:
                # Create 3 elections per polity:
                #    one soliciting candidates, one voting, one finished
                print '       - Creating 3 elections'
                if reset:
                    Election.objects.filter(polity=p).delete()
                for dc, dv in ((1, 2), (-1, 1), (-2, -1)):
                    e = Election(
                        name="%s Manager" % random.choice(THINGS),
                        polity=p,
                        voting_system='schulze',
                        deadline_candidacy=now + timedelta(days=dc),
                        deadline_votes=now + timedelta(days=dv),
                        deadline_joined_org=now + timedelta(days=dv))
                    e.save()

                    if (dc < 0) or (dv < 0):
                        candidatec = min(p.members.count(), 15)
                        voterc = 0
                    else:
                        candidatec = min(p.members.count(), 5)
                        voterc = min(p.members.count(), 5)

                    candidates = []
                    for cand in random.sample(p.members.all(), candidatec):
                        c = Candidate(election=e, user=cand)
                        c.save()
                        candidates.append(c)
                    for voter in random.sample(p.members.all(), voterc):
                        random.shuffle(candidates)
                        for rank, cand in enumerate(candidates):
                             ElectionVote(
                                 election=e,
                                 user=voter,
                                 candidate=cand,
                                 value=rank).save()

                    if (dv < 0) and voterc and candidatec:
                        try:
                            e.process()
                        except:
                            traceback.print_exc()
                            print 'Votes cast on %s: %s' % (e, ElectionVote.objects.filter(election=e).count())

            if new or options.get('documents') or create_all:
                # We create a list of authors biased towards the first
                # users created, so some users will have lots of documents
                # and others will have less.
                ul = [username for username, e, n in userlist]
                aw = [(m.username, max(20 - ul.index(m.username), 1))
                      for m in p.members.all()]
                authors = [a for a, w in aw for i in range(0, w)]

                # Get a list of topics...
                topics = Topic.objects.filter(polity=p)

                print '       - Creating %d documents' % size
                if reset:
                    Document.objects.filter(polity=p).delete()
                for docn in range(0, size):
                    topic = random.choice(topics)
                    subject = '%s %s with %s' % (random.choice(ACTACTS),
                                                 topic.name,
                                                 random.choice(THINGS) + 's')
                    author = User.objects.get(username=random.choice(authors))
                    doc = Document(
                        name=subject,
                        user=author,
                        polity=p)
                    doc.save()
                    doc.created = now - timedelta(hours=random.randint(0, 24 * 3))
                    doc.save()

                    documents[doc.id] = (topic, doc)
                    text = subject
                    for version in range(0, random.randint(1, 3)):
                        text = '%s\n%s' % (text, text)
                        docc = DocumentContent(document=doc, user=author, text=text)
                        docc.status = 'proposed'
                        docc.order = version
                        docc.save()

        if options.get('documents') or create_all:
            # Put max(3, 10%) of all the documents up for election
            howmany = min(max(3, len(documents) // 10), len(documents))
            print 'Creating issues for %d documents.' % howmany
            for dk in random.sample(documents.keys(), howmany):
                topic, doc = documents[dk]
                i = Issue(
                    name=doc.name,
                    polity=doc.polity,
                    created_by=doc.user,
                    ruleset=PolityRuleset.objects.filter(polity=doc.polity)[0],
                    majority_percentage=50,
                    documentcontent=doc.preferred_version())
                i.save()
                i.created = doc.created
                i.apply_ruleset(now=doc.created)
                i.save()
                i.topics.add(topic)
