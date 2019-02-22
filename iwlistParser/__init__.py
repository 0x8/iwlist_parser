#!/usr/bin/env python
# Scan and parse the output of iwlist

from __future__ import print_function
import re
import subprocess

class IWCELL:
    '''
    A trimmed instance of the Cells provide by iwlist
    in an easy-to-use format. The name is nothing more
    than the cell number assigned by iwlist, e.g. 'Cell 01'.
    '''

    def __init__(self,name):
        self.name = name
        self.channel = None
        self.address = None
        self.frequency = None
        self.quality = None
        self.signal_level = None
        self.encryption_key_status = None
        self.essid = None
        self.bit_rates = []
        self.mode = None
        self.group_cipher = None
        self.authentication_suites = []
        self.extra = []


def iwlist_output_parse(iwlist_output):
    '''
    Parse the output of iwlist into datastructures that
    can be easily used within Python.
    '''
    iwlist_lines = iwlist_output.splitlines()
    iwlist_lines.remove(iwlist_lines[0])
    iwlist_lines = [line.strip() for line in iwlist_lines]

    # Regex used to match lines denoting bit rates as it would be
    # extremely tricky otherwise.
    bitrate_pattern = re.compile(r'^(\d+ Mb/s|Bit Rates)')

    # Loop through the lines, beginning a new object on each
    # line beginning 'Cell'.
    iwcell_list = []
    for count in range(len(iwlist_lines)):
        line = iwlist_lines[count]
        
        # At each instance of "Cell*" we create a new cell object
        # and can immediately populate the name and MAC of the AP.
        if line.startwsith('Cell'):
            tokenized = line.split(' ')
            name = tokenized[0] + tokenized[1]
            address = tokenized[tokenized.index('Address:')+1]
            cell = IWCELL(name)
            cell.address = address
        
            # Ensure the cell is pushed to the iwcell_list
            # for persistence throughout loop cycles.
            iwcell_list.append(cell)

        # If the line starts with anything OTHER than 'Cell', we
        # can parse those elements and set the corresponding element
        # in iwcell_list[-1] assuming that the last cell appended is
        # the current cell being iterated through.

        # Elements _should_ appear in the order:
        # Channel, Frequency, Quality,Encryption Key,ESSID,Bit Rates,
        # Mode, Extra, A bunch of "IE" (unsure what this is), Group Cipher,
        # Pairwise Ciphers, Authentication Suites, finally possible more
        # unlabeled "IE" groups.

        # Because it is unclear what the IE: groups refer to, they are simply
        # ignored excepting the line containing "IEEE" as the 802.11 spec might
        # be worth knowing. These lines will be parsed in order.         

        if line.startswith('Channel'):
            # "Channel:X"
            channel=int(line.split(':')[1])
            iwcell_list[-1].channel = channel
        
        if line.startswith('Frequency'):
            # "Frequncy:X.XX... GHz (Channel X)"
            freq_num = line.split(':')[1].split(' ')[0]  # value
            freq_unt = line.split(':')[1].split(' ')[1]  # unit (MHz, GHz, etc.)
            freq = freq_num + freq_unt
            iwcell_list[-1].frequency = freq
        
        if line.startswith('Quality'):
            # "Quality=A/B  Signal level=-XX dBm"
            l = line.split("  ")  # Two spaces
            quality = l[0].split('=')[1]
            signal = l[1].split('=')[1]
            iwcell_list[-1].quality = quality
            iwcell_list[-1].signal_level = signal

        if line.startswith('Encryption'):
            # "Encryption key:STATUS"
            status = line.split(":")[1]
            iwcell_list[-1].encryption_key_status = status
        
        if line.startswith('ESSID'):
            # "ESSID:"ESSID""
            essid = line.split(':')[1].strip("\"")
            iwcell_list[-1].essid = essid

        if bitrate_pattern.match(line):
            # Either matched 1) "Bit Rates:A Mb/s; B Mb/s;..."
            # or matched 2) "XX Mb/s; YY Mb/s;..."
            if line.startswith("Bit Rates"):
                # Matched type 1
                rates = line.split(":")[1].split("; ")
                for rate in rates:
                    iwcell_list[-1].bit_rates.append(rate)
            else:
                # Matched type 2
                rates = line.split("; ")
                for rate in rates:
                    iwcell_list[-1].bit_rates.append(rate)

        if line.startswith("Mode"):
            # "Mode:MODE"
            mode = line.split(":")[1]
            iwcell_list[-1].mode = mode

        if line.startswith("Group Cipher"):
            # "Group Cipher : CIPHER"
            group_cipher = line.split(": ")[1]
            iwcell_list[-1].group_cipher = group_cipher

        if line.startswith("Authentication Suite"):
            # "Authentication Suites (X) : SUITE"
            suite = line.split(": ")[1]
            iwcell_list[-1].authentication_suite = suite

        if line.startswith("Extra") or line.startswith("IE:"):
            # Purpose unclear, simply preserve in "Extra" field
            iwcell_list[-1].extra.append(line)

        # END OF LOOP

    return iwcell_list


def scan(interface="wlan0", retry_limit=20):
    '''
    Callable when used as a library to run iwlist, parse output, and return
    cells.
    '''
    # Get the raw listing, trying sudo method first using interface
    # (Note: will automatically fail through to non-priv if needed)
    iwlist_output = get_raw_iwlist_priv(interface, retry_limit)
    
    # Parse the result and return the cell list
    cells = iwlist_output_parse(iwlist_output)

    return cells


def get_raw_iwlist_priv(interface='wlan0', retry_limit=20):
    '''
    Runs subprocess to obtain a raw, unparsed output for
    iwlist to be parsed through in a seperate function
    using sudo to get an immediately refreshed query.
    
    This function requires administrator (root) priveleges
    to use and should return up-to-date results in a single
    execution (nopriv variant must loop until the system
    decides to query the list on its own).
    '''
    try:
        iwlist_output = subprocess.check_output(['sudo','iwlist',interface, 'scan'])
        return iwlist_output
    except CalledProcessError as e:
        print("Incorrect password entered too many times.")
        print("Attempting to run non-priveleged version with retry_limit:", retry_limit)
        iwlist_output = get_raw_iwlist_nopriv(interface, retry_limit)


def get_raw_iwlist_nopriv(interface='wlan0', retry_limit=20):
    '''
    Runs subprocess to obtain a raw, unparsed output for
    iwlist to be parsed through in a seperate function

    This function requires no special priveleges to run however,
    as a consequence it must wait for the system to refresh the
    iwlist.
    '''
    for counter in range(retry_limit):
        # Attempt to get a valid scan within retry_limit tries
        iwlist_output = subprocess.check_output(['iwlist', interface, 'scan'])
        if iwlist_output.find('No scan results') < 1:  # Failed to find substr
            # Got a good scan, break the loop
            break.

        return iwlist_output

