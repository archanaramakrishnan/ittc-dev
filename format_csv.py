#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import csv
from itertools import zip_longest


def format_csv(file_name, grouped):
    if file_name is not None:

        # open the file in read mode

        csvfile = open(file_name, 'r')
    if grouped == 'grouped':
        print_csv_grouped(csvfile)
    elif grouped == 'ungrouped':
        print_csv_ungrouped(csvfile)


def print_csv_grouped(csvfile):

    # use reader function to iterate over the lines of the csvfile object

    reader = csv.reader(csvfile)
    rows = list(reader)

    # delete the row that says 'average stdev average stdev'

    del rows[2]
    transposed_rows = list(map(list, zip_longest(fillvalue='', *rows)))

    # create a list 'longest_lengths' of the max lengths from each column

    longest_lengths = []
    lengths = []
    for cell in transposed_rows[0]:
        lengths.append(len(cell))
    longest_lengths.append(max(lengths))

    # iterate through the transposed rows which consists of [column header, left enftry, right entry, left entry, right entry,..]
    # left row: start at index one and and jump two forward
    # right row: start at index two and jump two forward
    # create list of longest lengths for each column

    for (left_col, right_col) in zip(transposed_rows[1::2],
            transposed_rows[2::2]):
        lengths = []
        for i in range(len(left_col)):
            lengths.append(len(left_col[i]) + len(right_col[i]))
        longest_lengths.append(max(lengths))

    for line in rows:
        row = []

        # Handle first column specially

        row.append(line[0] + ' ' * 5 + ' ' * (int(longest_lengths[0])
                   - len(line[0])))

        # odd cells refer to the left column cells, and even to right column cells

        for (odd_cell, even_cell, space) in zip(line[1::2], line[2::2],
                longest_lengths[1:]):

            # if both cells contain something: left(right)

            if len(odd_cell) > 0 and len(even_cell) > 0:
                output = odd_cell + '(' + even_cell + ')'
            elif len(odd_cell) == 0 and not len(even_cell) == 0:
                output = even_cell
            elif len(even_cell) == 0 and not len(odd_cell) == 0:
                output = odd_cell
            else:
                output = ' '

            row.append(output + ' ' * (space - len(output) + 4))

        print ''.join(map(str, row))


def print_csv_ungrouped(csvfile):

    # use reader function to iterate over the lines of the csvfile object

    reader = csv.reader(csvfile)
    rows = list(reader)

    # goal: to split column headers by underscores and stack the words as the headers are too long as they are

    split_headers = []

    # scan the first line(rows[0]) of the file that contians the column headers
    # separate the headers by underscores and append them to a 'split headers' list

    for header in rows[0]:
        split_headers.append(header.split('_'))

    # transpose the list of lists of headers split by underscores
    # for uneven rows, fill with ""

    transposed_rows_split_headers = list(map(list,
            zip_longest(fillvalue='', *split_headers)))
    print rows

    # delete the unformatted and excessively rows of headers containing the underscores from rows

    del rows[0]

    # insert the formatted and transposed rows of header into the beginning of rows

    for line in transposed_rows_split_headers:
        rows.insert(0, line)

    # transpose the updated rows

    transposed_rows = list(map(list, zip_longest(fillvalue='', *rows)))

    longest_lengths = []
    lengths = []

    # create a list 'longest_lengths' of the max lengths from each column

    for column in transposed_rows:
        lengths = []
        for i in range(len(column)):
            lengths.append(len(column[i]))
        longest_lengths.append(max(lengths))

    for line in rows:
        row = []

        # Handle first and second column specially

        row.append(line[0] + ' ' * (int(longest_lengths[0])
                   - len(line[0]) + 2))
        row.append(line[1] + ' ' * (int(longest_lengths[1])
                   - len(line[1]) + 2))
        for (cell, space) in zip(line[2:], longest_lengths[2:]):

            # if both cells contain something: left(right)

            if len(cell) > 0:
                output = cell
            else:
                output = ' '
            row.append(output + ' ' * (space - len(output) + 5))
        print ''.join(map(str, row))


if __name__ == '__main__':

    # use the positional command line input to get the file directory and normalizatio as input

    parser = argparse.ArgumentParser()
    parser.add_argument('file_name',
                        help='format and print a csv file to terminal',
                        type=str)

    # use "grouped" or "ungrouped" command line flags

    parser.add_argument('grouped',
                        help='format by grouping values like average and stdev/ if not, print ungrouped'
                        , type=str)
    args = parser.parse_args()
    format_csv(args.grouped, args.file_name)

			