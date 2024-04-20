import json
# from pathlib import Path


# hosts file lookup
HOSTS: dict = {
    "buffalo": "10.0.0.107",
    "synology": "10.0.0.108",
}
HOSTS_NAME: str = 'hosts.json'

# smb share names to be created in fstab
SHARES: dict = {
    "buffalo": [
        'Music',
        'Cassie-Windows',
        'Cassie-Linux',
        'Cassie-Backup',
        'Cassie',
        'cenicol',
        'Shared',
    ],
    "synology": [
        'Cassie_Windows',
        'homes',
        'LaurieO',
        'linux',
        'music',
        'web',
        'web_packages'
    ],
}
SHARES_NAME: str = 'shares.json'


def load_json(name: str) -> dict:
    """
    Loads a json file into in memory python data.

    :param name:  The name of the file to load
    :return: The loaded json data
    """
    # data = None
    with open(name, 'r') as fp:
        data = json.load(fp)
    # print(type(data), data)
    return data


def save_json(name: str, data: dict) -> None:
    with open(name, 'w') as fp:
        json.dump(data, fp, indent=4)


def create_hosts_file() -> None:
    """
    Creates hosts file for HOSTS data in the beginning of this file.
    :return: Nothing
    """
    save_json(HOSTS_NAME, HOSTS)


def save_hosts(name: str, data: dict) -> None:
    """
    Saves the hosts dictionary to the named file.

    :param name: The name of the hosts file.
    :param data: The hosts dictionary.
    :return: Nothing
    """

    save_json(name, data)


def load_hosts(name: str) -> dict:
    """
    Loads the hosts dict from the named file.

    :param name: The name of the hosts file
    :return: The translated hosts dictionary
    """
    return load_json(name)


def create_shares_file() -> None:
    """
    Creates the shares file for SHARES data in the beginning of this file.

    :return: Nothing
    """
    save_json(SHARES_NAME, SHARES)


def save_shares(name: str, data: dict) -> None:
    """
    Saves the shares dictionary to the named file.

    :param name: The name of the shares file.
    :param data: The shares dictionary.
    :return: Nothing
    """
    save_json(name, data)


def load_shares(name: str) -> dict:
    """
    Loads the shares dict from the named file.

    :param name: The name of the shares file
    :return: The shares dictionary
    """
    return load_json(name)
