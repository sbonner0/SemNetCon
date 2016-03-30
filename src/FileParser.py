#Copyright 2016 John Brennan and Stephen Bonner
#This file is part of SEMNETCON.

#The Semantic Enabled Python Tool For The Construction Of Complex 
#Networks From Disperse Data Sources (SEMNETCON) 
#is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#SEMNETCON is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with SEMNETCON.  If not, see <http://www.gnu.org/licenses/>.
#Contact j.d.brennan@durham.ac.uk or s.a.r.bonner@durham.ac.uk

import sys, json, csv, xlrd, traceback, os, json
import networkx as nx
import xml.etree.ElementTree as et
from lxml import etree
try:
    import jq
    JQ = True
    print "Using JQ"
except:
    from jsonpath_rw import parse
    JQ = False
    print "Using jsonpth"

# Set consistent encoding across all data sources
reload(sys)
sys.setdefaultencoding('utf8')

# Parse JSON Function ----------------------------------------------------------------------------------------
# Convert JSON query into the required format
def jsonPathFix(simple_path):
    """
    Function to add wild card expressions to JSON path
    when using jsonpath_rw
    """
    if simple_path != "None":
        full_path = "$"
        path_array = simple_path.replace("[]", "").split(".")
        for element in path_array:
            full_path = full_path + element + "[*]."
        full_path = full_path.strip(".")
        return full_path
    else:
        return "None"

def parseJSON(decodedInfo, G):
    """
    Function to read JSON data.
    Returns: Graph object extracted from data.
    """
    nodeData = []
    nodeAttr = []
    edgeToData = []
    edgeFromData = []
    edgeAttr = []
    if not JQ:
        for i in {2, 4, 5}:
            decodedInfo[i] = jsonPathFix(decodedInfo[i])

        
    # Create metamap of decodedInfo for readability.
    metaMap = {'name':decodedInfo[0],
            'location':decodedInfo[1],
            'nodeinfo':decodedInfo[2],
            'nodeattr':decodedInfo[3],
            'edgefrom':decodedInfo[4],
            'edgeto':decodedInfo[5],
            'edgeattr':decodedInfo[6]}
   
       # Check for existance of attributes, and create temp array if they exist.
    if metaMap['nodeattr'] != "None":
        nodeAttrTemp = metaMap['nodeattr'].split(",")

    if metaMap['edgeattr'] != "None":
        edgeAttrTemp = metaMap['edgeattr'].split(",")

    if JQ:
        if metaMap['nodeinfo'] != "None":
            jqNode = jq.jq(metaMap['nodeinfo'])
        if metaMap['edgefrom'] != "None":
            jqEdgeFrom = jq.jq(metaMap['edgefrom'])
        if metaMap['edgeto'] != "None":
            jqEdgeTo = jq.jq(metaMap['edgeto'])
         
    try:
        with open(metaMap['location']) as jsonFile:
            for jsonLine in jsonFile:
                attr = {}
                edgeAttr = {}
                try:
                    jsonLine = json.loads(jsonLine)
                    # Ensure nodeinfo and nodeattr exists within the rdf -------------------------------------
                    if metaMap['nodeinfo'] != "None":
                        if JQ:
                            record = jqNode.transform(jsonLine)
                        else:
                            record = [match.value for match in parse(metaMap['nodeinfo']).find(jsonLine)][0]
                        if record != "":
                            n = str(record)
                            record = "";
                        if metaMap['nodeattr'] != "None":
                            for j in range(0,len(nodeAttrTemp)):
                                try:
                                    if JQ:
                                        record = jq.jq(nodeAttrTemp[j].split(":")[1]).transform(jsonLine)
                                    else:
                                        record = [match.value for match in parse(jsonPathFix(nodeAttrTemp[j].split(":")[1])).find(jsonLine)][0]
                                    if record != "":
                                        attr.update({str(nodeAttrTemp[j].split(":")[0]) : str(record)})
                                        record = "";
                                except (ValueError, IndexError):
                                    attr.update({str(nodeAttrTemp[j].split(":")[0]) : 'None'})
                        else:
                            attr = {'Attr':'None'}
                        #print n , " " , attr
                        G.add_node(n,attr_dict=attr)
                    
                    # Ensure edgefrom, edgeto and edgeattr exist within the rdf  -------------------------------------
                    if metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None":
                        # Extract edge from data from JSON and check is not null
                        try:
                            if JQ:
                                record = jqEdgeFrom.transform(jsonLine)
                            else:
                                record = [match.value for match in parse(metaMap['edgefrom']).find(jsonLine)][0]
                            if record != "":
                                f = str(record)
                                record = "";
                        except (ValueError, IndexError):
                            f = 'None'
                        # Extract edge from data from JSON and check is not null
                        try:
                            if JQ:
                                record = jqEdgeTo.transform(jsonLine)
                            else:   
                                record = [match.value for match in parse(metaMap['edgeto']).find(jsonLine)][0]
                            if record != "":
                                t = str(record)
                                record = "";
                        except (ValueError, IndexError):
                            t = 'None'
                        
                        if metaMap['edgeattr'] != "None":
                            for j in range(0,len(edgeAttrTemp)):
                                try:
                                    if JQ:
                                        record = jq.jq(edgeAttrTemp[j].split(":")[1]).transform(jsonLine)
                                    else:
                                        record = [match.value for match in parse(jsonPathFix(edgeAttrTemp[j].split(":")[1])).find(jsonLine)][0]
                                    if record != "":
                                        attr.update({str(edgeAttrTemp[j].split(":")[0]) : str(record)})
                                        record = "";
                                except (ValueError, IndexError):
                                    attr.update({str(edgeAttrTemp[j].split(":")[0]) : 'None'})
                                    
                        G.add_edge(f, t, attr_dict=attr)
                except IndexError:
                    traceback.print_exc()
                    pass
    except Exception:
        traceback.print_exc()
    return G

# Parse XML Function ----------------------------------------------------------------------------------------
def parseXML(decodedInfo,G):
    """
    Function to read XML data.
    Returns: Graph object extracted from data.
    """
    nodeData = []
    nodeAttr = []
    edgeToData = []
    edgeFromData = []
    edgeAttr = []
    # Create metamap of decodedInfo for readability.
    metaMap = {'name':decodedInfo[0],
            'location':decodedInfo[1],
            'nodeinfo':decodedInfo[2],
            'nodeattr':decodedInfo[3],
            'edgefrom':decodedInfo[4],
            'edgeto':decodedInfo[5],
            'edgeattr':decodedInfo[6]}
   
       # Check for existance of attributes, and create temp array if they exist.
    if metaMap['nodeattr'] != "None":
        nodeAttrTemp = metaMap['nodeattr'].split(",")

    if metaMap['edgeattr'] != "None":
        edgeAttrTemp = metaMap['edgeattr'].split(",")
    
    try:
        with open(metaMap['location']) as xmlFile:
            tree = etree.parse(xmlFile)
            
            # Ensure nodeinfo and nodeattr exists within the rdf -------------------------------------
            if metaMap['nodeinfo'] != "None" and metaMap['nodeattr'] != "None":
                for record in tree.xpath(metaMap['nodeinfo']):
                    if record != "":
                        nodeData.append(str(record))
                        
                for j in range(0,len(nodeAttrTemp)):
                    for record in tree.xpath(nodeAttrTemp[j].split(":")[1]):
                        if record != "":
                            nodeAttr.append(str(record))
                    # Test if nodeData and nodeAttr are the same length
                    if len(nodeAttr) == len(nodeData):
                        for n, a in zip(nodeData, nodeAttr):
                            attr = {str(nodeAttrTemp[j].split(":")[0]) : a}
                            G.add_node(n,attr)
                    else:
                        print "Node data and attributes are not the same size. Creating the network here would result is mismatch of nodes and attributes"
                    nodeAttr = []
                    
            # Ensure nodeinfo exists within the rdf -------------------------------------
            elif metaMap['nodeinfo'] != "None":
                # Extract edge from data from XML and check is not null
                for record in tree.xpath(metaMap['nodeinfo']):
                    if record != "":
                        nodeData.append(str(record))
                # Bulk add all nodes to the graph object         
                G.add_nodes_from(nodeData)
                
            # Ensure edgefrom, edgeto and edgeattr exist within the rdf  -------------------------------------
            if metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None" and metaMap['edgeattr'] != "None":
                 # Extract edge from data from XML and check is not null
                for record in tree.xpath(metaMap['edgefrom']):
                    if record != "":
                        edgeFromData.append(str(record))
                # Extract edge from data from XML and check is not null        
                for record in tree.xpath(metaMap['edgeto']):
                    if record != "":
                        edgeToData.append(str(record))
                
                for j in range(0,len(edgeAttrTemp)):
                    for record in tree.xpath(edgeAttrTemp[j].split(":")[1]):
                        if record != "":
                            edgeAttr.append(str(record))
                    # Test if edgeAttr and edgeFromData are the same length
                    if len(edgeAttr) == len(edgeFromData):
                        for f, t, a in zip(edgeFromData, edgeToData, edgeAttr):
                            attr = {str(edgeAttrTemp[j].split(":")[0]) : a}
                            G.add_edge(f, t, attr_dict=attr)
                    else:
                        print "Edge data and attributes are not the same size. Creating the network here would result is mismatch of nodes and attributes"
                    edgeAttr = []
                        
            # Ensure edgefrom and edgeto exist within the rdf -------------------------------------
            elif metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None":
                # Extract edge from data from XML and check is not null
                for record in tree.xpath(metaMap['edgefrom']):
                    if record != "":
                        edgeFromData.append(str(record))
                # Extract edge from data from XML and check is not null        
                for record in tree.xpath(metaMap['edgeto']):
                    if record != "":
                        edgeToData.append(str(record))
                # Zip edgeTo and edgeFrom togther and create graph object
                for f, t in zip(edgeFromData, edgeToData):
                    G.add_edge(f, t)
            
    except Exception:
        traceback.print_exc()

    return G
   
# Parse CSV Function ----------------------------------------------------------------------------------------        
def parseCSV(decodedInfo,G):
    """
    Function to read CSV data.
    Returns: Graph object extracted from data.
    """
    # Create metamap of decodedInfo for readability.
    metaMap = {'name':decodedInfo[0],
            'location':decodedInfo[1],
            'nodeinfo':decodedInfo[2],
            'nodeattr':decodedInfo[3],
            'edgefrom':decodedInfo[4],
            'edgeto':decodedInfo[5],
            'edgeattr':decodedInfo[6],
            'dlim':decodedInfo[7],
            'sl':decodedInfo[8]}

    # Deal with tab demlimiters
    if decodedInfo[7] == 't':
        metaMap['dlim'] = '\t'

    # Check for existance of attributes, and create temp array if they exist.
    if metaMap['nodeattr'] != "None":
        nodeAttrTemp = metaMap['nodeattr'].split(",")

    if metaMap['edgeattr'] != "None":
        edgeAttrTemp = metaMap['edgeattr'].split(",")

    # Open the required file
    try:
        with open(metaMap['location'], 'rb') as csvfile:
            dataReader = csv.reader(csvfile, delimiter=metaMap['dlim'])

            # Advance to starting line
            for i in range(int(metaMap['sl'])): next(dataReader)

            for line in dataReader:
                # Ensure nodeinfo and nodeattr exist within the rdf.
                if metaMap['nodeinfo'] != "None" and metaMap['nodeattr'] != "None":
                     # Check no empty strings exist before adding nodes to graph.
                    if line[int(metaMap['nodeinfo'])] != "":
                        # Create dictionary of attributes to be addded to the graph.
                        for j in range(0,len(nodeAttrTemp)):
                            attr = {str(nodeAttrTemp[j].split(":")[0]) : line[int(nodeAttrTemp[j].split(":")[1])]}
                            # Add data
                            G.add_node(line[int(metaMap['nodeinfo'])], attr)
                # Ensure nodeinfo exists within the rdf.
                elif metaMap['nodeinfo'] != "None":
                    # Check no empty strings exist before adding nodes to graph.
                    if line[int(metaMap['nodeinfo'])] != "":
                        # Add data
                        G.add_node(line[int(metaMap['nodeinfo'])])

                # Ensure edgefrom, edgeto and edgeattr exist within the rdf.
                if metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None" and metaMap['edgeattr'] != "None":
                    # Check no empty strings exist before adding edges to graph.
                    if line[int(metaMap['edgefrom'])] != "" or line[int(metaMap['edgeto'])] != "":
                        # Create dictionary of attributes to be addded to the graph.
                        for j in range(0,len(edgeAttrTemp)):
                            attr = {str(edgeAttrTemp[j].split(":")[0]) : line[int(edgeAttrTemp[j].split(":")[1])]}
                            # Add data
                            G.add_edge(line[int(metaMap['edgefrom'])], line[int(metaMap['edgeto'])], attr_dict=attr)
                # Ensure edgefrom and edgeto exist within the rdf.
                elif metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None":
                # Check no empty strings exist before adding edges to graph.
                    if line[int(metaMap['edgefrom'])] != "" or line[int(metaMap['edgeto'])] != "":
                        # Add data
                        G.add_edge(line[int(metaMap['edgefrom'])], line[int(metaMap['edgeto'])])
    except:
        traceback.print_exc()
        
    return G

# Parse EXCEL Function ----------------------------------------------------------------------------------------
def parseEXCEL(decodedInfo,G):
    """
    Function to read EXCEL data.
    Returns: Graph object extracted from data.
    """
    # Create metamap of decodedInfo for readability.
    metaMap = {'name':decodedInfo[0],
            'location':decodedInfo[1],
            'nodeinfo':decodedInfo[2],
            'nodeattr':decodedInfo[3],
            'edgefrom':decodedInfo[4],
            'edgeto':decodedInfo[5],
            'edgeattr':decodedInfo[6],
            'dlim':decodedInfo[7],
            'sl':decodedInfo[8]}

    # Check for existance of attributes, and create temp array if they exist.
    if metaMap['nodeattr'] != "None":
        nodeAttrTemp = metaMap['nodeattr'].split(",")
    if metaMap['edgeattr'] != "None":
        edgeAttrTemp = metaMap['edgeattr'].split(",")

    try:
        # Open required Excel fie.
        workbook = xlrd.open_workbook(metaMap['location'])
        # Open first workbook.
        worksheet = workbook.sheet_by_index(0)

        # Loop through Excel workbook starting from required line.
        for rownums in range(int(metaMap['sl']), worksheet.nrows):
            # Ensure nodeinfo and nodeattr exist within the rdf.
            if metaMap['nodeinfo'] != "None" and metaMap['nodeattr'] != "None":
                # Check no empty strings exist before adding nodes to graph.
                if worksheet.row_values(rownums)[int(metaMap['nodeinfo'])] != "":
                    # Create dictionary of attributes to be addded to the graph.
                    for j in range(0,len(nodeAttrTemp)):
                        attr = {str(nodeAttrTemp[j].split(":")[0]) : worksheet.row_values(rownums)[int(nodeAttrTemp[j].split(":")[1])]}
                        # Add data.
                        G.add_node(worksheet.row_values(rownums)[int(metaMap['nodeinfo'])], attr)
            # Ensure nodeinfo exists within the rdf.
            elif metaMap['nodeinfo'] != "None":
                #Check no empty strings exist before adding nodes to graph.
                if worksheet.row_values(rownums)[int(metaMap['nodeinfo'])] != "":
                    # Add data.
                    G.add_node(worksheet.row_values(rownums)[int(metaMap['nodeinfo'])])

            # Ensure edgefrom, edgeto and edgeattr exist within the rdf.
            if metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None" and metaMap['edgeattr'] != "None":
                #Check no empty strings exist before adding edges to graph.
                if worksheet.row_values(rownums)[int(metaMap['edgefrom'])] != "" or worksheet.row_values(rownums)[int(metaMap['edgeto'])] != "":
                    # Create dictionary of attributes to be addded to the graph.
                    for j in range(0,len(edgeAttrTemp)):
                        attr = {str(edgeAttrTemp[j].split(":")[0]) : worksheet.row_values(rownums)[int(edgeAttrTemp[j].split(":")[1])]}
                        # Add data.
                        G.add_edge(worksheet.row_values(rownums)[int(metaMap['edgefrom'])], worksheet.row_values(rownums)[int(metaMap['edgeto'])], attr_dict=attr)
            # Ensure edgefrom and edgeto exist within the rdf.
            elif metaMap['edgefrom'] != "None" and metaMap['edgeto'] != "None":
                # Check no empty strings exist before adding edges to graph.
                if worksheet.row_values(rownums)[int(metaMap['edgefrom'])] != "" or worksheet.row_values(rownums)[int(metaMap['edgeto'])] != "":
                # Add data.
                    G.add_edge(worksheet.row_values(rownums)[int(metaMap['edgefrom'])], worksheet.row_values(rownums)[int(metaMap['edgeto'])])
    except:
        traceback.print_exc()

    return G