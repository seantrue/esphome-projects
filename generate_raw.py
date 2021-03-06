lines = [line.strip() for line in open("QIP6200-2_lirc.conf").readlines()]
lines = [line for line in lines if not line.startswith("#")]
track = ("header","one","zero","ptrail","bits")
definitions = {}
in_codes = False
print("""# Example configuration entry
text_sensor:
  - platform: template
    name: "verizon"
    id: template_verizon""")
for line in lines:
    if not line:
        continue
    parts = line.split()
    if parts[0] in track:
        definitions[parts[0]] = [int(part) for part in parts[1:]]
        continue
    if line.startswith("begin codes"):
        in_codes = True
        continue
    if line.startswith("end codes"):
        in_codes = False
        continue
    if in_codes:
        name = parts[0]
        code = parts[1]
        code = int(code[2:],16)
        bits = definitions["bits"][0]
        binary = f"{code:016b}"
        binary = binary[-bits:]
        timing = definitions["header"][:]
        for bit in binary:
            if bit == '0':
                timing += definitions["zero"]
            else:
                timing += definitions["one"]
        timing += definitions["ptrail"]
        for i in range(1,len(timing),2):
            timing[i] *= -1
        print(f"""- platform: remote_receiver
  internal: true
  name: "{name.lower()}"
  on_press:
    - text_sensor.template.publish:
        id: template_verizon
        state: "{name[4:].lower()}"
  raw:
    code: {timing}""")


