'''
Created on 11 nov 2017

@author: TGU
'''
import cast_upgrades.cast_upgrade_1_5_15 # @UnusedImport
import cast.analysers.abap
import logging
import xml.etree.ElementTree as ET

 
class SAPExclusionsAnalysis(cast.analysers.abap.Extension):
 
    def __init__(self):
        logging.info('Init analysis')

        self.componentToBeExcluded = []
        self.includeToBeExcluded = []
        self.nbAbapIncludeExcluded = 0 
        self.programToBeExcluded = []
        self.nbProgrameToBeExcluded = 0         
        self.classpoolToBeExcluded = []
        self.nbAbapClasspoolExcluded = 0 
        self.classToBeExcluded = []
        self.nbAbapClassExcluded = 0         
        self.functionpoolToBeExcluded = []
        self.nbAbapFunctionpoolExcluded = 0 
        
        # the file we will use for exchanging data
        self.exchange_file = None       
 
    def start_analysis(self, options):
        cast.analysers.log.info("=============== Starting looking at ABAP source code for exclusions") 
        self.exchange_file = self.get_intermediate_file('exchange.txt')        
        
    def end_analysis(self, options):
        cast.analysers.log.info("=============== Ending looking at ABAP source code for exclusions")         
        cast.analysers.log.info('Number of Includes to be excluded from dashboard : ' + str(self.nbAbapIncludeExcluded))
        cast.analysers.log.info('Number of Programs to be excluded from dashboard : ' + str(self.nbProgrameToBeExcluded))
        cast.analysers.log.info('Number of Classpool to be excluded from dashboard : ' + str(self.nbAbapClasspoolExcluded))
        cast.analysers.log.info('Number of Functionpools to be excluded from dashboard : ' + str(self.nbAbapFunctionpoolExcluded))
    
    def start_program(self, file): 
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning program file : ' + sourcefilepath)    
        
    def start_include(self, file):
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning include file : ' + sourcefilepath)    
        # reading source file 
        include_name ='' 
        
        with open(sourcefilepath) as f:
            for line in f:
                if 'INCLUDE_NAME' in line: 
                    include_name = line.replace("INCLUDE_NAME", "").split('.')[0].strip()
                    #INCLUDE_NAME LZZXX_M_VOYAGEF00 .
                if '*   view maintenance generator version:' in line:
                    cast.analysers.log.info('Pattern [*   view maintenance generator version:] found in file [' + sourcefilepath + '] corresponding to include [' + include_name + '] so the include will be set as external')    
                    self.addToExclusionList('INCLUDE', include_name)        
        

    def start_frame(self, file):
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning frame file : ' + sourcefilepath)    


    def start_classpool(self, theObject):
        cast.analysers.log.info('Scanning classpool : ' + str(theObject)) 
        

    def start_modulepool(self, file):
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning modulepool file : ' + sourcefilepath)    
     
    def start_functionpool(self, theObject):
        #sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning functionpool : ' + str(theObject)) 
        
    def start_flowlogic(self, file):
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning flowlogic file : ' + sourcefilepath)  

    def start_programs_description_file(self, file): 
        sourcefilepath = file.get_path() 
        cast.analysers.log.info('Scanning programs_description file : ' + sourcefilepath)      
        
        tree = ET.parse(sourcefilepath)
        root = tree.getroot()         
    
        for definition in root.iter('PGDESCRIPTIONS'):
            
            for ABAPprogram in definition.iter('PROGRAM'):
                ABAPprogram_name = ABAPprogram.attrib.get("name")
                ABAPprogram_type = ABAPprogram.attrib.get("type")
                ABAPprogram_lastmodificationauthor = ABAPprogram.attrib.get("lastmodificationauthor") 
                
                if ((ABAPprogram_lastmodificationauthor == 'SAP*') or (ABAPprogram_lastmodificationauthor == 'SAP')): 
                    cast.analysers.log.info('== The [' + ABAPprogram_type + '] named [' + ABAPprogram_name + '] is last modified by [' +  ABAPprogram_lastmodificationauthor + '] and so will be set as external')
                    self.addToExclusionList(ABAPprogram_type, ABAPprogram_name)
                    
                    

    def addToExclusionList(self, componentType, componentName):
        
        if componentType == 'INCLUDE': 
            if componentName not in self.includeToBeExcluded: 
                self.includeToBeExcluded.append(componentName)
                self.exchange_file.write(componentType + ';' + componentName + '\n')
                self.nbAbapIncludeExcluded += 1 
        elif componentType == 'PROGRAM': 
            if componentName not in self.programToBeExcluded: 
                self.programToBeExcluded.append(componentName)
                self.exchange_file.write(componentType + ';' + componentName + '\n')               
                self.nbAbapProgramExcluded += 1 
        elif componentType == 'CLASSPOOL': 
            if componentName not in self.classpoolToBeExcluded: 
                self.classpoolToBeExcluded.append(componentName)
                self.exchange_file.write(componentType + ';' + componentName + '\n')                
                self.nbAbapClasspoolExcluded += 1
        elif componentType == 'CLASS': 
            if componentName not in self.classToBeExcluded: 
                self.classToBeExcluded.append(componentName)
                self.exchange_file.write(componentType + ';' + componentName + '\n')                
                self.nbAbapClassExcluded += 1                
        elif componentType == 'FUNCTIONPOOL': 
            if componentName not in self.functionpoolToBeExcluded: 
                self.functionpoolToBeExcluded.append(componentName)
                self.exchange_file.write(componentType + ';' + componentName + '\n')
                self.nbAbapFunctionpoolExcluded += 1 
        else: 
            cast.analysers.log.info('!!!!== Undefined type [' + componentType + '] for component [' + componentName + ']')
            
