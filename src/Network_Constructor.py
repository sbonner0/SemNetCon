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

import rdflib, logging, neonx, sys, argparse, os.path
from rdflib import Graph
import FileParser as FP
import networkx as nx

logging.basicConfig(level=logging.DEBUG)

# Print Licence info
print "SEMNETCON Copyright (C) 2016 John Brennan and Stephen Bonner.\n\
This program comes with ABSOLUTELY NO WARRANTY.\n\
This is free software, and you are welcome to redistribute it\n\
under certain conditions."

# Create the Global Graph Object
global g 
g = Graph()

# Query RDF File--------------------------------------------------------------------------------------
def queryAll(fileName, fileType):
    """Function to query the rdf and extract the information from it needed to create the network.
    Returns: Data extracted from RDF as a list.
    """
    tempRowList = []
    dataList = []

    # Master query common across all filetypes
    query = g.query( 
        """SELECT ?name ?location ?nodeHasValue ?nodeAttr ?edgeHasValueFrom ?edgeHasValueTo ?edgeAttr WHERE { 
        ?s network:fileName ?name .
        ?s network:filePath ?location . 
        ?s network:fileType ?filetype .
        ?s network:node ?nodename .
        ?s network:edge ?edgename .
        ?nodename network:hasValue ?nodeHasValue .
        ?nodename network:nodeAttributes ?nodeAttr .
        ?edgename network:hasValueFrom ?edgeHasValueFrom .
        ?edgename network:hasValueTo ?edgeHasValueTo .
        ?edgename network:edgeAttributes ?edgeAttr . 
        
        FILTER (str(?name) = "%s")
        FILTER (str(?filetype) = "%s")
        }""" % (fileName,fileType))
        
    for row in query:
        for item in row:
            tempRowList.append(str(item))
        dataList.append(tempRowList)
        tempRowList = []

    # CSV Specific Query-----------------
    if fileType == "csv":
        for element in dataList:
            query = g.query( 
                """SELECT ?dlim ?sl WHERE { 
                ?s network:fileName ?name .
                ?s network:delimData ?dlim .
                ?s network:startingLine ?sl .
                
                FILTER (str(?name) = "%s")
                }""" % (element[0]))
                
            for row in query:
                for item in row:
                    element.append(str(item))
                    
    # JSON Specific Query-----------------
    elif fileType == "json":
        pass
    # Excel Specific Query----------------------
    elif fileType == "excel":
        for element in dataList:
            query = g.query( 
                """SELECT ?dlim ?sl WHERE { 
                ?s network:fileName ?name .
                ?s network:delimData ?dlim .
                ?s network:startingLine ?sl .
                
                FILTER (str(?name) = "%s")
                }""" % (element[0]))
                
            for row in query:
                for item in row:
                    element.append(str(item))
    # XML Specific Query-----------------------
    elif fileType == "xml":
        pass
        
    return dataList

# Main Function --------------------------------------------------------------------------------------
def main(rdfLocation, outputType):
    """Main function which parses the rdf graph then sends it to be queried.
    It uses the result from the queryAll function to call the required file parser.
    If multiple files are detected it will parse them all.
    Returns: Final Network output to file in a variety of common network file formats. 
    """
    files = []
    # Parse The RDF Graph Object by first checking if it is a file location or the file itself.
    if os.path.isfile(rdfLocation):
        g.parse(location=rdfLocation)
    else:
        g.parse(data=rdfLocation)
    
    # Specify Output File Type For graph Object
    outputFileType = outputType
    
    # Create NetworkX Graph object
    G = nx.MultiDiGraph()
    
    # Extract the file types from the rdf as this will be used to call a custom query for a certain filetype
    fileInfo = g.query("""SELECT ?name ?filetype WHERE { ?s network:fileType ?filetype .
                                                          ?s network:fileName ?name . }""")
                                                          
    # Loop through files contained within the dataset and issue relavent queries
    for element in fileInfo:
        # Extract the FileType and Name from the query result
        fileName = str(element[0])
        fileType = str(element[1])
        
        # Call XML functions
        if fileType == "xml":
            print "Found XML File"
            xmlData = queryAll(fileName,fileType)
            for f in xmlData:
                G = FP.parseXML(f,G)
            
        elif fileType == "json":
            print "Found JSON file"
            jsonData = queryAll(fileName,fileType)
            for f in jsonData:
                G = FP.parseJSON(f,G)
            
        elif fileType == "csv":
            print "Found CSV file"
            csvData = queryAll(fileName,fileType)
            for f in csvData:
                print f
                G = FP.parseCSV(f,G)

        elif fileType == "excel":
            print "Found Excel File"
            excelData = queryAll(fileName,fileType)
            for f in excelData:
                G = FP.parseEXCEL(f,G)
            
        else:
            print "Currently Not a Supported File"    
            
        print "Finished processing file"
        
    # Write out the graph object to file -------------------------------------------------------------------------------------
    if outputFileType == "gml":
        nx.write_gml(G,'output.gml')
        
    elif outputFileType == "adj":
        nx.write_adjlist(G,"output.adj")

    elif outputFileType == "mladj":
        nx.write_multiline_adjlist(G,"output.adjlist")
    
    elif outputFileType == "graphml":
        nx.write_graphml(G, "output.graphml")   
        
    elif outputFileType == "pajek":
        nx.write_pajek(G, "output.net")

    elif outputFileType == "neo4j":
        # Update to address of the Neo4j server
        results = neonx.write_to_neo("http://localhost:7474/db/data/", G, 'LINKS_TO')
                
if __name__ == "__main__":

    # Use argparse to require the two required command line arguments
    parser = argparse.ArgumentParser(description='A tool to convert various data sources into a network  via the use of RDF.')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-r', '--rdf', type=str, nargs=1, required = True, help='the location of the rdf file to be processed. Must be a string')
    requiredNamed.add_argument('-o', '--out', type=str, nargs=1, required = True, help='the file format for the final network object to be saved as. Must be a string')
    args = parser.parse_args()
    
    main(str(args.rdf[0]), str(args.out[0]))