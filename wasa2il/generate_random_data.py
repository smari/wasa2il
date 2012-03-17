#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from wasa2il.core.models import Polity, Topic, Issue, VoteOption, Vote, Delegate, BaseIssue

from collections import defaultdict
from random import choice, random

COMMON_NAMES = """
	Akhrif
	Alami
	Alaoui
	Benjelloun
	Bennani
	Benziane
	Chbihi
	Cherkaoui
	Debbagh
	El Fassi
	Idrissi
	Kettani
	Ouazzani
	Skalli
	Souidi
	Tazi
	""".split()

NO_USERS = 20
NO_POLITIES = 5
NO_TOPICS = 4
NO_ISSUES = 5
DELEGATION_LIKELYHOOD = 0.5
VOTE_LIKELYHOOD = 0.9
POLITY_LIKELYHOOD = 0.5

def main():
	
	# Create random test users
	name_counter = defaultdict(lambda:0)
	User.objects.filter(last_name='Generated').delete()
	for i in range(NO_USERS):
		name = choice(COMMON_NAMES)
		counter = name_counter.get(name) or ''
		firstname = ('%s %s' % (name, counter)).strip()
		username = ('%s-%s' % (name, counter)).strip('-')
		u = User()
		u.username = username
		u.first_name = firstname
		u.last_name = 'Generated'
		u.save()
		name_counter[name] += 1
	users = User.objects.all()#.filter(last_name='Generated')
	
	
	# Set up voting options
	VoteOption.objects.all().delete()
	vo_y = VoteOption.objects.create(name='Yes', slug='yes')
	vo_n = VoteOption.objects.create(name='No', slug='no')
	vo_m = VoteOption.objects.create(name='Maybe', slug='maybe')
	vo_cr = VoteOption.objects.create(name='Red', slug='Red')
	vo_cg = VoteOption.objects.create(name='Green', slug='Green')
	vo_cb = VoteOption.objects.create(name='Blue', slug='Blue')
	options = VoteOption.objects.all()
	options_yesno = [vo_y, vo_n]
	options_yesnomaybe = [vo_y, vo_n, vo_m]
	options_colors = [vo_cr, vo_cg, vo_cb]
	options_classes = [options_yesno, options_yesnomaybe, options_colors]
	
	# Generate some polities
	Polity.objects.all().delete()
	p_m = Polity.objects.create(name="Morocco", slug="morocco")
	p_rr = Polity.objects.create(name="Rabat-Salé-Zemmour-Zaer ", slug="rabat-sale-zemmour-zaer", parent=p_m)
	p_r = Polity.objects.create(name="Rabat", slug="rabat", parent=p_rr)
	p_s = Polity.objects.create(name="Salé", slug="sale", parent=p_rr)
	# Add some random poilities.. all belong to Morocco for now..
	for i in range(4, 4+NO_POLITIES):
		Polity.objects.create(name='Polity %d'%i, slug='polity-%d'%i, parent=p_m)
	polities = Polity.objects.all()
	
	# Give each user atleast one polity
	for user in users:
		choice(polities).members.add(user)
		# Add more polities.. perhaps
		while True:
		    if random() > POLITY_LIKELYHOOD: break
		    choice(polities).members.add(user)

	
	
	# Generate random topics
	Topic.objects.all().delete()
	polities = list(Polity.objects.all())
	for i in range(NO_TOPICS):
		t = Topic.objects.create(name='Topic %d' % i, slug='topic-%d' % i, polity=choice(polities))
	
	# Generate random issues
	Issue.objects.all().delete()
	topics = list(Topic.objects.all())
	for i in range(NO_ISSUES):
		t = Issue.objects.create(name='Issue %d' % i, slug='issue-%d' % i)
		# Just set a single topic.. for now atleast
		t.topics.add(choice(topics))
	
	
	# Collect the base issues
	base_issues = BaseIssue.objects.all()
	
	
	# Generate some delegations
	Delegate.objects.all().delete()
	for user in users:
		if random() > DELEGATION_LIKELYHOOD:
			continue
		while True:
			delegate = choice(users)
			if delegate != user: break
		Delegate.objects.create(user=user, delegate=delegate, base_issue=choice(base_issues))
	
	# Finally, generate some votes!
	Vote.objects.all().delete()
	for issue in Issue.objects.all():
		options = choice(options_classes)
		for user in users:
			if random() > VOTE_LIKELYHOOD:
				continue
			Vote.objects.create(user=user, issue=issue, option=choice(options))		

if __name__=='__main__':
	main()
