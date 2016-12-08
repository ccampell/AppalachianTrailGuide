"""
DepartureStatistics.py
TODO: Class descriptor.
:author: Chris Campell
:version: 11/23/2016
"""
__author__ = "Chris Campell"
__version__ = "11/23/2016"

import os
import json
from collections import OrderedDict
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def get_validated_hikers(validated_hikers_path):
    """
    get_validated_hikers -Reads all validated hikers in the specified directory into memory. Returns an
        OrderedDictionary of validated_hikers sorted by hiker identifier.
    :param validated_hikers_path: The file path to the CSV file containing the validated hikers.
    :return sorted_validated_hikers: A dictionary containing the sorted validated hikers.
    """
    validated_hikers = {}
    for filename in os.listdir(validated_hikers_path):
        with open(validated_hikers_path + "/" + filename, 'r') as fp:
            hiker = json.load(fp=fp)
            validated_hikers[int(filename.strip(".json"))] = hiker
    # Sort the validated_hikers by hiker id:
    sorted_validated_hikers = OrderedDict(sorted(validated_hikers.items()))
    for hid, hiker in sorted_validated_hikers.items():
        sorted_hiker_journal = OrderedDict()
        for enum, entry in hiker['journal'].items():
            sorted_hiker_journal[int(enum)] = entry
        sorted_validated_hikers[hid]['journal'] = OrderedDict(sorted(sorted_hiker_journal.items()))
    # Sort the hiker's trail journals by entry number (chronologically....kinda):
    print("Read %d hikers from %s." % (len(sorted_validated_hikers), validated_hikers_path))
    return sorted_validated_hikers

def get_validated_thru_hikers(validated_hikers):
    """
    get_validated_thru_hikers - Returns the hiker objects with over 2,000 miles logged.
    :param validated_hikers: The dictionary of hikers with successfully mapped start locations.
    :return thru_hikers: A list of hikers who's total mileage was >= 2,000.
    """
    thru_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
        for enum, entry in hiker_info['journal'].items():
            if entry['trip_mileage'] >= 2000:
                thru_hikers[hid] = hiker_info
    return thru_hikers

def get_southbound_hikers(validated_hikers):
    """
    get_southbound_hikers - Returns the hiker objects whose primary direction of travel is southbound.
    :param validated_hikers: The list of validated hikers read into memory by get_validated_hikers.
    :return southbound_hikers: The list of southbound hikers.
    """
    southbound_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
        # If a direction was recorded from the website, we don't want it. Its not accurate.
        hiker_info['dir'] = None
        num_northbound_start_loc = 0
        num_southbound_start_loc = 0
        for enum, entry in hiker_info['journal'].items():
            if entry['start_loc']['dir'] == 'N':
                num_northbound_start_loc += 1
            elif entry['start_loc']['dir'] == 'S':
                num_southbound_start_loc += 1
        # Classify the hiker as northbound or southbound hiker based on the majority direction traveled:
        if num_northbound_start_loc > num_southbound_start_loc:
           validated_hikers[hid]['dir'] = "N"
        elif num_northbound_start_loc < num_southbound_start_loc:
            validated_hikers[hid]['dir'] = "S"
            southbound_hikers[hid] = hiker_info
    return southbound_hikers

def get_northbound_hikers(validated_hikers):
    """
    get_northbound_hikers - Returns the hiker objects whose primary direction of travel is northbound.
    :param validated_hikers: The list of validated hikers read into memory by get_validated_hikers.
    :return northbound_hikers: The list of northbound hikers.
    """
    northbound_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
        # If a direction was recorded from the website, we don't want it. Its not accurate.
        hiker_info['dir'] = None
        num_northbound_start_loc = 0
        num_southbound_start_loc = 0
        for enum, entry in hiker_info['journal'].items():
            if entry['start_loc']['dir'] == 'N':
                num_northbound_start_loc += 1
            elif entry['start_loc']['dir'] == 'S':
                num_southbound_start_loc += 1
        # Classify the hiker as northbound or southbound hiker based on the majority direction traveled:
        if num_northbound_start_loc > num_southbound_start_loc:
           validated_hikers[hid]['dir'] = "N"
           northbound_hikers[hid] = hiker_info
        elif num_northbound_start_loc < num_southbound_start_loc:
            validated_hikers[hid]['dir'] = "S"
    return northbound_hikers

def display_month_departure_stats(month_departure_stats):
    N  = len(month_departure_stats)
    monthly_departure_stats = [value for value in month_departure_stats.values()]
    # x locations for the groups:
    ind = np.arange(N)
    # width of the bars:
    width = 0.5
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, monthly_departure_stats, width, color='g')
    ax.set_xlabel('Month of the Year')
    ax.set_ylabel('Number of Hikers')
    ax.set_title('Month Thru Hikers Depart')
    ax.set_xticks(ind + width)
    plt.xlabel('Jan    Feb    Mar    Apr    May    Jun    July    Aug    Sep    Oct    Nov    Dec')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'monthly_departure_stats.png'))
    plt.savefig(storage_loc)

def display_southbound_month_departure_stats(southbound_month_departure_stats):
    N = len(southbound_month_departure_stats)
    monthly_departure_stats = [value for value in southbound_month_departure_stats.values()]
    # x locations for the groups:
    ind = np.arange(N)
    # width of the bars:
    width = 0.5
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, monthly_departure_stats, width, color='r')
    ax.set_xlabel('Month of the Year')
    ax.set_ylabel('Number of Hikers')
    ax.set_title('Month Southbound Thru Hikers Depart')
    ax.set_xticks(ind + width)
    plt.xlabel('Jan    Feb    Mar    Apr    May    Jun    July    Aug    Sep    Oct    Nov    Dec')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'southbound_monthly_departure_stats.png'))
    plt.savefig(storage_loc)

def display_northbound_month_departure_stats(northbound_month_departure_stats):
    N  = len(northbound_month_departure_stats)
    monthly_departure_stats = [value for value in northbound_month_departure_stats.values()]
    # x locations for the groups:
    ind = np.arange(N)
    # width of the bars:
    width = 0.5
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, monthly_departure_stats, width, color='b')
    ax.set_xlabel('Month of the Year')
    ax.set_ylabel('Number of Hikers')
    ax.set_title('Month Northbound Thru Hikers Depart')
    ax.set_xticks(ind + width)
    plt.xlabel('Jan    Feb    Mar    Apr    May    Jun    July    Aug    Sep    Oct    Nov    Dec')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'northbound_monthly_departure_stats.png'))
    plt.savefig(storage_loc)

def display_thru_hikers(validated_hikers, thru_hikers):
    plt.title('Thru Hikers and Non Thru Hikers on the AT')
    labels=['thru hikers', 'non-thru hikers']
    explode = (0, 0)
    colors = ['#33840e', '#47c10f']
    fraction_of_thru_hikers = ((len(thru_hikers) * 100)/len(validated_hikers))
    fraction_of_non_thru_hikers = 100 - fraction_of_thru_hikers
    print("Number of Hikers: %d" %len(validated_hikers))
    print("Number of Thru Hikers: %d" % len(thru_hikers))
    print("fraction of thru hikers: %d" % fraction_of_thru_hikers)
    fractions = [fraction_of_thru_hikers, fraction_of_non_thru_hikers]
    plt.pie(fractions, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.axis('square')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'percent_thru_hikers.png'))
    plt.savefig(storage_loc)

def main(valid_hikers_path):
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    thru_hikers = get_validated_thru_hikers(valid_hikers)
    display_thru_hikers(valid_hikers, thru_hikers)
    month_departure_stats = {}
    for hid, hiker_info in thru_hikers.items():
        first_entry_num = list(hiker_info['journal'].keys())[0]
        first_entry = hiker_info['journal'][first_entry_num]
        first_entry_date = first_entry['date'].replace(",", "")
        try:
            entry_date = datetime.strptime(first_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, first_entry_num))
        if entry_date.month in month_departure_stats:
            month_departure_stats[entry_date.month] += 1
        else:
            month_departure_stats[entry_date.month] = 1
    print("Total Number Hikers Considered (Northbound and Southbound): %d" %len(thru_hikers))
    print("Monthly Departure Statistics (Northbound and Southbound):")
    print(month_departure_stats)
    display_month_departure_stats(month_departure_stats)

    northbound_departure_stats = {}
    northbound_thru_hikers = get_validated_thru_hikers(get_northbound_hikers(valid_hikers))
    for hid, hiker_info in northbound_thru_hikers.items():
        first_entry_num = list(hiker_info['journal'].keys())[0]
        first_entry = hiker_info['journal'][first_entry_num]
        first_entry_date = first_entry['date'].replace(",", "")
        try:
            entry_date = datetime.strptime(first_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, first_entry_num))
        if entry_date.month in northbound_departure_stats:
            northbound_departure_stats[entry_date.month] += 1
        else:
            northbound_departure_stats[entry_date.month] = 1
    print("\nTotal Number Hikers Considered (Northbound): %d" %len(northbound_thru_hikers))
    print("Monthly Departure Statistics (Northbound):")
    print(northbound_departure_stats)
    display_northbound_month_departure_stats(northbound_departure_stats)

    southbound_departure_stats = {}
    southbound_thru_hikers = get_validated_thru_hikers(get_southbound_hikers(valid_hikers))
    for hid, hiker_info in southbound_thru_hikers.items():
        first_entry_num = list(hiker_info['journal'].keys())[0]
        first_entry = hiker_info['journal'][first_entry_num]
        first_entry_date = first_entry['date'].replace(",", "")
        try:
            entry_date = datetime.strptime(first_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, first_entry_num))
        if entry_date.month in southbound_departure_stats:
            southbound_departure_stats[entry_date.month] += 1
        else:
            southbound_departure_stats[entry_date.month] = 1
    print("\nTotal Number Hikers Considered (Southbound): %d" % len(southbound_thru_hikers))
    print("Monthly Departure Statistics (Southbound):")
    print(southbound_departure_stats)
    display_southbound_month_departure_stats(southbound_departure_stats)

if __name__ == '__main__':

    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    main(valid_hikers_path=validated_hikers_data_path)
