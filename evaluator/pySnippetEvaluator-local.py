import requests
import json
import subprocess
import time
import os
import ast
import numpy as np
import pandas as pd

class pySnippetEvaluator():
    def __init__(self,getURL3,postURL3,getURL2,postURL2,interval=0.1,timeout=10,local=False):
        self.getURL3=getURL3
        self.postURL3=postURL3
        self.getURL2=getURL2
        self.postURL2=postURL2
        self.interval=interval
        self.timeout=timeout #Default 10 seconds
        self.local=local
        if(local):
            self.dataFrame=pd.read_csv(self.getURL3)
            self.nextIndex=0 #initialize index for local environment
            self.currentCount=0 # initialize current counter for retireving a snippet for multiple times
            self.dfNumRow=len(self.dataFrame.index)


    def snippetParser(self,snippet):
        #newS=snippet
        newS=bytearray(snippet, 'utf8').decode('unicode_escape') #use bytearry to decode string and remove escape characters
        #newS=snippet.lstrip() #'remove space'
        newS=newS.replace('>>> ','') #'Remove >>>'
        #newS=newS.replace('\\n','\n') #'replace \\n with \n'
        #newS=newS.replace('\\t','\t') #'replace \\t with \t'
        newS=newS.replace('\t','    ') #'replace tab with 4 spaces'
        #Remove leading spaces in each line
        numSpaces=len(newS)-len(newS.lstrip())
        newS=newS.lstrip()
        strSpaces='\n'+' '*numSpaces
        newS=newS.replace(strSpaces,'\n')
        return(newS)

    def importParser(self,snippetString):
        import_string=snippetString
        modules=[]
        try:
            for node in ast.iter_child_nodes(ast.parse(import_string)):
                if isinstance(node, ast.ImportFrom):
                    if not node.names[0].asname:  # excluding the 'as' part of import
                        modules.append(node.module)
                elif isinstance(node, ast.Import): # excluding the 'as' part of import
                    if not node.names[0].asname:
                        modules.append(node.names[0].name)
        except:
            return []
        return modules

    def error2Code(self,errorType):
        statusCode={
            'Success':0,
            'UnkownError':1,
            'ImportAndSyntaxError':2,
            'ExitCodeException':3,
            'StandardError':11,
            'BufferError':12,
            'ArithmeticError':13,
            'FloatingPointError':14,
            'OverflowError':15,
            'ZeroDivisionError':16,
            'AssertionError':17,
            'AttributeError':18,
            'EnvironmentError':19,
            'IOError':20,
            'OSError':21,
            'WindowsError':22,
            'VMSError':23,
            'EOFError':24,
            'ImportError':25,
            'LookupError':26,
            'IndexError':27,
            'KeyError':28,
            'MemoryError':29,
            'NameError':30,
            'UnboundLocalError':31,
            'ReferenceError':32,
            'RuntimeError':33,
            'NotImplementedError':34,
            'SyntaxError':35,
            'IndentationError':36,
            'TabError':37,
            'SystemError':38,
            'TypeError':39,
            'ValueError':40,
            'UnicodeError':41,
            'UnicodeDecodeError':42,
            'UnicodeEncodeError':43,
            'UnicodeTranslateError':44,
            'StopIteration':45,
            'StopAsyncIteration':46,
            'ModuleNotFoundError':47,
            'BlockingIOError':48,
            'ChildProcessError':49,
            'ConnectionError':50,
            'BrokenPipeError':51,
            'ConnectionAbortedError':52,
            'ConnectionRefusedError':53,
            'ConnectionResetError':54,
            'FileExistsError':55,
            'FileNotFoundError':56,
            'InterruptedError':57,
            'IsADirectoryError':58,
            'NotADirectoryError':59,
            'PermissionError':60,
            'ProcessLookupError':61,
            'TimeoutError':62,
            'RecursionError':63,
            'TimeoutExpired':64,
        }
        try:
            code=statusCode[errorType]
            return(code)
        except:
            return 1

    def getSnippet(self,getURL,fileNamePrefix='',local=False):
        #If all snippets have been retrieved, the error will kill the container.
        if(not local):
            #Fetch from the remote database
            response=json.loads(requests.request('GET', getURL).text) 
        else:
            #Read from the dataframe
            response=self.dataFrame.iloc[self.nextIndex]
            self.currentCount=self.currentCount+1
            if(self.currentCount==2):
                self.nextIndex=self.nextIndex+1
                self.currentCount=0
            if(int(self.nextIndex/self.dfNumRow*100)%5==0): #Write results to the file whenever the progress increases by 5% 
                self.dataFrame.to_csv(getURL,index=False)
        snippetID=response['pk']
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        with open(pyFileName,'a') as pyFile:
            pyFile.write(self.snippetParser(response['content']))
        pyFile.close()
        return snippetID

    def postResult(self,postURL,resultDict,local=False,version=3):
        if(not local):
            #Post to the remote database
            payload="pk=%s&status_code=%s&result=%s&execution_time=%s"%(str(resultDict['pk']),str(resultDict['status_code']),resultDict['result'],str(resultDict['execution_time']))
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request('POST', postURL, headers = headers, data = payload.encode('utf-8'), allow_redirects=False)
        else:
            #Write to the dataframe
            if(version==3):
                self.dataFrame.at[self.nextIndex-1,'status_code_p3']=resultDict['status_code']
                self.dataFrame.at[self.nextIndex-1,'python3_result']=resultDict['result']
                self.dataFrame.at[self.nextIndex-1,'execution_time_p3']=resultDict['execution_time']
            if(version==2):
                self.dataFrame.at[self.nextIndex-1,'status_code_p2']=resultDict['status_code']
                self.dataFrame.at[self.nextIndex-1,'python2_result']=resultDict['result']
                self.dataFrame.at[self.nextIndex-1,'execution_time_p2']=resultDict['execution_time']

    def py3Execute(self,snippetID,fileNamePrefix='',local=False):
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        result={}
        result['pk']=snippetID
        startTime=time.time()
        proc=subprocess.Popen(['python3',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
        except subprocess.TimeoutExpired:
            result['status_code']=64
            result['result']='TimeoutExpired'
            result['execution_time']=self.timeout
            #post results
            self.postResult(self.postURL3,result,local=local,version=3)
            #remove the file after posting results
            rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return
        endTime=time.time()
        executionResult=executionResult[0].decode('utf-8',errors='backslashreplace')
        returnCode=proc.returncode
        executionTime=endTime-startTime
        #Remove py file after evaluation
        if(returnCode==0): #success
            result['status_code']=0
            result['result']=executionResult
            result['execution_time']=executionTime
        else:
            try:
                errorType=executionResult.splitlines()[-1].split(':')[0]
            except:
                errorType='ExitCodeException'
            # if module installation needed
            if(errorType=='ImportError' or errorType=='ModuleNotFoundError'):
                with open(pyFileName) as pyFile:
                    snippetString=pyFile.read()
                pyFile.close()
                moduleNameList=self.importParser(snippetString)
                if(len(moduleNameList)==0): 
                #The snippet has both import error and syntax error.
                    result['status_code']=self.error2Code('ImportAndSyntaxError')
                    result['result']=executionResult
                    result['execution_time']=executionTime
                    #post results
                    self.postResult(self.postURL3,result,local=local,version=3)
                    #remove the file after posting results
                    rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    return
                else:
                    for moduleName in moduleNameList:
                        if(moduleName==None): #Handle from . import module
                            continue
                        procpip=subprocess.Popen(['pip3','install',moduleName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        pipResult=procpip.communicate()[0]#make Popen blocking
                    #Re-evluate
                    startTime=time.time()
                    proc=subprocess.Popen(['python3',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    try:
                        executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
                    except subprocess.TimeoutExpired:
                        result['status_code']=64
                        result['result']='TimeoutExpired'
                        result['execution_time']=self.timeout
                        #post results
                        self.postResult(self.postURL3,result,local=local,version=3)
                        #remove the file after posting results
                        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        return
                    endTime=time.time()
                    executionResult=executionResult[0].decode('utf-8',errors='backslashreplace')
                    returnCode=proc.returncode
                    executionTime=endTime-startTime
                    if(returnCode==0): #success
                        result['status_code']=0
                        result['result']=executionResult
                        result['execution_time']=executionTime
                        #post results
                        self.postResult(self.postURL3,result,local=local,version=3)
                        #remove the file after posting results
                        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        return
            result['status_code']=self.error2Code(errorType)
            result['result']=executionResult
            result['execution_time']=executionTime
        #post results
        self.postResult(self.postURL3,result,local=local,version=3)
        #remove the file after posting results
        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def py2Execute(self,snippetID,fileNamePrefix='',local=False):
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        result={}
        result['pk']=snippetID
        startTime=time.time()
        proc=subprocess.Popen(['python2',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
        except subprocess.TimeoutExpired:
            result['status_code']=64
            result['result']='TimeoutExpired'
            result['execution_time']=self.timeout
            #post results
            self.postResult(self.postURL2,result,local=local,version=2)
            #remove the file after posting results
            rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return
        endTime=time.time()
        executionResult=executionResult[0].decode('utf-8',errors='backslashreplace')
        returnCode=proc.returncode
        executionTime=endTime-startTime
        #Remove py file after evaluation
        if(returnCode==0): #success
            result['status_code']=0
            result['result']=executionResult
            result['execution_time']=executionTime
        else:
            try:
                errorType=executionResult.splitlines()[-1].split(':')[0]
            except:
                errorType='ExitCodeException'
            # if module installation needed
            if(errorType=='ImportError' or errorType=='ModuleNotFoundError'):
                with open(pyFileName) as pyFile:
                    snippetString=pyFile.read()
                pyFile.close()
                moduleNameList=self.importParser(snippetString)
                if(len(moduleNameList)==0): 
                #The snippet has both import error and syntax error.
                    result['status_code']=self.error2Code('ImportAndSyntaxError')
                    result['result']=executionResult
                    result['execution_time']=executionTime
                    #post results
                    self.postResult(self.postURL2,result,local=local,version=2)
                    #remove the file after posting results
                    rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    return
                else:
                    for moduleName in moduleNameList:
                        if(moduleName==None): #Handle from . import module
                            continue
                        procpip=subprocess.Popen(['pip2','install',moduleName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        pipResult=procpip.communicate()[0]#make Popen blocking
                    #Re-evluate
                    startTime=time.time()
                    proc=subprocess.Popen(['python2',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    try:
                        executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
                    except subprocess.TimeoutExpired:
                        result['status_code']=64
                        result['result']='TimeoutExpired'
                        result['execution_time']=self.timeout
                        #post results
                        self.postResult(self.postURL2,result,local=local,version=2)
                        #remove the file after posting results
                        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        return
                    endTime=time.time()
                    executionResult=executionResult[0].decode('utf-8',errors='backslashreplace')
                    returnCode=proc.returncode
                    executionTime=endTime-startTime
                    if(returnCode==0): #success
                        result['status_code']=0
                        result['result']=executionResult
                        result['execution_time']=executionTime
                        #post results
                        self.postResult(self.postURL2,result,local=local,version=2)
                        #remove the file after posting results
                        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        return
            result['status_code']=self.error2Code(errorType)
            result['result']=executionResult
            result['execution_time']=executionTime
        #post results
        self.postResult(self.postURL2,result,local=local,version=2)
        #remove the file after posting results
        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def py3Evaluate(self,fileNamePrefix=''):
        print("Start running")
        while True:
            try:
                pk=self.getSnippet(self.getURL3)
                self.py3Execute(pk,fileNamePrefix)
            except:
                continue
            time.sleep(self.interval)

    def py2Evaluate(self,fileNamePrefix=''):
        print("Start running")
        while True:
            try:
                pk=self.getSnippet(self.getURL2)
                self.py2Execute(pk,fileNamePrefix)
            except:
                continue
            time.sleep(self.interval)

    def py3py2Evaluate(self):
        while True:
            pk3=self.getSnippet(self.getURL3,fileNamePrefix='py3_',local=self.local)
            self.py3Execute(pk3,fileNamePrefix='py3_',local=self.local)
            pk2=self.getSnippet(self.getURL2,fileNamePrefix='py2_',local=self.local)
            self.py2Execute(pk2,fileNamePrefix='py2_',local=self.local)
            time.sleep(self.interval)
