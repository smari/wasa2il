#!/usr/bin/env python

from wasa2il.core.models import Issue, Vote, Delegate
from collections import defaultdict


def flatten(lst):
	return [item for sublist in lst for item in sublist]

def main():

	for issue in Issue.objects.all():
		print '\n\n============='
		print 'Issue:', issue, '(topics:', issue.topics_str(), ')'
		# Get relevant topics and polities
		topics = list(issue.topics.all())
		polities = [topic.polity for topic in topics]
	
		# Create the base_issue list delegates must be bound
		base_issues = [derived_issue.baseissue_ptr for derived_issue in [issue] + topics + polities]
		
		if 0:
			print 'Issue:',
			print '', issue
			print 'Topics:'
			for topic in topics:
				print '', topic
			print 'Polities:'
			for polity in polities:
				print '', polity
			print '\nBase issues:'
			for base_issue in base_issues:
				print '', base_issue
	
	
		# Get the "weight" behind the vote
		def get_weight(votee):
			return 1 + sum(get_weight(delegate.user) for delegate in Delegate.objects.filter(delegate=votee, base_issue__in=base_issues))
	
		# Aggregate the votes
		options = defaultdict(lambda: 0)
		for vote in Vote.objects.filter(issue=issue):
			weight = get_weight(vote.user)
			options[vote.option.name] += weight
	
		print '\nVote results:'
		for option, votes in options.iteritems():
			print '  %s: %d' % (option, votes)
		
	print '\n'

if __name__=='__main__':
	main()
