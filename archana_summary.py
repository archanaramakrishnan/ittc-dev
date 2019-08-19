#!/usr/bin/python
# -*- coding: utf-8 -*-
#https://pythoniter.appspot.com/

import argparse
import csv
import glob
import io
import math
import os.path
import re
import statistics
import sys
from itertools import zip_longest
import format_csv

# sample command line input
# python3 archana_summary.py /nfs/projects/zephyr/wayedt/mibench_results/gcc /nfs/projects/zephyr/wayedt/mibench_results/llvm_diff --csv report.csv -n nopgo

print 'hello research world!'

# regex to find all decimal values that denote the time taken

TIME_PATTERN = re.compile(r' *(\d+\.\d+).*')


def normalized_standard_deviation(normalize_config, current_config):
    return 1 - (normalize_config[0] - current_config[0] - 2.262
                * math.sqrt(current_config[1] ** 2 / 10
                + float(normalize_config[1]) ** 2 / 10)) \
        / normalize_config[0] - current_config[0] / normalize_config[0]


def four_precision(*args):

    # if string is a tuple with more than one value:
    # return first(second), both in four precision

    if len(args) > 1:
        return '%0.4f(%0.4f)' % args
    else:

   # if string is a single element tuple:
    # return element in four precision

        return '%0.4f' % args[0]


def benchmarks_report(directory_list, normalize, file_name):

    # to report benchmarks

    contained_benchmarks = []
    benchmarks_and_directory = {}
    benchmarks = []
    formatted_benchmarks = []

    # store all the names of the benchmarks in a list
    # use glob to extract the names of the directories such as picking up "automotive/basicmath" from "/nfs/projects/zephyr/wayedt/mibench_results/gcc/automotive/basicmath/"

    for directory in directory_list:
        for i in glob.glob('%s/*/*/' % os.path.abspath(directory)):
            contained_benchmarks.append(i[len(directory) + 1:-1])
            if not i[len(directory):-1] in benchmarks:
                benchmarks.append(i[len(directory):-1])
        benchmarks_and_directory[directory] = contained_benchmarks
        contained_benchmarks = []

    # remove leading /

    for i in range(len(benchmarks)):
        formatted_benchmarks.append((benchmarks[i])[1:])

    sorted_benchmarks = sorted(formatted_benchmarks)

    # create a loop to extract all the configs from the different directories

    configs = []
    for directory in directory_list:
        for i in glob.glob('%s/*/*/*' % os.path.abspath(directory)):
            config_name = i[i.rfind('/') + 1:i.rfind('_')]
            if config_name not in configs and config_name != '':
                configs.append(config_name)

    if not normalize == None:
        copy_configs = configs
        configs = []

        # append the config that you are normalizing by to the beginning of the list

        for config in copy_configs:

            # mark normalizing config with an asterisk

            if config == normalize:
                configs.append(config + '*')

        # append all the configs other than the one being used to normalize

        for config in copy_configs:
            if not config == normalize:
                configs.append(config)
    print configs
    split_path = os.path.abspath(directory_list[0]).split('/')
    number_of_directories = len(split_path)

    # slice off the directory paths until where they do not share common directories
    # for example, take:
    # /nfs/projects/zephyr/wayedt/mibench_results/gcc
    # /nfs/projects/zephyr/wayedt/mibench_results/llvm_diff
    # and turn it into gcc and llvm_diff

    # go through each index of all directories (each word bounded by / on both sides)
    # if equal, increment count
    # remove count number of items from the beginning of each directory

    count = []
    same_directory_count = 0
    truncated_directories = []
    for directory in directory_list:
        for i in range(number_of_directories):
            if os.path.abspath(directory).split('/')[i] \
                == os.path.abspath(directory_list[0]).split('/')[i]:
                same_directory_count += 1
        count.append(same_directory_count)
        same_directory_count = 0

    to_remove = min(count)
    for directory in directory_list:
        truncated = '/'.join(os.path.abspath(directory).split('/'
                             )[to_remove:])
        truncated_directories.append(truncated)
    time_lst = []
    sum_lst = []

    # use regex to pull out the required info from file

    all_results = {}
    results = {}
    longest = 0
    longest_name = ''
    for directory in directory_list:

        # print('\n')
        # print(os.path.abspath(directory))

        for benchmark in sorted_benchmarks:
            results[benchmark] = {}
            if benchmark in benchmarks_and_directory[directory]:

                # print(benchmarks_and_directory[directory])

                if len(benchmark) > longest:
                    longest = len(benchmark)
                    longest_name = benchmark
                for config_name in configs:
                    time_lst = []
                    for fname in glob.glob(os.path.abspath(directory)
                            + '/' + benchmark + '/' + config_name
                            + '_*.txt'):
                        with open(fname) as file:
                            sum_of_pair = 0
                            for line in file:
                                m = TIME_PATTERN.match(line)
                                if not m == None:
                                    sum_of_pair += float(m.groups()[0])
                            time_lst.append(sum_of_pair)

                    average = sum(time_lst) / len(time_lst)
                    standdev = statistics.stdev(time_lst)
                    results[benchmark][config_name] = (average,
                            standdev)
            else:
                for config_name in configs:
                    results[benchmark][config_name] = None

        for truncdirectory in truncated_directories:
            if truncdirectory in directory:
                all_results[truncdirectory] = results
                results = {}

    csv_configs = ['']
    csv_directories = ['']

    # write the above table in to a csv file

    if not file_name == None:
        csvfile = open(file_name, 'w')
    else:
        csvfile = io.StringIO('')

    benchmark_writer = csv.writer(csvfile, delimiter=',')
    for directory in truncated_directories:
        csv_directories.append(directory)
        csv_directories += [''] * 3
        for config in configs:
            csv_configs.append(config)
            csv_configs.append('')

    benchmark_writer.writerow(csv_directories)
    benchmark_writer.writerow(csv_configs)
    benchmark_writer.writerow([''] + ['average', 'standard_deviation']
                              * len(configs)
                              * len(truncated_directories))

    # mark normalizing config with an asterisk

    if not normalize == None:
        normalize = normalize + '*'
    for benchmark in sorted_benchmarks:
        row = [benchmark]
        for directory in truncated_directories:
            for configuration in configs:
                if not all_results[directory][benchmark][configuration] \
                    == None:
                    if not normalize == None:
                        row.append(four_precision(all_results[directory][benchmark][normalize][0]))
                        row.append(four_precision(all_results[directory][benchmark][normalize][1]))
                        break
                    row.append(four_precision(all_results[directory][benchmark][configuration][0]))
                    row.append(four_precision(all_results[directory][benchmark][configuration][1]))
                else:
                    row.append('-')
                    row.append('-')
            if not normalize == None:
                for configuration in configs:
                    if not all_results[directory][benchmark][configuration] \
                        == None and not configuration == normalize:
                        row.append(four_precision(all_results[directory][benchmark][configuration][0]
                                   / all_results[directory][benchmark][normalize][0]))
                        row.append(four_precision(normalized_standard_deviation(all_results[directory][benchmark][normalize],
                                   all_results[directory][benchmark][configuration])))

        benchmark_writer.writerow(row)

    if file_name is not None:
        csvfile.close()
        csvfile = open(file_name, 'r')
    else:
        csvfile.seek(0)

        # import pdb; pdb.set_trace()

    format_csv.print_csv_grouped(csvfile)


# use the positional command line input to get the file directory and normalizatio as input

parser = argparse.ArgumentParser()
parser.add_argument('file_path', nargs='+',
                    help='generate a benchmarks report using the files in the directory given'
                    , type=str)
parser.add_argument('-n', '--normalize',
                    help='normalizes the values of all the times of the configurations with respect to a chosen one'
                    , action='store')
parser.add_argument('--csv',
                    help='takes in the file name of the csv file to store collected data. if no name mentioned, no csv file is created'
                    , action='store')
args = parser.parse_args()
benchmarks_report(args.file_path, args.normalize, args.csv)


			