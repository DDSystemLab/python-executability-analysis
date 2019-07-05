import requests
import json
import subprocess
import time
import os
import ast

class pySnippetEvaluator():
    def __init__(self,getURL3,postURL3,getURL2,postURL2,interval=0.1,timeout=10):
        self.getURL3=getURL3
        self.postURL3=postURL3
        self.getURL2=getURL2
        self.postURL2=postURL2
        self.interval=interval
        self.timeout=timeout #Default 10 seconds

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

    def importParser(self,snippet):
        import_string=snippet
        modules=[]
        for node in ast.iter_child_nodes(ast.parse(import_string)):
            if isinstance(node, ast.ImportFrom):
                if not node.names[0].asname:  # excluding the 'as' part of import
                    modules.append(node.module)
            elif isinstance(node, ast.Import): # excluding the 'as' part of import
                if not node.names[0].asname:
                    modules.append(node.names[0].name)
        return modules

    def error2Code(self,errorType):
        statusCode={
            'Success':0,
            'UnkownError':1,
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
            'TimeoutExpired':64
        }
        try:
            code=statusCode[errorType]
            return(code)
        except:
            return 1

    def getSnippet(self,getURL,fileNamePrefix=''):
        response=json.loads(requests.request('GET', getURL).text)
        snippetID=response['pk']
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        with open(pyFileName,'a') as pyFile:
            pyFile.write(self.snippetParser(response['content']))
        pyFile.close()
        return snippetID

    def py3Execute(self,snippetID,fileNamePrefix=''):
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        result={}
        result['pk']=snippetID
        startTime=time.time()
        proc=subprocess.Popen(['python3',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
        except subprocess.TimeoutExpired:
            payload="pk=%s&status_code=%s&result=%s&execution_time=%s"%(str(result['pk']),str(64),'TimeoutExpired',str(self.timeout))
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request('POST', self.postURL3, headers = headers, data = payload, allow_redirects=False)
            return
        endTime=time.time()
        executionResult=executionResult[0].decode('utf-8')
        returnCode=proc.returncode
        executionTime=endTime-startTime
        #Remove py file after evaluation
        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if(returnCode==0): #success
            result['status_code']=0
            result['result']=executionResult
            result['execution_time']=executionTime
        else:
            errorType=executionResult.splitlines()[-1].split(':')[0]
            # if module installation needed
            if(errorType=='ImportError' or errorType=='ModuleNotFoundError'):
                moduleName=executionResult.splitlines()[-1].split(':')[1].split("'")[1]
                procpip=subprocess.Popen(['pip3','install',moduleName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                pipResult=procpip.communicate()[0].decode('utf-8')#make Popen blocking and fetch the result
                if('Successfully installed '+moduleName in pipResult):
                    return result['pk'] #Post is not performed. This snippet will be evaluated later.               
            result['status_code']=self.error2Code(errorType)
            result['result']=executionResult
            result['execution_time']=executionTime
        #post results
        payload="pk=%s&status_code=%s&result=%s&execution_time=%s"%(str(result['pk']),str(result['status_code']),result['result'],str(result['execution_time']))
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request('POST', self.postURL3, headers = headers, data = payload.encode('utf-8'), allow_redirects=False)

    def py2Execute(self,snippetID,fileNamePrefix=''):
        pyFileName=fileNamePrefix+str(snippetID)+'.py'
        result={}
        result['pk']=snippetID
        startTime=time.time()
        proc=subprocess.Popen(['python2',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            executionResult=proc.communicate(timeout=self.timeout) #make Popen blocking
        except subprocess.TimeoutExpired:
            payload="pk=%s&status_code=%s&result=%s&execution_time=%s"%(str(result['pk']),str(64),'TimeoutExpired',str(self.timeout))
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request('POST', self.postURL2, headers = headers, data = payload, allow_redirects=False)
            return
        endTime=time.time()
        executionResult=executionResult[0].decode('utf-8')
        returnCode=proc.returncode
        executionTime=endTime-startTime
        #Remove py file after evaluation
        rmPyFile=subprocess.Popen(['rm','-rf',pyFileName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if(returnCode==0): #success
            result['status_code']=0
            result['result']=executionResult
            result['execution_time']=executionTime
        else:
            errorType=executionResult.splitlines()[-1].split(':')[0]
            # if module installation needed
            if(errorType=='ImportError' or errorType=='ModuleNotFoundError'):
                moduleName=executionResult.splitlines()[-1].split(':')[1].split("No module named")[-1]
                procpip=subprocess.Popen(['pip2','install',moduleName],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                pipResult=procpip.communicate()[0].decode('utf-8')#make Popen blocking and fetch the result
                if('Successfully installed '+moduleName in pipResult):
                    return result['pk'] #Post is not performed. This snippet will be evaluated later.               
            result['status_code']=self.error2Code(errorType)
            result['result']=executionResult
            result['execution_time']=executionTime
        #post results
        payload="pk=%s&status_code=%s&result=%s&execution_time=%s"%(str(result['pk']),str(result['status_code']),result['result'],str(result['execution_time']))
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request('POST', self.postURL2, headers = headers, data = payload.encode('utf-8'), allow_redirects=False)

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
            pk3=self.getSnippet(self.getURL3,fileNamePrefix='py3_')
            self.py3Execute(pk3,fileNamePrefix='py3_')
            pk2=self.getSnippet(self.getURL2,fileNamePrefix='py2_')
            self.py2Execute(pk2,fileNamePrefix='py2_')
            time.sleep(self.interval)

def main():
    GETURL3=os.environ.get('GETURL3')
    POSTURL3=os.environ.get('POSTURL3')
    GETURL2=os.environ.get('GETURL2')
    POSTURL2=os.environ.get('POSTURL2')
    if(GETURL3==None or POSTURL3==None or GETURL2==None or POSTURL2==None):
        print('Can not find required environment variables')
        return
    INTERVAL=os.environ.get('INTERVAL')
    if(INTERVAL==None):
        INTERVAL=0.1
    else:
        INTERVAL=float(INTERVAL)
    TIMEOUT=os.environ.get('TIMEOUT')
    if(TIMEOUT==None):
        TIMEOUT=10
    else:
        TIMEOUT=int(TIMEOUT)
    eva=pySnippetEvaluator(GETURL3,POSTURL3,GETURL2,POSTURL2,INTERVAL,TIMEOUT)
    eva.py3py2Evaluate()

if __name__=='__main__':
    main()