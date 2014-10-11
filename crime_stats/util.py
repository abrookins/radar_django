"""
Utility functions.
"""
import pickle
import dateutil.parser


def get_crime_sums(crimes):
    """Calculate sums of crimes by type for crimes in ``crimes``."""
    summary = {
        'by_type': {},
        'types_by_hour': {hour: {} for hour in range(0, 24)},
        'types_by_day': {day: {} for day in range(0, 7)}
    }

    for crime in crimes:
        crime_type = crime['properties']['crimeType']
        report_time = dateutil.parser.parse(crime['properties']['reportTime'])
        day = report_time.weekday()
        hour = report_time.hour

        if crime_type in summary['by_type']:
            summary['by_type'][crime_type] += 1
        else:
            summary['by_type'][crime_type] = 1

        if crime_type in summary['types_by_day'][day]:
            summary['types_by_day'][day][crime_type] += 1
        else:
            summary['types_by_day'][day][crime_type] = 1

        if crime_type in summary['types_by_hour']:
            summary['types_by_hour'][hour][crime_type] += 1
        else:
            summary['types_by_hour'][hour][crime_type] = 1

    return summary


def percentage_difference(x, y):
    """Calculate the percentage difference between ``x`` and ``y``."""
    difference = (x - y / ((x + y) / 2)) * 100
    if x > y:
        difference = -difference
    return difference


def write_pickled_file(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def load_pickled_file(path):
    with open(path, 'rb') as f:
        return pickle.load(f)
