# -*- coding: utf-8 -*-

import os
import argparse
# import cmake
# import ewpproject
# import uvprojxproject
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

        print('\n\n### start list source files. ###\n\n')
        for element in self.root.Targets.Target.Groups.getchildren():
            # print('GroupName: ' + element.GroupName.text)
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

        print('\n\n### start list include paths. ###\n\n')
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
            print(s)
        print('\n\n')
        self.project['files'] = []


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
            print("Size:", match_ram.group(2), '= %d kB' % (size // 1024) )
        else:
            print("No match found.")

        if match_rom:
            start_addr = int(match_rom.group(1), 16)
            size = int(match_rom.group(2), 16)
            self.project['rom_addr'] = start_addr
            self.project['rom_size'] = size
            print("ROM Start Address:", start_addr)
            print("Size:", size)

    def getProject(self):
        """ Return parsed project settings stored as dictionary
        @return Dictionary containing project settings
        """
        return self.project


def find_file(path, fileext):
    """ Find file with extension in path
        @param path Root path of the project
        @param fileext File extension to find
        @return File name
    """
    filename = ''
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(fileext):
                filename = os.path.join(root, file)
    return filename

if __name__ == '__main__':
    """ Parses params and calls the right conversion"""

    parser = argparse.ArgumentParser()
    # parser.add_argument("format", choices=("ewp", "uvprojx"))
    parser.add_argument("-p", '--path', type=str, help="Root directory of project, default is current dir")
    parser.add_argument("-f", '--file', type=str, help="file name of project like a.uvprojx")
	#"--ewp", help="Search for *.EWP file in project structure", action='store_true')
    #parser.add_argument("--uvprojx", help="Search for *.UPROJX file in project structure", action='store_true')
    args = parser.parse_args()

    # 如果加了 -f xx.uvprojx就是选择某个工程 否则按路径选第一个匹配扩展名
    # 策略 直接执行就是path = '.'当前目录
    filename = ''
    path = ''
    if args.file:
        filename = args.file
    elif args.path:
        path = args.path
    else:
        path = '.'

    if os.path.isdir(path):
        print('Looking for *.uvprojx file in ' + path)
        filename = find_file(path, '.uvprojx')
    else:
        print('not valid path')
    
    print(filename)
    if len(filename):
        print('Found project file: ' + filename)
        project = UVPROJXProject(path, filename)
        project.parseProject()
        project.displaySummary()

        # cmakefile = cmake.CMake(project.getProject(), '../')
        # cmakefile.populateCMake()
    else:
        print('No project *.uvprojx file found')
