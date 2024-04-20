#!/usr/bin/env python3
""" update-fstab - Reads data files to update the /etc/fstab file.

[https://peps.python.org/pep-0257/ How to document docstring's]

"""
import sys
import json
import os
import re
import shutil
from pathlib import Path

# My data module
import sharedata

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#Debug = True
Debug = False
# Verbose = True
Verbose = False
# Require sudo privilege.
# Strict = True
Strict = False

USERNAME = 'cenicol'
OPTIONS = f'uid={USERNAME},gid={USERNAME},credentials=/etc/smb-{USERNAME},iocharset=utf8,vers=2.0'
BEG_SECTION = '# Begin NAS Shares'
END_SECTION = '# End NAS Shares'
begin_re = re.compile(BEG_SECTION)
end_re = re.compile(END_SECTION)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+8 to toggle the breakpoint.


def log(*args, **kwargs):
    print(args, kwargs)
    print(kwargs)
    print("args")
    for s in args:
        print('\t"', s, '"', sep='')
    print("kwargs")
    for s in kwargs:
        print('\t"', s, '"', sep='')


def main():
    print_hi('PyCharm')
    print()
    # pHosts = Path('hosts.json')
    if Path('hosts.json').exists():
        hosts = sharedata.load_hosts(sharedata.HOSTS_NAME)
    else:
        hosts = sharedata.HOSTS.copy()
        sharedata.create_hosts_file()
    # Test to append a new entry
    assert hosts is not None
    if Debug:
        # add a new host: my laser printer
        hosts.update({"brother": "10.0.0.100"})
        print(json.dumps(hosts, indent=4))

    # pShares = Path('shares.json')
    if Path(sharedata.SHARES_NAME).exists():
        shares = sharedata.load_shares(sharedata.SHARES_NAME)
    else:
        shares = sharedata.SHARES.copy()
        sharedata.create_shares_file()
    assert shares is not None
    if Debug:
        print(json.dumps(shares, indent=4))

    # Sets the source and target filenames.
    # If not sudo privilege, then exit if strict,
    # otherwise, change the source and target to be
    # in the local directory.
    # If not sudo privilege, then exit the program.
    source = '/etc/fstab'
    target = source + '.bak'
    if os.getenv("SUDO_USER") is None:
        if Strict:
            print("This program needs 'sudo' privileges")
            exit(1)
        else:
            print("Using local fstab.")
            if Debug:
                print("Changes will be written to fstab.new.")
            source = 'fstab'
            target = source + '.bak'
    else:
        source = '/etc/fstab'
        target = source + '.bak'
    if Debug:
        print('source:', source)
        print('target:', target)
        print()

    assert source is not None
    assert shares is not None

    # Ensure that fstab exists
    # fstab must exist for the next section of code, Create a backup file, to succeed.
    source_path = Path(source)
    if not source_path.exists():
        print('Creating fstab because it does not exist\n')
        source_path.touch()

    # Create a backup file
    try:
        shutil.copyfile(source, target)
    except FileNotFoundError as e:
        print(f'File not found. {e}')
        print(f'{source} is not found')
        exit(1)
    except IOError as e:
        print(f'Unable to copy file. {e}')
        exit(1)
    except:
        print(f'Unexpected error: {sys.exc_info()[0]}')
        exit(1)
    else:
        pass
        # print()

    # Find the maximum share name length. This value is used to create
    # the padding size.
    max_name_len = 0
    for server in shares:
        for share in shares[server]:
            max_name_len = max(max_name_len, len(share))
    max_name_len += 1
    if Debug:
        print('max_name_len\n', max_name_len)
        print('Creating internal fstab\n')

    # Create a bash shell script to create mount points needed in fstab.
    # s = Path.cwd().joinpath('mount.sh')
    s = 'mount.sh'
    print(f'{s} has been created to make directories needed by the mount commands.')
    print(f'use:\n\tsudo bash mount.sh\nto create mount directories.\n')
    mnt_fp = open(s, 'w')
    mnt_fp.write('#!/bin/env bash\n\n')

    new_shares = []
    for server in shares:
        if Debug:
            print(f'Server: {server}', hosts[server])
        for share in shares[server]:
            share_name = '//' + hosts[server] + '/' + share
            share_mount = f'/mnt/{share}'
            mnt_fp.write('mkdir -p ' + share_mount + '\n')
            pad = ' ' * (max_name_len - len(share))
            line = f'{share_name}{pad}{share_mount}{pad}cifs {OPTIONS} 0 0'
            new_shares.append(line)
            if Debug:
                print('\t', line)

    # Close the shell script
    mnt_fp.close()

    if Debug:
        print('End Creating fstab\n')

    # Add in comments encasing the new_shares
    new_shares.insert(0, BEG_SECTION)
    new_shares.append(END_SECTION)

    if Debug:
        print('Begin printing "new_shares"')
        for line in new_shares:
            print('\t' + line)
        print(f'End printing "new_shares"')
        print()

    # Read in fstab
    if Debug:
        print('Begin reading fstab')
    with open(source, 'r') as f:
        fstab = f.readlines()
    # Remove trailing whitespace (newlines)
    for index in range(len(fstab)):
        fstab[index] = fstab[index].rstrip()
    if Debug:
        print(f'End reading fstab {len(fstab)} lines')
        print()

    if Debug:
        print('Begin showing fstab')
        index = 0
        for line in fstab:
            print(f'\t{index} {line}')
            index += 1
        print(f'End showing fstab {index} lines')
        print()

    """ -----------------------------------------------------------------------
    Copy lines from fstab to new_fstab, replacing the existing shares section
    with the new one generated here.
    """
    if Debug:
        print('Begin insert shares section')
    copying = False      # begin_found and not end_found
    begin_found = False
    end_found = False
    index = 0
    new_fstab = []
    for line in fstab:
        index += 1
        if Debug:
            print(index, line)
        if end_found:  # begin_found and end_found
            # Copy the lines after end_found
            new_fstab.append(line)
        else:  # not end_found
            if copying is True:  # begin_found and not end_found
                # Search for end_found
                m_re = end_re.match(line)
                # if Debug: print(f'm_re  {m_re} {len(line)}')
                if m_re:  # if end_found
                    end_found = True
                    copying = False
                continue
            else:  # copying is False: not copying: not begin_found or end_found
                m_re = begin_re.match(line)
                if Debug:
                    print(f'm_re  {m_re} {len(line)}')
                if m_re:
                    # begin_found
                    begin_found = True
                    copying = True
                    # copy fstab to new fstab
                    if Debug:
                        new_fstab.append('# begin_found - start copying')
                        new_fstab.append('# copy new_shares into new_fstab')
                    for share in new_shares:
                        new_fstab.append(share)
                else:  # not begin_found or end_found
                    # Copy the lines before begin_found
                    new_fstab.append(line)
    if Debug and Verbose:
        new_fstab.append(f'begin_found {begin_found}')
        new_fstab.append(f'end_found {end_found}')
        new_fstab.append(f'copying {copying}')
    if not begin_found:
        """
        If past the end of the main loop and the shares section has not been
        found in fstab, then copy the shares here (at the end).
        
        Manual editing of fstab may be needed if the previous shares section in
        fstab was not marked.
        """
        if Debug:
            print('not begin_found')
            print('copying new_shares into new_fstab')
            new_fstab.append('# copying new_shares into new_fstab')
        for share in new_shares:
            print(share)
            new_fstab.append(share)
        if Debug:
            print('end copy')
            new_fstab.append('end copy')
    if Debug:
        print('End insert shares section')
        print()

    # Show new_fstab
    if Debug:
        print('Begin printing new_Fstab')
        index = 0
        for line in new_fstab:
            print(index, line, end='\n')
        print('End printing new_fstab')
        print()

    # Save the updated fstab. If Debug, then write to fstab.new.
    # Otherwise, overwrite fstab
    #
    if Debug:
        print('Begin writing new_fstab')
    # Ensure SOURCE is defined
    assert source is not None
    # if Debug, do not overwrite SOURCE
    update = source
    if Debug:
        update += '.new'
    with open(update, 'w') as f:
        for line in new_fstab:
            f.write(line + '\n')
    if Debug:
        print('End writing new_fstab')

    # End main()


if __name__ == '__main__':
    main()
