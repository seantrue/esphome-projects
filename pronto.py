import os
from collections import namedtuple, defaultdict
from typing import List, Dict
from yaml import safe_dump, safe_load


def hex2int(s: str) -> int:
    return int(s, 16)


Header = namedtuple("Header", ["frequency", "once", "repeatable"])


def pronto_header(hexcodes: List[str]):
    if hexcodes[0] != "0000":
        raise RuntimeError(f"Pronto format {hexcodes[0]} is not supported")
    frequency = hex2int(hexcodes[1])
    frequency = 1000000 / (frequency * 0.241246)
    once = hex2int(hexcodes[2])
    repeatable = hex2int(hexcodes[3])
    return Header(frequency, once, repeatable)


Pronto = namedtuple("Pronto", ["header", "pulses"])


def pronto(hexcodes: List[str]) -> Pronto:
    header = pronto_header(hexcodes)
    pulses = []
    for code in hexcodes[4:]:
        pulse = (hex2int(code) * 1000000) / header.frequency
        pulse = int(round(pulse))
        pulses.append(pulse)
    if len(pulses) != (2 * (header.once + header.repeatable)):
        raise RuntimeError(f"pulses {len(pulses)} is not 2*(once+reapeatable) {header}")
    return Pronto(header=header, pulses=pulses)


def load_pronto(name: str) -> Dict[str,List[List]]:
    path = f"ircodes/{name}"
    assert os.path.exists(path)
    bykey = defaultdict(list)
    with open(path) as inf:
        for line in inf.readlines():
            parts = [part.strip() for part in line.strip().split(':')]
            if len(parts) != 2:
                raise ValueError(f"{parts} does not have 'key:xxxx xxxx ...' form")
            key = "_".join(parts[0].lower().split())
            hexcodes = parts[1].split()
            bykey[key].append(hexcodes)
    return bykey

def pronto2pulses(bykey: Dict[str,List[List]]) -> List[Dict]:
    parsed = []
    for key, hexcodes in bykey.items():
        if len(hexcodes) == 1:
            parsed.append({"key": key, "pronto": hexcodes[0]})
        else:
            for i, alternate in enumerate(hexcodes):
                parsed.append({"key":f"{key}_{i + 1}", "pronto":alternate})
    return parsed

def pronto2esphome(name:str) -> List[Dict]:
    pronto_codes = load_pronto(name)
    key2pulse = pronto2pulses(pronto_codes)
    esphome_codes = []
    for kp in key2pulse:
        # print(kp)
        key, pulses = kp["key"], pronto(kp["pronto"]).pulses
        for i in range(1,len(pulses),2):
            pulses[i] *= -1
        esphome_code = dict(platform="remote_receiver",name=key,raw=dict(code=pulses[:-1]))
        esphome_codes.append(esphome_code)
    return esphome_codes

if __name__ == '__main__':
    esphome_codes = pronto2esphome("denon_12_x.pronto")
    print(safe_dump(esphome_codes))