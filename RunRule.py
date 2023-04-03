#!/usr/bin/env python
# coding: utf-8

# In[37]:


from lxml import etree
import re
import strip

filename = "cse.xml"

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


# In[38]:


def ruleDecode(element):
    global sqltext, mfilter, ftype, batts, orifilter, zeus, swversion, sources, testmodedesc
    global repact, defcomp, rulename, testmode, shorttest_filter, diagdtfrom, diagdtto, proddtfrom, proddtto, ecutext


    if element.tag == "rule":
        rulename = element.attrib.get('name')
        print(element.tag)

    
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
            print(testmodedesc)
            
    if element.tag ==  "repact":
            repact = element.text
            print(repact)

    if element.tag ==  "defcomp":
            defcomp = element.text
            print(defcomp)
                    
    if element.tag ==  "diagdtfrom":
            diagdtfrom = "(diag_start_ts "+element.text+")"

    if element.tag == "diagdtto":
            diagdtto = "(diag_end_ts "+element.text+")"

    if element.tag ==  "proddtfrom":
            proddtfrom = "(prod_start_ts "+element.text+")"

    if element.tag == "proddtto":
            proddtto = "(prod_end_ts "+element.text+")"

    if element.tag ==  "shorttest":
            shorttest_filter = '(df_dtc.process_run_num'+element.text+')'
                    
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

            tokenList = str.replace(' ', '').replace('\n', '').replace('\t', '').replace('not', '~').replace('and', '&').replace('or', '|').split('#')

            for token in tokenList:
                
                if token != '':
                    tokenPartikelList = token.split(".")
                    
                    if len(tokenPartikelList) == 0:
                        print("Fehler")
                    if len(tokenPartikelList) == 1:
                        mfilter = mfilter + token
                    if len(tokenPartikelList) == 2:
                        mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and fault_nm = \''+tokenPartikelList[1]+'\') '
                    if len(tokenPartikelList) == 3:
                        status = tokenPartikelList[2]
                        print(tokenPartikelList)

                        mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and fault_nm = \''+tokenPartikelList[1]+'\''
                        mfilter = mfilter + ' and status = true'
                        mfilter = mfilter + ' and status = true ) '



# In[39]:


def ecuListDecode(node):

    global ecutext
    swversions = ""
    hwversions = ""
    swver = ""
    hwver = ""
    dtcs = ""
    ecu = ""
    
    ecutext=""
    
    for elem in root.iter("eculist"):

        for i in elem.iter("ecu"):

            ecu = "(ecu_nm like "+i.attrib.get('name')
            swversions = elem.findall( "ecu/ecu_sw_version_txt")[0].text
            print(swversions)
            hwversions = elem.findall( "ecu/ecu_hw_version_txt")[0].text
            print(hwversions)
            dtcs = elem.findall( "ecu/ecu_dtc_count")[0].text
        
            if swversions != None:
                swversionList = swversions.split(",")
                print(swversionList)
                if len(swversionList)==1:
                        swver = '( ecu_sw_version_txt like \''+ swversionList[0].strip()+'\') '
                if len(swversionList)>1:
                    swver = " ("
                    for n in range(0, len(swversionList)):
                        swver = swver + '( ecu_sw_version_txt like \''+ swversionList[n].strip()+'\') '
                        if n < len(swversionList)-1:
                            swver = swver+ " or "
                            
                    swver = swver+ ")\n"
            print(swver)   
            
            if hwversions != None:
                hwversionList = hwversions.split(",")
                print(hwversionList)
                if len(hwversionList)==1:
                    swver = '( ecu_sw_version_txt like \''+ hwversionList[0].strip()+'\') '
                    if len(hwversionList)>1:
                        hwver = " ("
                        for n in range(0, len(hwversionList)):
                            hwver = hwver + '( ecu_sw_version_txt like \''+ hwversionList[n].strip()+'\') '
                            if n < len(swversionList)-1:
                                hwver = hwver+ " or "

                hwver = hwver+ ")\n"
           
            ecutext = ecutext+ecu+")"


# In[40]:


simpleElementList = ["rule", "testmode", "sourcesystem","shorttest", "testdescription","battery"]
simpleElementList = simpleElementList+ ["zeus", "shortdesc", "repact","defcomp","filter"]
simpleElementList = simpleElementList+ ["diagdtfrom","diagdtto","proddtfrom","proddtto"]

ecuElemntList = ["eculist"]

tree = etree.parse(filename)
root = tree.getroot()

root.tag, root.attrib
[elem.tag for elem in root.iter("*")]


for element in root.iter("*"):
    if element.tag in simpleElementList:
        ruleDecode(element)
    if element.tag in ecuElemntList:
        ecuListDecode(element)
  
sqltext = "select * from input_ms where \n "
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
print(sqltext)

