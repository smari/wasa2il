from django import template

from election.models import ElectionVote

register = template.Library()


@register.filter(name='electionvoted')
def electionvoted(election, user):
    ut = 0
    try:
        ut = ElectionVote.objects.filter(user=user, election=election).count()
    except TypeError:
        pass

    return (ut > 0)


@register.filter
def sparkline(variable, skip_last=False):
    if not variable:
        return ''
    if isinstance(variable, dict):
        pairs = sorted([(k, v) for k, v in variable.iteritems()])
        sparkline = [0] * (pairs[-1][0] + 1)
        for i, v in pairs:
            sparkline[i] = v
        if 0 not in variable and '0' not in variable:
            variable = sparkline[1:]
        else:
            variable = sparkline
    if skip_last:
        variable = variable[:-1]
    return ','.join(str(v) for v in variable)
