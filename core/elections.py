#TODO Can we remove this file? Seems like ancient garbage
from openstv.ballots import Ballots
from openstv.plugins import getMethodPlugins


class RankedElection:
    def __init__(self):
        pass

    def load_ballot(self, ballot):
        try:
            dirtyBallots = Ballots()
            dirtyBallots.loadKnown(bltFn, exclude0=False)
            cleanBallots = dirtyBallots.getCleanBallots()
        except RuntimeError, msg:
            print msg

    def load_ballot_file(self, filename):
        pass

    def set_election_type(self, electiontype):
        pass

    def get_election_types(self):
        return getMethodPlugins("byName").keys()

    def get_election_classes(self):
        return getMethodPlugins("byName")

    def set_num_seats(self):
        pass

    def get_num_seats(self):
        pass

    def get_result(self):
        pass


if __name__ == "__main__":
    print "RANKEDELECTIONMADNESS!"
    r = RankedElection()
