#!/usr/bin/env python

from wasa2il.core.models import Issue, Vote, Delegate
from collections import defaultdict

def main():
	
	# Get a issue
	issue = Issue.objects.all()[0]
	
	# Aggregate the votes
	options = defaultdict(lambda: 0)
	for vote in Vote.objects.filter(issue=issue):
		# Get the "weight" behind the vote
		def get_weight(votee):
			return 1 + sum(get_weight(delegate.user) for delegate in Delegate.objects.filter(delegate=votee))
		weight = get_weight(vote.user)
		options[vote.option.name] += weight
	
	print '\nVote results:'
	for option, votes in options.iteritems():
		print '  %s: %d' % (option, votes)
		


if __name__=='__main__':
	main()
