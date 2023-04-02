from lxml import etree
import re

ftype = ""
sqltext = ""
mfilter = ""
zeus = ""
swversion = ""


def ruleDecode(node):
    global sqltext, mfilter, ftype, batts, orifilter, zeus, swversion
    
    print(element)
            
    match element.tag:
        case "battery":
            batts = element.text
            sqltext = sqltext+" and battery_nm like '"+element.text+"'"

        case "shorttest":
            txt = element.text
            if not "<" in txt and not ">" in txt and not "=" in txt:
                txt = "="+txt
            sqltext = sqltext+" and process_run_num"+txt
            
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
            shorttest_filter=''
            comperatorList =['==', '<', '>', '<=', '>=']
            for comperator in comperatorList:
                if comperator in element.text:
                    shorttest_filter = 'and ((df_dtc.process_run_num'+element.text+') '
                    
        case "sourcesystem":  
            sourcesystem_filter=''
            text = element.text
            sourceSystemList = text.replace(' ','').split(",")

            for sourceSystem in sourceSystemList:
                sourcesystem_filter = sourcesystem_filter + 'and (source_system_nm like \''+ sourceSystem+'\') '    
                
            print(sourcesystem_filter) 
         
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


simpleElementList = ["testmode", "shorttest", "testdescription","battery", "zeus", "shortdesc", "repact","defcomp","filter"]
ecuElemntList = ["eculist"]

tree = etree.parse("C:\\AnacondaProjects\\cse.xml")
root = tree.getroot()

root.tag, root.attrib
[elem.tag for elem in root.iter("*")]

print("=====================================================")
for element in root.iter("*"):
    if element.tag in simpleElementList:
        ruleDecode(element)
    if element.tag in ecuElemntList:
        ecuListDecode(element)
        
print(">", sqltext)
