#
# A tool for converting Pronto format hex codes to lircd.conf format
#
# Copyright by Olavi Akerman <olavi.akerman@gmail.com>
#
# pronto2lirc is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

class CodeSequence:  # Handles codesequences parsing and conversion

    def ProcessPreamble(self, sPreamble):
        if sPreamble[0] != "0000":
            raise RuntimeError(f"Formats other than starting with 0000 are not supported!: {sPreamble}")

        self.dIRFrequency = 1000000 / (int(sPreamble[1], 16) * 0.241246)  # Frequency of the IR carrier in Khz

        self.lOnceSequenceLength = int(sPreamble[2], 16)  # No of pulses that is sent once when button is pressed
        self.lRepeatableSequenceLength = int(sPreamble[3], 16)  # No of pulses that are repeatable while button pressed

    def CreatePulses(self, sItems):
        self.dPulseWidths = []  # Table of Pulse widths. Length is repsented in microseconds

        for i in sItems:
            self.dPulseWidths.append(1000000 * int(i, 16) / self.dIRFrequency)  # Convert pulse widths to uS

        if len(self.dPulseWidths) != 2 * (self.lOnceSequenceLength + self.lRepeatableSequenceLength):
            raise RuntimeError("Number of actual codes does not match the header information!")

    def AnalyzeCode(self, sCodeName, sHexCodes):

        sHexTable = sHexCodes.split()
        self.sCodeName = sCodeName.rstrip()  # Name of the Code associated with code sequence

        self.ProcessPreamble(sHexTable[:4])  # First four sequences make up Preamble
        self.CreatePulses(sHexTable[4:])  # The rest are OnceSequence + RepeatableSequence
        return self.dPulseWidths[-1]  # Final gap=last off signal length

    def WriteCodeSection(self, fOut):
        fOut.write('\n\t\t\tname ' + self.sCodeName + '\n')
        for i in range(len(self.dPulseWidths) - 1):  # Do not write the last signal as lircd.conf
            # does not contain last off signal length
            if (i % 6) == 0:
                fOut.write('\t\t\t\t')

            fOut.write('%d ' % round(self.dPulseWidths[i]))

            if (i + 1) % 6 == 0:  # Group codes as six per line
                fOut.write('\n')

        fOut.write('\n')  # Final EOL

fmt = """
  - platform: remote_receiver
    name: irl02_{platform}_{name}_detected
    raw:
      code: {pulses}"""

class HexParser:
    def __init__(self, sFileName):
        f = open(sFileName, 'r')
        self.sRemoteName = sFileName.split('.')[:1][0]  # Name of the remote
        self.sCodes = []  # Codes contained in file
        self.lGap = 0  # Final Gap

        while True:
            sLine = f.readline()
            if sLine == '' or sLine.strip() == '':  # EOF?
                break
            if sLine.strip().startswith("#"):
                continue
            try:
                [sCodeName, sHexCodes] = sLine.split(':')
            except:
                print(f"Couldn't parse {sLine}")
                continue
            seq = CodeSequence()
            finalgap = seq.AnalyzeCode(sCodeName, sHexCodes)
            if finalgap > self.lGap:
                self.lGap = finalgap

            self.sCodes.append(seq)

        f.close()

    def WriteLIRCConf(self, sOutFileName):
        registry = {}
        f = open(sOutFileName, 'w')
        registry = {}
        for iCode,i in enumerate(self.sCodes):
            name = i.sCodeName
            found = False
            for z in ("ipod","z1","z2","z2","z3","z4","ipod"):
                if z in name:
                    found = True
                    break
            if found:
                continue
            found = False
            #for target in ("input","volume","on","off"):
            #    if target in name:
            #        found = True
            #        break
            #if not found:
            #    continue
            for source,target in (("+","_up_"),("-","_down_"),("/","_"),("?","_")):
                name = name.replace(source,target)
            name = name.split("_")
            name = "_".join([part.strip() for part in name if part.strip()])
            print(name)
            pulses = [round(x) for x in i.dPulseWidths[:-1]]
            if name in registry:
                diff = sum([abs(a-b) for (a,b) in zip(pulses,registry[name])])
                if diff == 0:
                    continue
                else:
                    print(f"Variant: {name} {diff}")
                name = f"{name}_{iCode}"
            registry[name] = pulses
            for i in range(1, len(pulses), 2):
                pulses[i] *= -1
            print(fmt.format(platform="denon",name=name,pulses=pulses),file=f)
# Main

import sys

if len(sys.argv) != 2:
    print("Pronto codes converter to lircd.conf format (version 1.00)")
    print()
    print("Usage:   pronto2lirc.py inputfile.hex ")
    print()
    print("Input file must be in format where each line contains all codes")
    print("         associated with a button like:")
    print("         Button1:0000 00ac 000b 00de ...")
    print()
    print("Result:  lircd.conf file is written to the current directory")
    print("         containing all the Pronto codes extracted from")
    print("         the input file")
    print()
else:
    p = HexParser(sys.argv[1])
    p.WriteLIRCConf('lircd.conf')
