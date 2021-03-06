"""
HikerValidator.py
Handles the mapping between user entered text and GPS coordinates for shelters.
:Author: Chris Campell
:Version: 9/8/2016
"""

import os
import json
from fuzzywuzzy import fuzz
from collections import OrderedDict
import numpy as np
import copy

class HikerValidator(object):
    """
    HikerValidator(object) -Wrapper for ShelterValidator, HostelValidator, and GeoValidator. Maps a hiker's entered
        locations to validated GPS coordinates in the appropriate data sets.
    :Author: Chris Campell
    :Version: 9/14/2016
    """
    # TODO: Declare data structure to hold statistics for each hiker

    """
    __init__ -Constructor for objects of type HikerValidator.
    :param validated_shelters: The AT_Shelters data set loaded into memory from json file.
    :param validated_hostels: The AT_Hostels data set loaded into memory from json file.
    :param validated_places: The AT_Places data set loaded into memory from json file.
    :param statistics: A boolean flag; if True then statistics regarding the geocoding success of hiker's journals
        will be recorded.
    """
    def __init__(self, validated_shelters, validated_hostels, validated_places, statistics=False):
        self.validated_shelters = validated_shelters
        self.validated_hostels = validated_hostels
        self.validated_places = validated_places
        self.storage_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/'))
        self.stats = statistics
        if statistics:
            self.geocode_stats = {}

    """
    validate_entry_locations -Takes a hiker journal entry and attempts to map the provided
        start_loc and dest to a validated shelter in the AT Shelters data set.
    :param unvalidated_start_loc: The user entered string for their starting location.
    :param unvalidated_dest: The user entered string for their destination location.
    :param comparison_threshold: The threshold by which a match is considered valid during fuzzy string comparison.
    :returns (comp_ratios_usl, comp_ratios_ud): The top three fuzzy string comparisons greater than the
            comparsion_threshold for both start_location and destination.
        :return comp_ratios_usl: The top three matching shelter strings for start_location as determined by
                fuzzy string comparison.
        :return comp_ratios_ud: The top three matching shelter strings for destination as determined by
                fuzzy string comparison.
    """
    def validate_entry_locations(self, unvalidated_start_loc, unvalidated_dest, comparison_threshold=90):
        # If the user didn't enter any text then there can be no geovalidation.
        if unvalidated_start_loc is None and unvalidated_dest is None:
            return (None, None)

        max_comp_ratio_usl = -1
        usl_assoc_sid = None
        max_comp_ratio_udl = -1
        udl_assoc_sid = None
        for shelter_id, shelter_data in self.validated_shelters.items():
            # Create a comparison ratio for the hiker's entered start_loc and the validated shelter's name.
            comparison_ratio_usl = fuzz.partial_ratio(unvalidated_start_loc, shelter_data['name'])
            # Create a comparison ratio for the hiker's entered destination and the validated shelter's name.
            comparison_ratio_udl = fuzz.partial_ratio(unvalidated_dest, shelter_data['name'])

            # Perform comparison threshold check:
            if comparison_ratio_usl >= comparison_threshold:
                if comparison_ratio_usl >= max_comp_ratio_usl:
                    max_comp_ratio_usl = comparison_ratio_usl
                    usl_assoc_sid = shelter_id

            # Perform comparison threshold check:
            if comparison_ratio_udl >= comparison_threshold:
                if comparison_ratio_udl >= max_comp_ratio_udl:
                    max_comp_ratio_udl = comparison_ratio_udl
                    udl_assoc_sid = shelter_id
        return (usl_assoc_sid, udl_assoc_sid)

    """
    validate_entry -Maps an unvalidated hiker's trail journal entry to a validated entry in one of the data sets.
    :param user_start_loc: The start location from the trail journal entry to be mapped to a GPS location.
    :param user_dest_loc: The destination location from the trail journal entry to be mapped to a GPS location.
    :returns (validated_entry, comp_ratios_start_loc, comp_ratios_dest_loc):
        :return validated_entry: The now mapped/validated user_start_location and user_destination_location; returns
            None for key 'start_loc' if not mappable, and None for key 'dest' if not mappable.
        :return comp_ratios_start_loc: The top three results and their associated comparision ratios from the geocoding
            fuzzy string comparision process for the user's starting location.
        :return comp_ratios_dest_loc: The top three results and their associated comparision ratios fromt he geocoding
            fuzzy string comparison process for the user's destination location.
    """
    def validate_entry(self, user_start_loc, user_dest_loc, comparison_threshold=90):
        validated_entry = {}
        # Get the three best results for geocoded solutions for both start_loc and destination.
        usl_assoc_sid, udl_assoc_sid = self.validate_entry_locations(
            unvalidated_start_loc=user_start_loc, unvalidated_dest=user_dest_loc, comparison_threshold=comparison_threshold)

        # Determine if geovalidation was successful for the start_location
        if usl_assoc_sid is not None and usl_assoc_sid != -1:
            validated_entry['start_loc'] = {
                'shelter_name': self.validated_shelters[usl_assoc_sid]['name'],
                'SID': usl_assoc_sid,
                'lat': self.validated_shelters[usl_assoc_sid]['lat'],
                'lon': self.validated_shelters[usl_assoc_sid]['lon'],
                'type': self.validated_shelters[usl_assoc_sid]['type']
            }
        else:
            # Geovalidation for the provided start_location was unsuccessful.
            validated_entry['start_loc'] = None

        # Determine if geovalidation was successful for the destination.
        if udl_assoc_sid is not None and udl_assoc_sid != -1:
            validated_entry['dest'] = {
                'shelter_name': self.validated_shelters[udl_assoc_sid]['name'],
                'SID': udl_assoc_sid,
                'lat': self.validated_shelters[udl_assoc_sid]['lat'],
                'lon': self.validated_shelters[udl_assoc_sid]['lon'],
                'type': self.validated_shelters[udl_assoc_sid]['type']
            }
        else:
            # Geovalidation for the provided dest_location was unsuccessful.
            validated_entry['dest'] = None
        return validated_entry

    """
    validate_shelters -Goes through the hiker's journal entries: geocoding each starting location and destination. If
        the self.stats flag was set to true during object instantiation then record geocoding statistics.
    :param hiker: The deserialized hiker object read from the json file.
    """
    def validate_shelters(self, hiker):
        failed_mappings_start_loc = {}
        failed_mappings_dest_loc = {}
        unvalidated_journal = hiker['journal']
        validated_journal = {}

        for entry_num, entry in unvalidated_journal.items():
            validated_entry = self.validate_entry(
                user_start_loc=entry['start_loc'], user_dest_loc=entry['dest'], comparison_threshold=90)

            validated_journal[entry_num] = copy.deepcopy(entry)
            if validated_entry['start_loc'] is None:
                # The user entered start_location could not be mapped.
                # TODO: Record any other information that may be pertinent to analyzing Fuzzy string comparison.
                failed_mappings_start_loc[entry_num] = {
                    'start_loc': entry['start_loc']
                }
                validated_journal[entry_num]['start_loc'] = None
            else:
                # The user entered start_location was mapped.
                validated_journal[entry_num]['start_loc'] = validated_entry['start_loc']

            if validated_entry['dest'] is None:
                # The user entered destination location could not be mapped.
                # TODO: Record any other information that may be pertinent to analyzing Fuzzy string comparison.
                failed_mappings_dest_loc[entry_num] = {
                    'dest': entry['dest']
                }
                validated_journal[entry_num]['dest'] = None
            else:
                # The user entered destination location was mapped.
                validated_journal[entry_num]['dest'] = validated_entry['dest']

        if self.stats:
            # TODO: Compute additional hiker statistics.
            geocode_stats = {
                'hiker_id': hiker['identifier'],
                'USLS': failed_mappings_start_loc,
                'UDLS': failed_mappings_dest_loc,
                'num_unvalidated': len(failed_mappings_start_loc) + len(failed_mappings_dest_loc),
                'num_validated': len(validated_journal),
            }
        else:
            geocode_stats = None
        return (validated_journal, geocode_stats)

    """
    write_validated_hiker -Writes a geocoded hiker to the specified storage directory in json format.
    :param hiker -The deserialized hiker object read from the json file and mapped.
    """
    def write_validated_hiker(self, hiker):
        validated_hikers_data_path = self.storage_location + "/HikerData/ValidatedHikers/"
        # validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/HikerData/ValidatedHikers"
        hiker_id = hiker['identifier']
        with open(validated_hikers_data_path + str(hiker_id) + ".json", 'w') as fp:
            json.dump(hiker, fp=fp)

"""
get_validated_shelters -Returns a dictionary of the shelters validated using the combined TNL and ATC data sets.
@param validated_shelters_path -The path to the CSV file containing the validated shelters.
@return validated_shelters -A dictionary containing the geocoded shelters.
"""
def get_validated_shelters(validated_shelters_path):
    validated_shelters = {}
    line_num = 0
    with open(validated_shelters_path, 'r') as fp:
        for line in iter(fp):
            if not line_num == 0:
                split_string = str.split(line, sep=",")
                shelter_id = split_string[0]
                shelter_name = split_string[1]
                data_set = split_string[2]
                lat = float(split_string[3])
                lon = float(split_string[4])
                type = split_string[5]
                validated_shelters[shelter_id] = {
                    'name': shelter_name, 'dataset': data_set,
                    'type': type, 'lat': lat, 'lon': lon
                }
            line_num += 1
    return validated_shelters

"""
"""
def get_validated_hostels(validated_hostels_path):
    pass

"""
"""
def get_validated_places(validated_places_path):
    pass

def compute_geocoding_stats(validated_journals, geocoding_statistics):
    statistics = {
        'num_valid_sl': 0,
        'num_unvalid_usl': 0,
        'frequency_usl': {},
        'num_valid_udl': 0,
        'num_unvalid_udl': 0,
        'frequency_udl': {}
    }

    for hiker_id, journal in validated_journals.items():
        for entry_num,entry in journal.items():
            if entry['start_loc'] is not None:
                statistics['num_valid_sl'] += 1
            if entry['dest'] is not None:
                statistics['num_valid_udl'] += 1
    if geocoding_statistics is not None:
        for hiker_id,geo_stats in geocoding_statistics.items():
            if geo_stats['UDLS']:
                for entry_num,USL in geo_stats['USLS'].items():
                    if USL['start_loc'] not in statistics['frequency_usl']:
                        statistics['frequency_usl'][USL['start_loc']] = 0
                    else:
                        statistics['frequency_usl'][USL['start_loc']] += 1
                statistics['num_unvalid_usl'] += len(geo_stats['USLS'])
            if geo_stats['UDLS']:
                for entry_num,UDL in geo_stats['UDLS'].items():
                    if UDL['dest'] not in statistics['frequency_udl']:
                        statistics['frequency_udl'][UDL['dest']] = 0
                    else:
                        statistics['frequency_udl'][UDL['dest']] += 1
                statistics['num_unvalid_udl'] += len(geo_stats['UDLS'])
            else:
                pass
    return statistics

"""
main -Main method for hiker validation. Goes through every unvalidated hiker and maps their location to an entry in the
    AT Shelters database.
"""
def main(stats=False, num_hikers_to_map=None):
    unvalidated_hikers_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/UnvalidatedHikers/'))
    validated_hikers_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/ValidatedHikers/'))
    validated_shelter_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    # validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/HikerData/ValidatedHikers/"
    # validated_shelter_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/TrailShelters/"
    geocoding_stats = {}
    validated_journals = {}
    num_hikers = 0

    # Go through the list of unvalidated hikers and validate.
    for filename in os.listdir(unvalidated_hikers_data_path):
        if num_hikers_to_map:
            if num_hikers > num_hikers_to_map:
                break
        # If the hiker has already been validated, don't re-validate.
        if filename not in os.listdir(validated_hikers_data_path):
            # Load the unvalidated json file into memory.
            with open(unvalidated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
            # Load the validated AT shelters into memory:
            validated_shelters = get_validated_shelters(validated_shelters_path=validated_shelter_data_path + "/newShelters.csv")
            # TODO: Load validated hostels into memory:
            # validated_hostels = get_validated_hostels(validated_hostels_path=validated_shelter_data_path + "/validated_hostels.csv")
            # TODO: Load validated places (that are not recognized shelters or hostels) into memory:
            # validated_places = get_validated_places(validated_places_path=validated_shelter_data_path + "/validated_places.csv")

            # TODO: Validate using hostels, shelters, and places; not just shelters.
            # Instantiate validator object.
            validator = HikerValidator(validated_shelters=validated_shelters,
                                       validated_hostels=None, validated_places=None, statistics=stats)
            # Execute shelter validation.
            validated_journal, geovalidation_stats = validator.validate_shelters(hiker)
            # If the statistics flag was set to true during instantiation, retrieve the computed statistics:
            if stats:
                geocoding_stats[hiker['identifier']] = geovalidation_stats
            # If there are any successfully mapped journal entries, write them to validated hikers.
            if len(validated_journal) > 0:
                validated_journals[hiker['identifier']] = validated_journal
                validator.write_validated_hiker(hiker)
            num_hikers += 1
        else:
            print("Hiker %s Has Already been Validated." % filename)

    # If geocoding statistics are requested then perform analysis
    if stats:
        statistics = compute_geocoding_stats(validated_journals, geocoding_stats)

if __name__ == '__main__':
    main(stats=True,num_hikers_to_map=3)
