#!/usr/bin/env python
# coding: utf-8

# In[1]:


from lxml import etree
import re
import strip
from databricks import sql
import os
import sys
import csv
from pandas import DataFrame
from sql_formatter.core import format_sql

#filename = "cse.xml"

ftype = ""          #will contain the filter logic of the rule
sqltext = ""        #will contain the complete sql command
mfilter = ""
batts = ""          #will contain the query restriction due to the battery types
sources = ""        #will contain the query restriction due to the source system (or connection)

rulename = ""       #will contain the zeus informations -> for excel only
zeus = ""           #will contain the zeus informations -> for excel only
shortdesc = ""      #will contain the short description informations -> for excel only
testmode = ""       #will contain the testmode informations -> for excel only
testmodedesc = ""   #will contain the testmode description -> for excel only
repact = ""         #will contain the repair action -> for excel only
defcomp = ""        #will contain the defective component -> for excel only
shorttest_filter=""
diagdtfrom = ""
diagdtto = ""
proddtfrom = ""
proddtto = ""
ecutext=""
filename = ""


filename = sys.argv[1]
doSql = True


# In[2]:


def ruleDecode(element):
    global sqltext, mfilter, ftype, batts, orifilter, zeus, swversion, sources, testmodedesc
    global repact, defcomp, rulename, testmode, shorttest_filter, diagdtfrom, diagdtto, proddtfrom, proddtto, ecutext


    if element.tag == "rule":
        rulename = element.attrib.get('name')

    
    if element.tag ==  "battery":
        text = element.text

        batteryList = text.replace(' ','').split(",")
        
        if len(batteryList)==1:
                batts = '( battery_nm like \''+ batteryList[0]+'\') '
        else:
            batts = "("
            for n in range(0, len(batteryList)):
                batts = batts + '( battery_nm like \''+ batteryList[n]+'\') '
                if n < len(batteryList)-1:
                    batts = batts+ " or "
                    
            batts = batts+ " )" 

    if element.tag ==  "testmode":
        testmode = element.text


    if element.tag ==  "testdescription":
            testmodedesc = element.text
            
    if element.tag ==  "repact":
            repact = element.text

    if element.tag ==  "defcomp":
            defcomp = element.text
       
    if element.tag ==  "diagdtfrom":
            diagdtfrom = "(diag_start_Ts "+element.text+")"

    if element.tag == "diagdtto":
            diagdtto = "(diag_start_Ts "+element.text+")"

    if element.tag ==  "proddtfrom":
            proddtfrom = "(prod_dt "+element.text+")"

    if element.tag == "proddtto":
            proddtto = "(prod_dt "+element.text+")"

    if element.tag ==  "shorttest":
            shorttest_filter = '(process_run_num'+element.text+')'
                    
    if element.tag ==  "sourcesystem":  
            text = element.text
            sourceSystemList = text.replace(' ','').split(",")
            
            if len(sourceSystemList)==1:
                    sources = '(source_system_nm like \''+ sourceSystemList[0]+'\')'
            else:
                sources = "("
                for n in range(0, len(sourceSystemList)):
                    sources = sources + '(source_system_nm like \''+ sourceSystemList[n]+'\')'
                    if n < len(sourceSystemList)-1:
                        sources = sources+ " or "
                        
                sources = sources+ ")" 

         
    if element.tag == "filter":  
            str= element.text
            mfilter = ""
            status = ""

            tokenList = str.replace('\n', '').replace('\t', '').split('#')

            for token in tokenList:
                
                if token != '':
                    tokenPartikelList = token.split(".")
                    
                    if len(tokenPartikelList) == 0:
                        print("Fehler")
                    if len(tokenPartikelList) == 1:
                        mfilter = mfilter + token
                    if len(tokenPartikelList) == 2:
                        mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and dtcs like \'%'+tokenPartikelList[1]+'%\') '
                    if len(tokenPartikelList) == 3:
                        status = tokenPartikelList[2]
                        #print(tokenPartikelList)

                        mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and fault_nm = \'%'+tokenPartikelList[1]+'\'%'
                        mfilter = mfilter + ' and status = true'
                        mfilter = mfilter + ' and status = true ) '



# In[3]:


def buildVersion( version, type):
    versionText = "("
    versionList = version.split(",")
    numElements = len(versionList)
    
    for i in range(numElements):
        if type == 0:
            versionText =  versionText+ "ecu_sw_version_txt like '%" + versionList[i]+ "%'"
        if type == 1:
            versionText =  versionText+ "ecu_hw_version_txt like '%" + versionList[i]+ "%'"
        if i < len(versionList)-1:
            versionText = versionText+ " or "
            
    versionText = versionText+")"

    return versionText


# In[4]:


def ecuListDecode(node):

    global ecutext
    swversions = ""
    hwversions = ""
    swver = ""
    hwver = ""
    dtcs = ""
    ecu = ""
    
    ecutext="("
    
    for elem in root.iter("eculist"):

        for i in range(len(elem)):
            ecu = elem[i].attrib.get('name')
            swversions = elem.findall( "ecu/ecu_sw_version_txt")[0].text
            hwversions = elem.findall( "ecu/ecu_hw_version_txt")[0].text
            dtcs = elem.findall( "ecu/ecu_dtc_count")[0].text
        
            #print("Ecu-name: ", ecu)
        
            ecutext = ecutext+ "(ecu_nm like '%"+ecu+"%'"
            if swversions != None:
                ecutext = ecutext+ "and "+ buildVersion(swversions,0)
    
            if hwversions != None:
                ecutext = ecutext+ "and "+buildVersion(hwversions,1)        
            if dtcs !=None:
                ecutext = ecutext +" and (dtc"+dtcs+")\n"
            
            ecutext = ecutext+")"
            if i < len(elem)-1:
                ecutext = ecutext+" or "
        
    ecutext = ecutext+")\n"



# In[5]:


simpleElementList = ["rule", "testmode", "sourcesystem","shorttest", "testdescription","battery"]
simpleElementList = simpleElementList+ ["zeus", "shortdesc", "repact","defcomp","filter"]
simpleElementList = simpleElementList+ ["diagdtfrom","diagdtto","proddtfrom","proddtto"]

ecuElemntList = ["eculist"]

if os.path.exists(filename) != True:
	print ("File: "+filename+" does not exists")
	sys.exit()

tree = etree.parse(filename)
root = tree.getroot()

root.tag, root.attrib
[elem.tag for elem in root.iter("*")]


for element in root.iter("*"):
    if element.tag in simpleElementList:
        ruleDecode(element)
    if element.tag in ecuElemntList:
        ecuListDecode(element)

sqltext = "select * from dev_mg.input_ms where \n "

sqltext = sqltext + batts+"\n"

sqltext = sqltext + " and "+ ecutext+"\n"

if sources != "":
    sqltext = sqltext + " and "+sources+"\n"
    
if shorttest_filter != "":
    sqltext = sqltext + " and "+shorttest_filter+"\n"
    
if diagdtfrom != "":
    sqltext = sqltext + " and "+ diagdtfrom+"\n"  
    
if diagdtto != "":
    sqltext = sqltext + " and "+ diagdtto+"\n"
    
if proddtfrom != "":
    sqltext = sqltext + " and "+ proddtfrom+"\n"
      
if diagdtto != "":
    sqltext = sqltext + " and "+ diagdtto+"\n"
    

sqltext = sqltext + "\n and "+mfilter+"\n"


sqltext = sqltext +"Limit 100\n"

print("==============================================")
print("filename: \t",filename)
print("==============================================")
print("RuleName: \t", rulename)
print("TestMode: \t", testmode, testmodedesc)
print("ShortDesc:\t", shortdesc)
print("DefComp:  \t", defcomp)
print("RepAct:   \t", repact)
print("Zeus:     \t", zeus)
print("---------------------------------------------")
print("SourceSystem: \t", sources)
print("Shorttest: \t", shorttest_filter)
print("DiagDate from: \t", diagdtfrom)
print("DiagDate to: \t", diagdtto)
print("ProdDate from: \t", proddtfrom)
print("ProdDate to: \t", proddtto)
print()
#print(format_sql(sqltext))


# In[6]:


if doSql:
    DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

    connection = sql.connect(server_hostname = DATABRICKS_SERVER_HOSTNAME,
                             http_path       = DATABRICKS_HTTP_PATH,
                             access_token    = DATABRICKS_TOKEN)



    with connection.cursor() as cursor:

        print ("---- Start Step 1")
        cursor.execute(sqltext)

        print ("---- Start Step 2")
        rows = cursor.fetchall()

        header = cursor.description

        print ("---- Start Step 3")

        df = DataFrame(rows)
        df.columns = [i[0] for i in header]

        print("---------------------------")

        excelfilename = filename.rsplit('.', 1)[0]+".xlsx"
        df.to_excel(excelfilename, sheet_name="Fehlerbilder", index=False)
        
        print("Excel-File ",excelfilename," created")

    cursor.close()
    connection.close()

print ("--- ENDE")
