from lxml import etree
import re

filename = "C:\\AnacondaProjects\\cse.xml"

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
shorttest_filter=''

def ruleDecode(node):
    global sqltext, mfilter, ftype, batts, orifilter, zeus, swversion, sources, testmodedesc
    global repact, defcomp, rulename, testmode, shorttest_filter

    
    print(element)
            
    match element.tag:
    
        case "rule":
            rulename = element.attrib
            print(rulename)
    
        case "battery":
            text = element.text
            batteryList = text.replace(' ','').split(",")
            
            if len(batteryList)==1:
                    batts = 'and ( battery_nm like \''+ batteryList[0]+'\') '
            else:
                batts = " and ("
                for n in range(0, len(batteryList)):
                    batts = batts + '( battery_nm like \''+ batteryList[n]+'\') '
                    if n < len(batteryList)-1:
                        batts = batts+ " or "
                        
                batts = batts+ " )\n" 
            print(batts)            
            

        case "testmode":
            testmode = element.text
            print(testmode)

        case "testdescription":
            testmodedesc = element.text
            print(testmodedesc)
            
        case "repact":
            repact = element.text
            print(repact)

        case "defcomp":
            defcomp = element.text
            print(defcomp)
                    
        case "diagfrom":
            txt = element.text
            sqltext = sqltext+" and diag_start_ts "+diagdt.text

        case "diagfrom":
            txt = element.text
            sqltext = sqltext+" and diag_start_ts "+diagdt.text

        case "proddtfrom":
            txt = element.text
            sqltext = sqltext+" and diag_start_ts "+diagdt.text

        case "proddtto":
            txt = element.text
            sqltext = sqltext+" and diag_start_ts "+diagdt.text
            
        case "shorttest":
            comperatorList =['==', '<', '>', '<=', '>=']
            for comperator in comperatorList:
                if comperator in element.text:
                    shorttest_filter = 'and ((df_dtc.process_run_num'+element.text+') '
                    
        case "sourcesystem":  
            text = element.text
            sourceSystemList = text.replace(' ','').split(",")
            
            if len(sourceSystemList)==1:
                    sources = 'and (source_system_nm like \''+ sourceSystemList[0]+'\') '
            else:
                sources = " and ("
                for n in range(0, len(sourceSystemList)):
                    sources = sources + '(source_system_nm like \''+ sourceSystemList[n]+'\') '
                    if n < len(sourceSystemList)-1:
                        sources = sources+ " or "
                        
                sources = sources+ " )\n" 
            print(sources)
         
        case "filter":  
            str= element.text
            mfilter = ""
            status = ""

            tokenList = str.replace(' ', '').replace('\n', '').replace('\t', '').replace('not', '~').replace('and', '&').replace('or', '|').split('#')

            for token in tokenList:
                
                if token != '':
                    tokenPartikelList = token.split(".")
                    match len(tokenPartikelList):
                        case 0:
                            print("Fehler")
                        case 1:
                            mfilter = mfilter + token
                        case 2:
                            mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and fault_nm = \''+tokenPartikelList[1]+'\') '
                        case 3:
                            status = tokenPartikelList[2]
                            print(tokenPartikelList)

                            mfilter = mfilter + ' ( ecu_nm = \''+tokenPartikelList[0]+'\' and fault_nm = \''+tokenPartikelList[1]+'\''
                            mfilter = mfilter + ' and status = true'
                            mfilter = mfilter + ' and status = true ) '




def ecuListDecode(node):
    for elem in root.iter("eculist"):
        print("Item: ", elem.text)
        for i in elem.iter("ecu"):
            print ("Sub:", i.tag)
            print ("Name:", i.attrib)
            for sw in elem.iter("ecu_sw_version_txt"):
                print ("sw:", sw.text)
            for hw in elem.iter("ecu_hw_version_txt"):
                print ("hw:", hw.text)
            for dtc in elem.iter("ecu_dtc_count"):
                print ("dtc:", dtc.text)


simpleElementList = ["testmode", "sourcesystem","shorttest", "testdescription","battery", "zeus", "shortdesc", "repact","defcomp","filter"]
ecuElemntList = ["eculist"]

tree = etree.parse(filename)
root = tree.getroot()

root.tag, root.attrib
[elem.tag for elem in root.iter("*")]

print("=====================================================")
for element in root.iter("*"):
    if element.tag in simpleElementList:
        ruleDecode(element)
    if element.tag in ecuElemntList:
        ecuListDecode(element)
  
sqltext = "select * from input_ms where \n"
sqltext = 
sqltext = sqltext + sources+"\n"
sqltext = sqltext + mfilter+"\n"

sqltext = sqltext + "\n\n"+shorttest_filter+"\n"
  
print("==============================================")
print("filename: \t",filename)
print("==============================================")
print("RuleName: \t",rulename)
print("TestMode: \t", testmode, testmodedesc)
print("ShortDesc:\t", shortdesc)
print("DefComp:  \t", defcomp)
print("RepAct:   \t", repact)
print("Zeus:     \t",zeus)
       
print(">", sqltext)
