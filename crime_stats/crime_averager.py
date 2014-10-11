"""
Code to generate Portland crime averages for a given year.
"""
import os
import statistics

from . import util


class CachingCrimeAverager(object):
    """Calculates the median average for crime types.

    Caches the averages in a pickle file at ``averages_path`` and crime sums
    in ``summaries_path``.
    """
    def __init__(self, crimes, root_dir, year, averages_path=None, summaries_path=None):
        self.crimes = crimes
        self.root_dir = root_dir
        self.year = year
        self._averages = None

        if not averages_path:
            averages_path = os.path.join(root_dir, 'crime_averages_{}'.format(year))
        self.averages_path = averages_path

        if not summaries_path:
            summaries_path = os.path.join(self.root_dir, 'crime_summaries_{}'.format(year))
        self.summaries_path = summaries_path

    def get_cell_sums(self):
        """Returns summaries of all crime activity.

        If the summaries file doesn't exist, calculates summary data for all crimes in the ES
        store and pickles a dict containing this data to self.summaries_path.
        """
        try:
            cell_summaries = util.load_pickled_file(self.summaries_path)
        except OSError:
            cells = self.crimes.get_cells()
            cell_summaries = self.crimes.sum_crimes_in_cells(cells, self.year)
            util.write_pickled_file(cell_summaries, self.summaries_path)
        return cell_summaries

    def calculate_averages_for_cells(self, cell_sums):
        """Calculate the median average of crimes by type for all geohash cells that we know about."""
        sums_by_type = {}
        averages = {}

        for sums in cell_sums:
            by_type = sums['by_type']

            for crime_type, crime_type_sum in by_type.items():
                if crime_type in sums_by_type:
                    sums_by_type[crime_type].append(crime_type_sum)
                else:
                    sums_by_type[crime_type] = [crime_type_sum]

        for crime_type, crime_sums in sums_by_type.items():
            averages[crime_type] = statistics.median(crime_sums)

        return averages

    @property
    def averages(self):
        """Return a dict containing data on crime averages per geohash cell.

        Attempts to load the data from ``path``. If that file does not exist,
        the data will be calculated for year ``year``.
        """
        if self._averages:
            return self._averages
        try:
            averages = util.load_pickled_file(self.averages_path)
        except OSError:
            cell_sums = self.get_cell_sums()
            averages = self.calculate_averages_for_cells(cell_sums)
        self._averages = averages
        return averages
