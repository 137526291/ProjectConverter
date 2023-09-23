# -*- coding: utf-8 -*-

""" Module for converting UVPROJX project format file
    @file
"""

import os
import re
from lxml import objectify

class UVPROJXProject(object):
    """ Class for converting UVPROJX project format file
    """

    def __init__(self, path, xmlFile):
        self.path = path
        self.project = {}
        self.xmlFile = xmlFile
        xmltree = objectify.parse(xmlFile)
        self.root = xmltree.getroot()

    def parseProject(self):
        """ Parses EWP project file for project settings
        """
        self.project['name'] = self.root.Targets.Target.TargetName
        self.project['chip'] = str(self.root.Targets.Target.TargetOption.TargetCommonOption.Device)
        self.project['incs'] = self.root.Targets.Target.TargetOption.TargetArmAds.Cads.VariousControls.IncludePath.text.split(';')
        self.project['mems'] = self.root.Targets.Target.TargetOption.TargetCommonOption.Cpu
        self.project['defs'] = self.root.Targets.Target.TargetOption.TargetArmAds.Cads.VariousControls.Define.text.split(',')
        self.project['srcs'] = []

        for element in self.root.Targets.Target.Groups.getchildren():
            print('GroupName: ' + element.GroupName.text)
            if hasattr(element, 'Files'):
                # if hasattr(element.Files.getchildren(), 'FileOption'):
                #     print(element.Files.File.FileOption.CommonProperty.IncludeInBuild)
                for file in element.Files.getchildren():
                    # if not str(file.FilePath.text).endswith('.s'):
                    if not hasattr(file, 'FileOption') or \
                        hasattr(file, 'FileOption') and file.FileOption.CommonProperty.IncludeInBuild:
                        s = str(file.FilePath.text)
                        # if os.path.sep not in s:
                        # if os.path.sep == '\\':
                        s = s.replace('\\', '/')
                        s = s.lstrip('../')
                            # elif os.path.sep == '/':
                            #     s = s.replace('\\', '/')
                        print(s)
                        self.project['srcs'].append(s)

        for i in range(0, len(self.project['incs'])):
            s = str(self.project['incs'][i])
            # if os.path.sep not in s:
            # if os.path.sep == '\\':
            s = s.replace('\\', '/')
            # s = s[3:]
            s = s.lstrip('../')
            #     elif os.path.sep == '/':
            #         s = s.replace('\\', '/')

            # self.project['incs'][i] = s.replace('..', self.path, 1)
            self.project['incs'][i] = s

        self.project['files'] = []
        i = 0

        # if os.path.exists(self.path + '/Drivers/CMSIS/Device/ST/STM32F3xx/Source/Templates/gcc'):
        #     for entry in os.listdir(self.path + '/Drivers/CMSIS/Device/ST/STM32F3xx/Source/Templates/gcc'):
        #         if entry.endswith('.S') or entry.endswith('.s'):
        #             self.project['files'].append(self.path + '/Drivers/CMSIS/Device/ST/STM32F3xx/Source/Templates/gcc/'+ entry)




    def displaySummary(self):
        """ Display summary of parsed project settings
        """
        print('Project Name:' + self.project['name'])
        print('Project chip:' + self.project['chip'])
        print('Project includes: ' + ' '.join(self.project['incs']))
        print('Project defines: ' + ' '.join(self.project['defs']))
        print('Project srcs: ' + ' '.join(self.project['srcs']))
        print('Project mems: ' + self.project['mems'])

        # string = 'IROM(0x08000000,0x040000)'
        string  = str(self.project['mems'])
        pattern_ram = r'IRAM\((0x[0-9A-Fa-f]+),0x([0-9A-Fa-f]+)\)'
        pattern_rom = r'IROM\((0x[0-9A-Fa-f]+),0x([0-9A-Fa-f]+)\)'

        match_ram = re.search(pattern_ram, string)
        match_rom = re.search(pattern_rom, string)
        if match_ram:
            start_addr = int(match_ram.group(1), 16)
            size = int(match_ram.group(2), 16)
            self.project['ram_size'] = size
            print("RAM Start Address:", match_ram.group(1))
            print("Size:", match_ram.group(2))
        else:
            print("No match found.")

        if match_rom:
            start_addr = int(match_rom.group(1), 16)
            size = int(match_rom.group(2), 16)
            self.project['rom_addr'] = start_addr
            self.project['rom_size'] = size
            print("ROM Start Address:", start_addr)
            print("Size:", size)

        if ''

    def getProject(self):
        """ Return parsed project settings stored as dictionary
        @return Dictionary containing project settings
        """
        return self.project


if __name__ == '__main__':
    print('run')
    uv = UVPROJXProject('.', './mdk/f303.uvprojx')
    uv.parseProject()
    uv.displaySummary()