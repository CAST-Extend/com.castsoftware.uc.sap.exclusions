'''
Created on 11 nov 2017

@author: TGU
'''
import cast_upgrades.cast_upgrade_1_5_15 # @UnusedImport
from cast.application import ApplicationLevelExtension, ReferenceFinder 

import logging
 
class SAPExclusionsApplication(ApplicationLevelExtension):
 
    def __init__(self):
        logging.info('Init application level')

        self.nbAbapInclude = 0 
        self.nbAbapIncludeExcluded = 0 
        self.nbAbapProgram = 0 
        self.nbAbapProgramExcluded = 0         
        self.nbAbapClasspool = 0         
        self.nbAbapClasspoolExcluded = 0 
        self.nbAbapClass = 0         
        self.nbAbapClassExcluded = 0         
        self.nbAbapFunctionpool = 0         
        self.nbAbapFunctionpoolExcluded = 0 
        self.nbAbapFunction = 0         
        self.nbAbapFunctionExcluded = 0 
        self.nbAbapForm = 0 
        self.nbAbapFormExcluded = 0         
        self.nbAbapFileLevelCodeUnitExcluded = 0 
        self.nbAbapModule = 0 
        self.nbAbapModuleExcluded = 0  
        self.nbAbapFile = 0 

        self.abapPrograms = {} 
        self.abapIncludes = {}
        self.abapIncludesExcluded = {}
        self.abapClasspools = {}
        self.abapClasspoolsExcluded = {}
        self.abapClasses = {}
        self.abapFunctionpools = {}  
        self.abapFunctionpoolsExcluded = {}
        self.abapFunctions = {} 
        self.abapForms = {} 
        self.abapModules = {} 
        self.abapFiles = {}
 
    def end_application(self, application):
        
        self.abapProgramList(application)
        self.abapIncludeList(application)     
        self.abapClasspoolList(application)
        self.abapClassList(application)
        self.abapFunctionpoolList(application)
        self.abapFunctionlList(application)
        self.abapFormlList(application)
        self.abapModulelList(application)
        self.abapFileList(application)
        
        self.lookForGeneratedCodingInFunctions(application)
        self.lookForGeneratedCodingInIncludes(application)
        
        logging.info('**** LookForGeneratedCodeReferencedAsCreatedbySAPUser')
        for line in self.get_intermediate_file('exchange.txt'):        
        #with open('exchange.txt') as f:     # for tests in Eclipse 
        #    for line in f:
            
            logging.info(line.strip())
                
            componentType = line.split(';')[0]
            componentName = line.split(';')[1].strip()

            if (componentType == 'INCLUDE' and componentName in self.abapIncludes): 
                if componentName not in self.abapIncludesExcluded:
                    includeObject = self.abapIncludes[componentName]
                    includeObject.set_as_external()
                    self.abapIncludesExcluded[componentName]=includeObject
                    logging.info('Include [' + str(includeObject) + '] set as external')
                    self.nbAbapIncludeExcluded += 1 
                    
                    # find now the ABAPFileLevelCode and other components part of the include file  
                    # and also exclude them 
                    if componentName in self.abapFiles: 
                        abapComponentFile = self.abapFiles[componentName]
                        for subObject in abapComponentFile.load_objects():
                            subObjectType = subObject.get_type()
                            subObjectName = subObject.get_name()
                            logging.info("Include subObjectName [" + subObjectName + "] subObjectType [" + subObjectType +"]")     

                            if subObjectType == 'CAST_ABAP_FileLevelCodeUnit': 
                                subObject.set_as_external()
                                logging.info('CAST_ABAP_FileLevelCodeUnit [' + str(subObjectName) + '] set as external')
                                self.nbAbapFileLevelCodeUnitExcluded += 1 
                            elif subObjectType == 'abapForm':      
                                subObject.set_as_external()
                                logging.info('abapForm [' + str(subObject) + '] set as external')
                                self.nbAbapFormExcluded += 1 
                            elif subObjectType == 'abapModule':      
                                subObject.set_as_external()
                                logging.info('abapModule [' + str(subObject) + '] set as external')
                                self.nbAbapModuleExcluded += 1                                 
                            else: 
                                logging.info('Subcomponent [' + str(subObject) + '] + [' + subObjectType + '] of the include not determined ==> algorithm to improve ')
                    else: 
                        logging.info("componentName1 [" + componentName + "] not found in the abapFiles") 
                            
                else: 
                    logging.info("include name [" + componentName + "] was already set as external")    
            elif (componentType == 'INCLUDE' and componentName not in self.abapIncludes): 
                logging.info('=======> Undetermined include : need to check if part of a classpool or functionpool')   #TODO 
                
                #if componentName.replace('/','#') in self.abapFiles:                     # check if it is a classpool 
                if componentName in self.abapFiles:                     # check if it is a classpool 
                    
                    abapComponentFile = self.abapFiles[componentName]
                    for subObject in abapComponentFile.load_objects():
                        subObjectType = subObject.get_type()
                        
                        if subObjectType == 'AbapClassPool': 
                            subObjectName = subObject.get_name()
                            if subObjectName not in self.abapClasspoolsExcluded:
                                subObject.set_as_external()
                                self.abapClasspoolsExcluded[subObjectName]=subObject
                                logging.info('Classpool [' + str(subObjectName) + '] set as external')
                                self.nbAbapClasspoolExcluded += 1 
                            else: 
                                logging.info("claspool name [" + subObjectName + "] was already set as external")                        
                        else:
                            if subObjectType != 'AbapClass' and subObjectType != 'AbapMethod': # low level objects 
                                logging.info("Not a AbapClassPool ==> subObjectType [" + subObjectType + "]")
                else: 
                    #logging.info("componentName2 [" + str(componentName.replace('/','#')) + "] not found in the abapFiles") 
                    logging.info("componentName2 [" + str(componentName) + "] not found in the abapFiles") 
                    
                         
            elif (componentType == 'PROGRAM' and componentName in self.abapPrograms): 
                programObject = self.abapPrograms[componentName]
                programObject.set_as_external()
                logging.info('Program [' + str(programObject) + '] set as external')
                self.nbAbapProgramExcluded += 1 
            elif (componentType == 'FUNCTIONPOOL' and componentName in self.abapFunctionpools): 
                if componentName not in self.abapFunctionpoolsExcluded:
                    functionPoolObject = self.abapFunctionpools[componentName]
                    functionPoolObject.set_as_external()
                    logging.info('functionPoolObject [' + str(functionPoolObject) + '] set as external')
                    self.nbAbapFunctionpoolExcluded += 1  
                else: 
                    logging.info("Functionpool name [" + componentName + "] was already set as external")                     
            elif (componentType == 'CLASSPOOL' and componentName in self.abapClasspools): 
                if componentName not in self.abapClasspoolsExcluded:
                    classPoolObject = self.abapClasspools[componentName]
                    classPoolObject.set_as_external()
                    logging.info('classPoolObject [' + str(subObject) + '] set as external')
                    self.nbAbapClasspoolExcluded += 1   
                else: 
                    logging.info("claspool name [" + componentName + "] was already set as external")  
            else: 
                logging.info('### componentType [' + componentType + '] & componentName [' + componentName + '] ==> algorithm to improve or missing in the delivery 2')

        logging.info("=============== Searching done. Exclusions done for ABAP source code")         
        logging.info("Nb of abapInclude : " + str(self.nbAbapInclude))                            
        logging.info('Number of abapIncludes excluded from dashboard : ' + str(self.nbAbapIncludeExcluded))
        logging.info('Number of abapFileLevelCodeUnit excluded from dashboard : ' + str(self.nbAbapFileLevelCodeUnitExcluded))    
        logging.info("Nb of abapPrograms : " + str(self.nbAbapProgram))                       
        logging.info('Number of abapPrograms excluded from dashboard : ' + str(self.nbAbapProgramExcluded))
        logging.info("Nb of abapClasspools : " + str(self.nbAbapClasspool))             
        logging.info('Number of abapClasspools excluded from dashboard : ' + str(self.nbAbapClasspoolExcluded))
        logging.info("Nb of abapClasses : " + str(self.nbAbapClass))             
        logging.info('Number of abapClass excluded from dashboard : ' + str(self.nbAbapClassExcluded))    
        logging.info("Nb of abapFunctionpool : " + str(self.nbAbapFunctionpool))               
        logging.info('Number of abapFunctionpools excluded from dashboard : ' + str(self.nbAbapFunctionpoolExcluded))
        logging.info("Nb of abapFunctions : " + str(self.nbAbapFunction))                                
        logging.info('Number of abapFunctions excluded from dashboard : ' + str(self.nbAbapFunctionExcluded))
        logging.info("Nb of abapForms : " + str(self.nbAbapForm)) 
        logging.info('Number of abapForms excluded from dashboard : ' + str(self.nbAbapFormExcluded))    
        logging.info("Nb of abapModules : " + str(self.nbAbapModule)) 
        logging.info('Number of abapModules excluded from dashboard : ' + str(self.nbAbapModuleExcluded))                 
            
            
        # clean memory 
        self.abapPrograms = {} 
        self.abapIncludes = {}
        self.abapIncludesExcluded = {}
        self.abapClasspools = {}
        self.abapClasspoolsExcluded = {}
        self.abapClasses = {}
        self.abapFunctionpools = {}  
        self.abapFunctionpoolsExcluded = {}
        self.abapFunctions = {} 
        self.abapForms = {} 
        self.abapModules = {} 
        self.abapFiles = {}                

    def abapProgramList(self, application):
    
        for abapProgram in application.objects().has_type('abapProgram'):     
            abapProgram_name = abapProgram.get_name()
            #logging.info("abapProgram Name = [" + abapProgram_name + "]") 
            self.abapPrograms[abapProgram_name] = abapProgram 
            self.nbAbapProgram += 1
            
            
    def abapIncludeList(self, application):
    
        for abapInclude in application.objects().has_type('abapInclude'):     
            abapInclude_name = abapInclude.get_name()
            #logging.info("abapInclude Name = [" + abapInclude_name + "]") 
            self.abapIncludes[abapInclude_name] = abapInclude 
            self.nbAbapInclude += 1
            
            
    def abapClasspoolList(self, application):
    
        for abapClasspool in application.objects().has_type('AbapClassPool'):     
            abapClasspool_name = abapClasspool.get_name()
            #logging.info("abapClasspool Name = [" + abapClasspool_name + "]") 
            self.abapPrograms[abapClasspool_name] = abapClasspool 
            self.nbAbapClasspool += 1
            
        
    def abapClassList(self, application):
    
        for abapClass in application.objects().has_type('AbapClass'):     
            abapClass_name = abapClass.get_name()
            #logging.info("abapClass Name = [" + abapClass_name + "]") 
            self.abapClasses[abapClass_name] = abapClass 
            self.nbAbapClass += 1
            
        
    def abapFunctionpoolList(self, application):
    
        for abapFunctionpool in application.objects().has_type('abapFunctionPool'):     
            abapFunctionpool_name = abapFunctionpool.get_name()
            #logging.info("abapFunctionpool Name = [" + abapFunctionpool_name + "]") 
            self.abapFunctionpools[abapFunctionpool_name] = abapFunctionpool 
            self.nbAbapFunctionpool += 1
            

    def abapFunctionlList(self, application):
    
        for abapFunction in application.objects().has_type('abapFunction'):     
            abapFunction_name = abapFunction.get_name()
            #logging.info("abapFunction Name = [" + abapFunction_name + "]") 
            self.abapFunctions[abapFunction_name] = abapFunction 
            self.nbAbapFunction += 1
            
    def abapFormlList(self, application):
    
        for abapForm in application.objects().has_type('abapForm'):     
            abapForm_name = abapForm.get_name()
            #logging.info("abapForm Name = [" + abapForm_name + "]") 
            self.abapFunctions[abapForm_name] = abapForm 
            self.nbAbapForm += 1            

    def abapModulelList(self, application):
    
        for abapModule in application.objects().has_type('abapModule'):     
            abapModule_name = abapModule.get_name()
            #logging.info("abapModule Name = [" + abapModule_name + "]") 
            self.abapModules[abapModule_name] = abapModule
            self.nbAbapModule += 1          
            
   
    def abapFileList(self, application):

        logging.info('abapFileList')

        #for file in application.get_files([ 'ABAPFile' ]):
        for abapFile in application.get_files():
            
            
            if not abapFile.get_path():
                continue            
            
            if not abapFile.get_path().lower().endswith('.abap'):
                continue
            
            #logging.info("abapFile Name = [" + abapFile.get_path() + "]") 
            
#             abapFile_location = abapFile.get_path().rsplit("\\")[-2:]
#             abapFile_location = "\\".join(abapFile_location).split(".ABAP")[0]
#             logging.info("dev class \ file name [" + str(abapFile_location) + "]")
            
            abapFile_location = abapFile.get_path().rsplit("\\")[-1:]
            abapFile_location = "\\".join(abapFile_location).split(".ABAP")[0]
            #logging.info("file name [" + str(abapFile_location) + "]")
            
            self.abapFiles[abapFile_location.replace('#' , '/')] = abapFile   # text replacement to take into account that the / of namespaces are replaced in file names by the extractor
            self.nbAbapFile += 1   
                          

    def lookForGeneratedCodingInFunctions(self, application):      
            
        logging.info('**** lookForGeneratedCodingInFunctions')
        generated_coding_access = ReferenceFinder()
        generated_coding_access.add_pattern("GeneratedCodingFunction", before="", element="Generated Coding", after="")
        #***** Generated Coding, do not modify *****
                 
        for o in application.get_files(): # restriction to ABAP class would be better

            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            if not o.get_path().lower().endswith('.abap'):
                continue
            
            for reference in generated_coding_access.find_references_in_file(o):
                logging.info("Reference " + reference.value)      
                
                # manipulate the reference pattern found
                searched_generated_coding = reference.value
                sourcefilepath = o.get_path() 
                logging.info("found generated coding [" + searched_generated_coding + "] in file [" + sourcefilepath + "]")
                
                # reading source file                 
                with open(sourcefilepath) as f:
                    for line in f:
                        if line.strip().startswith('FUNCTION'): 
                            function_name = line.split(' ')[1].split('.')[0]
                            logging.info("function name [" + function_name + "] in file [" + sourcefilepath + "] contain generated coding : will be set as external")    
                            
                            functionObject = self.abapFunctions[function_name]
                            functionObject.set_as_external()
                            self.nbAbapFunctionExcluded += 1                             
                

    def lookForGeneratedCodingInIncludes(self, application):      
            
        logging.info('**** lookForGeneratedCodingInIncludes')
        generated_coding_access = ReferenceFinder()
        generated_coding_access.add_pattern("GeneratedCodingInclude", before="", element="THIS FILE IS GENERATED BY THE FUNCTION LIBRARY", after="")
        #THIS FILE IS GENERATED BY THE FUNCTION LIBRARY
                 
        for o in application.get_files(): # restriction to ABAP class would be better

            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            if not o.get_path().lower().endswith('.abap'):
                continue
            
            for reference in generated_coding_access.find_references_in_file(o):
                logging.info("Reference " + reference.value)      
                
                # manipulate the reference pattern found
                searched_generated_coding = reference.value
                sourcefilepath = o.get_path() 
                logging.info("found generated coding [" + searched_generated_coding + "] in file [" + sourcefilepath + "]")
                
                # reading source file                 
                with open(sourcefilepath) as f:
                    for line in f:
                        if line.strip().startswith('INCLUDE_NAME'): 
                            include_name = line.split(' ')[1].split('.')[0]
                            logging.info("include name [" + include_name + "] in file [" + sourcefilepath + "] contain generated coding : will be set as external")    
                            
                            if include_name not in self.abapIncludesExcluded:
                                includeObject = self.abapIncludes[include_name]
                                includeObject.set_as_external()
                                self.abapIncludesExcluded[include_name]=includeObject
                                self.nbAbapIncludeExcluded += 1
                            else: 
                                logging.info("include name [" + include_name + "] in file [" + sourcefilepath + "] was already set as external")    
                