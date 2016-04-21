<img align="right" src="http://raw.githubusercontent.com/sbonner0/SemNetCon/master/docs/images/network.png?raw=true">
# SemNetCon

### What is SemNetCon
Semantic Enabled Python Tool For The Construction Of Complex Networks From Disperse Data Sources (SemNetCon).
SemNetCon it a tool to enable the conversion between multiple graph or complex network storage formats. It has been designed to allow end users to easily convert a given data source into a range of possible common network formats. In addition to this it has been designed to be extended by the research community to support new features and file formats.

### Features
* Generate RDF by describing the data to be converted into a network againstthe ontology.* Leverage the RDF to enable generic parsers to construct topological representations of the data.* Create a GUI so users do not have to manually create the RDF data.* Allow for easy expansion of the underlying OWL ontology and the list of fileparsers so the tool can be applicable in a wide range of fields.
* Supports; JSON, XML, CSV, and Excel file formats. 

### Supported OS
SemNetCon has been designed and tested on various UNIX like platforms, specifically Mac OSX and Linux. As such, it should work on any modern OSX version or Linux distribution. SemNetCon has been explicitly tested on the following platforms - Ubuntu 14.04, Fedora 22, CentOS 7 and OSX 10.11.

### Licence

SemNetCon is licensed under the GNU GPL version 3. For more information please refer to the LICENCE file that accompanies the source.

### Examples

A number of examples are provided with this code, in the folder named as such. These can be used with the command line interface, e.g. to use the XML example;

`./semnetcon --cli -r examples/XML-Test.rdf -o graphml`

## Dependancies and Installation
SemNetCon has the following dependencies, all of which are available via pip;

Dependancy  | Min Version
------------- | -------------
Python  | 2.7
NetworkX | 1.10jq <sup id="a1">[1](#f1)</sup>| 0.1.5
lxml | 3.4.4rdflib | 4.2.1SPARQLWrapper | 1.7.4xlrd | 0.9.4

### Downloading
SemnetCon is currently hosted at GitHub. It's project page can be found at <http://github.com/sbonner0/SemNetCon>.

The source can be downloaded with:

`git clone http://github.com/sbonner0/SemNetCon`

### Installation

No installation is required as SenNetCon will run directly from any location.

## GUI Interface
The graphical interface is invoked with:

`./semnetcon`

Upon invoking the GUI the user is asked to select an input file. Once this is done the file information form will be presented.
<p align="center">
<img src="http://raw.githubusercontent.com/sbonner0/SemNetCon/master/docs/images/info_form_default.png?raw=true" alt="Default Form"/>
</p>
File Type and Output Format are simply selected through drop-down options. Other fields are dependent on the input file format being used, these are explained fully below.<sup id="a2">[2](#f2)</sup>

**note** All attributes are specified in the form `name:value` where `name` is a user defined literal string and `value` is defined as a suitable form for the input type. Multiple attributes must be comma separated.

Upon completion of the form the user will be asked if there are further files to process. When information for all files has been completed the user will be given the option to save the RDF description of the data in addition to the production of the output file.

### Node, Edge and Attribute Syntax

#### XML
Values and attributes for XML input files need to be represented as valid XPath queries.

**Example**

Given the XML input;

```xml
<?xml version="1.0" encoding="utf-8"?>
<net>
  <netitem id="file" value="graph1" node="node_0" attribute_1="Attr_1"
  edge_from="Node_1" edge_to="Node_2" att_1="Attr_1" att2="Attr_2"
  />

```

* Node Value would be `/net/netitem/@node`
* Node Attrs would be `/net/netitem/@attribute_1`
* Edge Value From would be `/net/netitem/@edge_to`
* Edge Value To would be `/net/netitem/@edge_from`
* Edge Attrs From would be
```
ATT1:/net/netitem/@att1,ATT2:/net/netitem/@att2
```


Delimiter and Starting Line values are not required for this file type.
#### JSON
Values and attribute values for JSON input files need to be represented as valid JSONPath queries, with any arrays identified with the use of `[]`.

**Example**

Given the JSON input;

```json
{"net": {
  "id": "file",
  "value": "graph1",
  {"node": "Node_0"},
  {"attribute_1": "Attr_1"},
  "info": {
    "netitem": [
      {"edge_from": "Node_1"},
      {"edge_to": "Node_2"},
      {"att_1": "Attr_1"},
      {"att_2": "Attr_2"}
    ]
  }
}}
```
 
* Node Value would be `.net.node`
* Node Attrs would be `.net.attribute_1`
* Edge Value From would be `.net.info.netitem[].edge_from`
* Edge Value To would be `.net.info.netitem[].edge_to`
* Edge Attrs From would be
```
ATT1:.net.info.netitem[].att_1,ATT2:.net.info.netitem[].att_2
```

Delimiter and Starting Line values are not required for this file type.

#### CSV
Values and Attribute values for CSV files need to be the column number where the values can be found.

The Delimiter field can accept any delimiting character. The only currently supported alphabetic escape sequences is `\t` for TAB separated values which must be entered into the form as `t`.

The starting line is used to ignore any comments or headers that may exist at the beginning of the file.

#### Excel
Values and Attributes for CSV files need to be the column number where the values can be found.

The Delimiter value is not required for this file type.

The starting line is used to ignore any comments or headers that may exist at the head of the spreadsheet. 


## CLI Interface
The SemnetCon command line interface is invoked with;

`./semnetcon --cli`

Arguments available are;

```
-h, --help         show this help message and exit
--cli              Use CLI instaed of default GUI: Requires -r and -o
-r RDF, --rdf RDF  The location of the rdf file to be processed.
-o OUT, --out OUT  The file format for the final network object to be saved as.
```

Using SemNetCon in this manner requires that the user already has a pre-generated RDF that describes the data to be processed. Please see the examples folder for samples of valid RDF that can be used for this purpose. The RDF file is specified with the `-r` flag. The `-o` flag specifies the output type required by the user. The available options are described in the table below.

Flag  | File Type
------------- | -------------
gml | GML<sup id="a3">[3](#f3)</sup>
adj | Adjacency List
mladj | Multiline Adjacency List
graphml | GraphML<sup id="a4">[4](#f4)</sup>
pajek | Pajek<sup id="a5">[5](#f5)</sup>

## Developer

### Adding a Custom Parser

In order to add a custom parser the following steps are required.

#### CLI Integration/Requirements

* Define the new parser in `FileParser.py`. The function should be of the form;

    ```python 
    def newParser(decodedInfo, G)
    ```
    Where decodedInfo is a list of network attributes, supplied by Network_Constructor.queryAll, and G is a networkX graph object, within which the network is constructed. This function also needs to return G.
* In `Network_Constructor.queryAll` specify an appropriate RDF query to produce the decodedInfo for the desired file type.
* Add a suitable condition to `Network_Constructor.main` in order to call `queryAll` and the parser for the new file type.


#### GUI Integration/Requirements

* Add the new type option to the drop-down list in `RdfBuildGUI.formbox` using the typeChoices variable.
* Specify any fields that should not be active for the required type using `RdfBuildGUI.typeUpdate`.

<b id="f1">1</b> The jq dependancy is interchangeable with jsonpath rw > 1.4.0. [↩](#a1)

<b id="f2">2</b> It is expected that a single file will contain either node or edge information, not both. However if this is the case the same file can be included twice, once with node information and once with edge information. [↩](#a2)

<b id="f3">3</b> [GML Information](https://www.fim.uni-passau.de/fileadmin/files/lehrstuhl/brandenburg/projekte/gml/gml-technical-report.pdf) [↩](#a3)

<b id="f4">4</b> [GraphML Information](http://graphml.graphdrawing.org/primer/graphml-primer.html) [↩](#a4)

<b id="f5">5</b> [Pajek Information](http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/pajekman.pdf) [↩](#a5)
