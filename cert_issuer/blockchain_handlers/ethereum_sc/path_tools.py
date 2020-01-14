import os


def get_root_dir():
    root_dir = os.path.abspath(__file__)
    for _ in range(3):
        root_dir = os.path.dirname(root_dir)
    return root_dir


def get_contract_path():
    return get_root_dir() + "/deployment/BlockCertsOnchaining.sol"


def get_compile_data_path():
    return get_root_dir() + "deployment/data/compile_opt.json"


def get_contr_info_path():
    return get_root_dir() + "deployment/data/contr_info.json"


def get_ens_abi_path():
    return get_root_dir() + "/data/ens_abi.json"
