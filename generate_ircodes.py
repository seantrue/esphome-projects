import os
from typing import List, Dict, Callable
from yaml import safe_load, safe_dump
from pronto import pronto2esphome

Codes = List[Dict]


def load_ircodes(name: str) -> Codes:
    path = f"ircodes/{name}"
    assert os.path.exists(path)
    return safe_load(open(path))


def save_ircodes(name: str, codes: Codes) -> None:
    path = f"ircodes/{name}"
    safe_dump(codes, open(path, "w"))


def export_ircodes(name: str, codes: Codes) -> None:
    path = f"config/ircodes/{name}"
    safe_dump(codes, open(path, "w"))


def show_ircodes(codes: Codes):
    print(safe_dump(codes))


def add_text_sensor(sensor_name: str, codes: Codes) -> None:
    for code in codes:
        code["internal"] = True
        code["on_press"] = [{
            "text_sensor.template.publish":
                {"id": f"template_{sensor_name}",
                 "state": code["name"]}
        }]


text_sensor_template = """text_sensor:
  - platform: template
    name: "{name}"
    id: template_{name}

binary_sensor:
  !include "ircodes/{name}_template.yaml"
"""


def show_text_sensor(name: str) -> str:
    s = text_sensor_template.format(name=name)
    print(s)
    return s


def drop_text_sensor(codes: Codes) -> None:
    for code in codes:
        code.pop("internal", None)
        code.pop("on_press", None)


def mangle_name(codes: Codes, mangler: Callable) -> None:
    for code in codes:
        code["name"] = mangler(code["name"])


def generate_carmp3():
    codes = load_ircodes("carmp3.yaml")
    drop_text_sensor(codes)
    mangle_name(codes, lambda s: s[7:-9])
    add_text_sensor("carmp3", codes)
    export_ircodes("carmp3_template.yaml", codes)
    print("Add this block to your device definition.")
    show_text_sensor("carmp3")


def generate_verizon():
    codes = load_ircodes("verizon.yaml")
    drop_text_sensor(codes)
    mangle_name(codes, lambda s: s[11:-9])
    add_text_sensor("verizon", codes)
    export_ircodes("verizon_template.yaml", codes)
    print("Add this block to your device definition.")
    show_text_sensor("verizon")


def generate_denon():
    denons = "denon_2_x denon_4_x denon_12_x denon_k_2_3 denon_k_4_1 denon_k_4_2 " \
             "denon_k_4_3 denon_k_4_5 denon_k_4_7 denon_k_7_5".split()
    for denon in denons:
        codes = pronto2esphome(f"{denon}.pronto")
        save_ircodes(f"{denon}.yaml", codes)
        add_text_sensor(denon, codes)
        export_ircodes(f"{denon}_template.yaml", codes)
        print("Add this block to your device definition.")
        show_text_sensor(denon)


if __name__ == '__main__':
    generate_carmp3()
    generate_verizon()
    generate_denon()
