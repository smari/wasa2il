from datetime import datetime

from dateutil.relativedelta import relativedelta

def ssn_is_formatted_correctly(ssn):
    # We don't need any hard-core checksumming here, since we're only making
    # sure that the data format is correct, so that we can safely retrieve
    # parts of it through string manipulation.
    return ssn.isdigit() and len(ssn) == 10

def calculate_age_from_ssn(ssn):
    if not ssn_is_formatted_correctly(ssn):
        raise AttributeError('SSN must be numeric and exactly 10 digits long')

    # Determine year.
    century_num = ssn[9:]
    if century_num == '9':
        century = 1900
    elif century_num == '0':
        century = 2000
    else:
        raise AttributeError('%s is not a known number for any century' % century_num)
    year = century + int(ssn[4:6])

    # Determine month and day
    month = int(ssn[2:4])
    day = int(ssn[0:2])

    # Calculate the differences between birthdate and today.
    birthdate = datetime(year, month, day)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    age = relativedelta(today, birthdate).years

    return age

def is_ssn_human_or_institution(ssn):
    if not ssn_is_formatted_correctly(ssn):
        raise AttributeError('SSN must be numeric and exactly 10 digits long')

    return 'institution' if int(ssn[0:2]) > 31 else 'human'
