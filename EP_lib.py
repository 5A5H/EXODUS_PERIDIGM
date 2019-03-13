# This is the projects library containing the functions and object definitions
import numpy as np
from time import gmtime, strftime
import subprocess


def loadcheck():
    print('- EP_lib library loaded -');
    return 0

class Nodes:
    '''
    This Class contains nodal data.
    '''

    def __init__(self):
        self.NumberOfNodes = 0;
        self.xcoor = [];
        self.zcoor = [];
        self.ycoor = [];

    def __update(self): # the __ makes the function private, else it overwrites update method of mother class
        self.NumberOfNodes = len(self.xcoor);

    def check_database(self):
        '''
        Checks for data to be healthy.
        Features:
        - 1 check wether all number of coordinates are eual
        '''
        # Check wether all coordinate fields are of the same length
        lenx = len(self.xcoor);
        leny = len(self.ycoor);
        lenz = len(self.zcoor);
        lst = [lenx, leny, lenz];
        if (lst[1:] == lst[:-1]):
            return 0
        else:
            print('Error! Unequal Coordinate Numbers');
            print('       Coordinates have been resetted');
            self.xcoor = [];
            self.zcoor = [];
            self.ycoor = [];


    def GetNodesFromCSVFile(self, filename):
        '''
        Read in Nodal data from CVS file.
        File should look like:
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        1.0, 1.0, 0.0,
        ...
        Remark: only 3D nodes supported!
        '''
        XI = np.loadtxt(filename, delimiter=",", dtype="float");
        self.xcoor = XI[:, 0];
        self.ycoor = XI[:, 1];
        self.zcoor = XI[:, 2];
        self.check_database();
        self.__update();

    def GetNodes(self):
        '''
        Function returns a 2d numpy array of current nodes.
        returns: np.array([
                           [0.0, 0.0, 0.0],
                           [1.0, 0.0, 0.0],
                           [1.0, 1.0, 0.0],
                           ...
                         ])
        '''
        return np.array([self.xcoor, self.ycoor, self.zcoor]).T

class Element_Block:
    '''
    This class contains element block data.
    1. A list of nodal numbers (int)
    2. Knows its kind of elements (TETRA or HEX8)
    element_data has the form: np.array([[1,2,3,4],[3,4,5,6]])
    '''

    def __init__(self,
                 element_data
                 ):
        # first find out of how many nodes an element is made of
        self.nodes_per_element = len(element_data[0]);
        self.elements_in_this_block = len(element_data);
        self.kind = 'TETRA' if self.nodes_per_element==4 else 'HEX8';
        # finally store the data as a pure list of node numbers
        self.element_block_node_list = element_data.flatten();

class Node_Set:
    '''
    This class contains node numbers of a node set.
    node_set has the form: np.array([1,2,3,4,5,...])
    '''
    def __init__(self,
                 node_set
                 ):
        self.node_set_node_list = node_set;
        self.nodes_in_this_set = len(node_set);

class EXODUS_PERIDIGM_MESH(Nodes):
    '''
    This is the mother class which inherits everything to be known for a PERIDIGM used mesh.
    It is also able to generate a .ascii version of its content by means of an EXODUSII format.
    As the command 'ncgen' is knwon it can convert it to netcdf binary.
    Renark: For usage in PERIDIGM this basically mans introducing:
    "Nodes" in 3D which are used in "Element-Blocks" were elements are of same type (either TETRA or HEX8)
    and finally "Node-Sets" which are need to define boundary contitions.
    Functions to collect Data:
     - GetElementBlockFromCSVFile(filename)
     - GetNodeSetFromCSVFile(filename)
     - GetNodesFromCSVFile(filenme)
    Functions to write Files:
     - WriteToFile()
     - ConvertToBinary()
    Functions of major interest:
     - report()
    '''

    def __init__(self,
                 filename=''
                 ):
        self.filename = filename;
        Nodes.__init__(self);
        self.element_blocks = [];
        self.node_sets = [];
        self.NumberOfElements = 0;
        self.title = 'UNKNOWN';
        self.NumberOfNodeSets = 0;
        self.NumberOfElementBlocks = 0;
        self.binaryfilename = filename.split('.')[0]+'.g';

# Define functions to fetch data

## Fetch Element Block Data From CSV File
    def GetElementBlockFromCSVFile(self, filename):
        '''
        Reads element block from a CSV file.
        Each block needs to be loaded by a separate file.
        The file should contain a simple list with element connections by line, e.g.:
        1, 2, 4, 3,
        6, 4, 3, 5, ...
        The node number must correspond to the nodes stored within the EXODUS_PERIDIGM_MESH class.
        '''
        self.element_blocks.append(Element_Block(np.atleast_2d(np.loadtxt(filename, delimiter=",", dtype="int"))));

## Fetch Node Set Data From CSV File
    def GetNodeSetFromCSVFile(self, filename):
        '''
        Reads a node set from a CSV file.
        Each set needs to be loaded by a separate file.
        The file should contain a simple list with element connections by line, e.g.:
        1, 2, 3, ...
        The node number must correspond to the nodes stored within the EXODUS_PERIDIGM_MESH class.
        '''
        self.node_sets.append(Node_Set(np.loadtxt(filename, delimiter=",", dtype="int")));

# Report function
    def report(self):
        '''
        Gives a summary of the current states / content of this class
        '''
        self.update();
        print('Class: EXODUS_PERIDIGM_MESH');
        print('Current associated output file: %s' % self.filename);

        # Report on Nodes
        if (self.NumberOfNodes > 0):
            print('- Nodal Data:');
            print('  number of nodes: %d' % self.NumberOfNodes);
        else:
            print('- no Nodes specified yet!');

        # Report on Element Blocks
        if (len(self.element_blocks) > 0):
            print('- Element Data:');
            print('  total number of elements: %d' % self.NumberOfElements);
            # loop over all element blocks and give all attributies
            for n,elmtset in enumerate(self.element_blocks):
                print('  + Element Block %d'%n);
                print('    block contains %d elements' %elmtset.elements_in_this_block);
                print('    elements are of type %s with %d nodes each' %(elmtset.kind,elmtset.nodes_per_element));
            # Warn if elements are known but no nodes yet!
            if (self.NumberOfNodes == 0):
                print('Warning! No nodes specified yet!');
                print('         elements refere to void!');
        else:
            print('- no Element Blocks specified yet!');

        # Report on Node Sets
        if (len(self.node_sets) > 0):
            print('- Node Sets:');
            # loop over all node sets and give all attributies
            for n, nodeset in enumerate(self.node_sets):
                print('  + Node Set %d' % n);
                print('    set contains %d nodes'%nodeset.nodes_in_this_set)
            # Warn if node sets are known but no nodes yet!
            if (self.NumberOfNodes == 0):
                print('Warning! No nodes specified yet!');
                print('         node sets refere to void!');
        else:
            print('- no Node Sets specified yet!');

# Update function
    def update(self):
        self.NumberOfElements = 0;
        for elmtset in self.element_blocks:
            self.NumberOfElements += elmtset.elements_in_this_block;
        self.NumberOfNodeSets = len(self.node_sets);
        self.NumberOfElementBlocks = len(self.element_blocks);

# Functions used within the class

## Function to write global attributes data
    def write_GlobalAttribute_data_EXII(self, EXODUS_OUTPUT):
        '''
        Function writes global attributes to EXODUS.ascii file.
        (tells Paraview which reader to use).
        Should not be called by the user.
        '''
        EXODUS_OUTPUT.write(":api_version = 4.98f ;\n");
        EXODUS_OUTPUT.write(":version = 4.98f ;\n");
        EXODUS_OUTPUT.write(":floating_point_word_size = 8 ;\n");
        EXODUS_OUTPUT.write(":file_size = 1 ;\n");
        EXODUS_OUTPUT.write(":title = \""+self.title+"\" ;\n");

## Function to write dimensional data V2
    def write_Dimensions_data_EXII(self, EXODUS_OUTPUT):
        '''
        Function writes dimension declaration to EXODUS.ascii file.
        Should not be called by the user.
        '''
        EXODUS_OUTPUT.write("dimensions:\n");
        EXODUS_OUTPUT.write("    len_string = "+str(33)+" ;\n");
        EXODUS_OUTPUT.write("    len_line = " + str(81) + " ;\n");
        EXODUS_OUTPUT.write("    four = " + str(4) + " ;\n");
        EXODUS_OUTPUT.write("    len_name = " + str(33) + " ;\n");
        EXODUS_OUTPUT.write("    time_step = UNLIMITED ;\n");
        EXODUS_OUTPUT.write("    num_dim = " + str(3) + " ;\n");
        EXODUS_OUTPUT.write("    num_nodes = " + str(self.NumberOfNodes) + " ;\n");
        EXODUS_OUTPUT.write("    num_elem = " + str(self.NumberOfElements) + " ;\n");
        EXODUS_OUTPUT.write("    num_node_sets = " + str(self.NumberOfNodeSets) + " ;\n");
        EXODUS_OUTPUT.write("    num_el_blk = " + str(self.NumberOfElementBlocks) + " ;\n");
        EXODUS_OUTPUT.write("    num_qa_rec = " + str(1) + " ;\n");

        # extend dimension data dictionary by element block dimensions
        for Number, ElmBlk in enumerate(self.element_blocks):
            EXODUS_OUTPUT.write("num_el_in_blk" + str(Number + 1)+" = "+str(ElmBlk.elements_in_this_block)+" ;\n");
            EXODUS_OUTPUT.write("num_nod_per_el" + str(Number + 1)+" = "+str(ElmBlk.nodes_per_element)+" ;\n");

        # extend dimension data dictionary by node set dimensions
        for Number, NodeSet in enumerate(self.node_sets):
            EXODUS_OUTPUT.write("num_nod_ns" + str(Number + 1)+" = "+str(NodeSet.nodes_in_this_set)+" ;\n");

## Function to write variables data
    def write_Variables_data_EXII(self, EXODUS_OUTPUT):
        '''
        Function writes variable declaration to EXODUS.ascii file.
        Should not be called by the user.
        '''
        EXODUS_OUTPUT.write("variables:\n");
        # declare general integer variables
        EXODUS_OUTPUT.write("    int eb_status(num_el_blk);\n");
        EXODUS_OUTPUT.write("    int eb_prop1(num_el_blk);\n");
        EXODUS_OUTPUT.write("        eb_prop1:name = \"ID\" ;\n");
        EXODUS_OUTPUT.write("    int ns_status(num_node_sets);\n");
        EXODUS_OUTPUT.write("    int ns_prop1(num_node_sets);\n");
        EXODUS_OUTPUT.write("        ns_prop1:name = \"ID\" ;\n");
        EXODUS_OUTPUT.write("    int elem_map(num_elem);\n");
        EXODUS_OUTPUT.write("    int elem_num_map(num_elem);\n");
        EXODUS_OUTPUT.write("    int node_num_map(num_elem);\n");
        # declare general double variables
        EXODUS_OUTPUT.write("    double coordx(num_nodes);\n");
        EXODUS_OUTPUT.write("    double coordy(num_nodes);\n");
        EXODUS_OUTPUT.write("    double coordz(num_nodes);\n");
        EXODUS_OUTPUT.write("    double time_whole(time_step);\n");
        # declare general character variables
        EXODUS_OUTPUT.write("    char eb_names(num_el_blk, len_name);\n");
        EXODUS_OUTPUT.write("    char ns_names(num_node_sets, len_name);\n");
        EXODUS_OUTPUT.write("    char coor_names(num_dim, len_name);\n");
        EXODUS_OUTPUT.write("    char qa_records(num_qa_rec, four, len_string);\n");
        # declare block specific variables
        for Number, ElmBlk in enumerate(self.element_blocks):
            EXODUS_OUTPUT.write("    int connect"+str(Number+1)+"(num_el_in_blk"+str(Number+1)+", num_nod_per_el"+str(Number+1)+");\n");
            EXODUS_OUTPUT.write("        connect" + str(Number + 1) + ":elem_type = \""+ElmBlk.kind+ "\" ;\n");

        # declare node set specific variables
        for Number,NodeSet in enumerate(self.node_sets):
            EXODUS_OUTPUT.write("    int node_ns" + str(Number + 1) + "(num_nod_ns" + str(Number + 1) + ");\n");
            EXODUS_OUTPUT.write("    double dist_fact_ns" + str(Number + 1) + "(num_nod_ns" + str(Number + 1) + ");\n");

## Function to write actual mesh data
    def write_Mesh_data_EXII(self, EXODUS_OUTPUT):
        '''
        Function writes quality assurance data to EXODUS.ascii file.
        Should not be called by the user.
        '''
        EXODUS_OUTPUT.write("data:\n");

        # Write QA data
        EXODUS_OUTPUT.write("  qa_records = ");
        EXODUS_OUTPUT.write("\"PYTHON_EXODUSII_PERIDIGM\", ");
        EXODUS_OUTPUT.write("\"V1.0\", ");
        EXODUS_OUTPUT.write("\""+strftime("%Y/%m/%d",gmtime())+"\", ");
        EXODUS_OUTPUT.write("\""+strftime("%H:%M:%S", gmtime())+"\"");
        EXODUS_OUTPUT.write(";\n");

        # Write standard data

        ## eb_status = 1, 1, ... n_element_blocks;
        EXODUS_OUTPUT.write("  eb_status = ");
        for Number in range(self.NumberOfElementBlocks):
            EXODUS_OUTPUT.write("1" + (";\n" if Number == self.NumberOfElementBlocks - 1 else ", "));

        ## eb_prop1 = 1, 2, ... n_element_blocks;
        EXODUS_OUTPUT.write("  eb_prop1 = ");
        for Number in range(self.NumberOfElementBlocks):
            EXODUS_OUTPUT.write(str(Number+1)+(";\n" if Number==self.NumberOfElementBlocks - 1 else ", "));

        ## ns_status = 1 , ... n_node_sets;
        EXODUS_OUTPUT.write("  ns_status = ");
        for Number in range(self.NumberOfNodeSets):
            EXODUS_OUTPUT.write("1" + (";\n" if Number == self.NumberOfNodeSets - 1 else ", "));

        ## ns_prop1 = 1, 2, ... n_element_blocks;
        EXODUS_OUTPUT.write("  ns_prop1 = ");
        for Number in range(self.NumberOfNodeSets):
            EXODUS_OUTPUT.write(str(Number + 1) + (";\n" if Number == self.NumberOfNodeSets - 1 else ", "));

        # Write Nodal data

        ## coorinate names = "x", "y", "z";
        EXODUS_OUTPUT.write("  coor_names = \"x\",\"y\",\"z\";\n");

        ## nodal coordinates
        ii=1;
        EXODUS_OUTPUT.write("  coordx = ");
        for n, x in enumerate(self.xcoor):
            EXODUS_OUTPUT.write(str(x) + (";\n" if n == self.NumberOfNodes - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;
        ii=1;
        EXODUS_OUTPUT.write("  coordy = ");
        for n, y in enumerate(self.ycoor):
            EXODUS_OUTPUT.write(str(y) + (";\n" if n == self.NumberOfNodes - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;

        ii=1;
        EXODUS_OUTPUT.write("  coordz = ");
        for n, z in enumerate(self.zcoor):
            EXODUS_OUTPUT.write(str(z) + (";\n" if n == self.NumberOfNodes - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;

        # Write Elemental data

        ## for each node
        ## connectX = node1_of_elm1, node2_of_elm1, .... nodeN_of_elmN;
        ii=1;
        for Number,ElmtBlk in enumerate(self.element_blocks):
            EXODUS_OUTPUT.write("  connect" + str(Number + 1) + " = ");
            for n,node in enumerate(ElmtBlk.element_block_node_list):
                EXODUS_OUTPUT.write(str(node) + (";\n" if n == len(ElmtBlk.element_block_node_list) - 1 else ", "));
                ii=ii+1;
                if ii > 3:
                    EXODUS_OUTPUT.write("\n          ");
                    ii=1;

        ## element map = 1,2,3,... n_elem;
        ii=1;
        EXODUS_OUTPUT.write("  elem_map = ");
        for i in range(self.NumberOfElements):
            EXODUS_OUTPUT.write(str(i + 1) + (";\n" if i == self.NumberOfElements - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;

        ## elem_num_map = 1,2,3,... n_elem;
        ii=1;
        EXODUS_OUTPUT.write("  elem_num_map = ");
        for i in range(self.NumberOfElements):
            EXODUS_OUTPUT.write(str(i + 1) + (";\n" if i == self.NumberOfElements - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;

        ## eb_names = "", "", .. n_number_of_element_blocks;
        ii=1;
        EXODUS_OUTPUT.write("  eb_names = ");
        for i in range(self.NumberOfElementBlocks):
            EXODUS_OUTPUT.write("\"\"" + (";\n" if i == self.NumberOfElementBlocks - 1 else ", "));
            ii=ii+1;
            if ii > 3:
                EXODUS_OUTPUT.write("\n          ");
                ii=1;


        # Write Node Set data

        ## ns_names = "", "", "", ... n_number_of_node_sets;
        # 4.1 ns_names
        EXODUS_OUTPUT.write("  ns_names = ");
        for i in range(self.NumberOfNodeSets):
            EXODUS_OUTPUT.write("\"\"" + (";\n" if i == self.NumberOfNodeSets - 1 else ", "));

        ## for each node set
        ## node_nsX = 1,4,6,...34, n_number_of_nodes_in_set
        ## dist_fact_ns_X = 1,1,1,1,1.... number_of_nodes_in_set
        for Number, NodeSet in enumerate(self.node_sets):
            ii=1;
            EXODUS_OUTPUT.write("  node_ns" + str(Number + 1) + " = ");
            for num, node in enumerate(NodeSet.node_set_node_list):
                EXODUS_OUTPUT.write(str(node)+(";\n" if num ==NodeSet.nodes_in_this_set - 1 else ", "));
                ii=ii+1;
                if ii > 3:
                    EXODUS_OUTPUT.write("\n          ");
                    ii=1;

            ii=1;
            EXODUS_OUTPUT.write("  dist_fact_ns" + str(Number + 1) + " = ");
            for num, node in enumerate(NodeSet.node_set_node_list):
                EXODUS_OUTPUT.write("1" + (";\n" if num == NodeSet.nodes_in_this_set - 1 else ", "));
                ii=ii+1;
                if ii > 3:
                    EXODUS_OUTPUT.write("\n          ");
                    ii=1;

# Functions to write output

## Function to write the EXODUS file
    def WriteToFile(self):
        '''
        This function writes the content to .ascii file.
        '''
        self.update();
        # Write header
        EXODUS_OUTPUT = open(self.filename,'w');
        EXODUS_OUTPUT.write("netcdf "+self.title+" {\n");
        # Write global attributes
        self.write_GlobalAttribute_data_EXII(EXODUS_OUTPUT);
        # Write dimensional data
        self.write_Dimensions_data_EXII(EXODUS_OUTPUT);
        # Write variable declaration
        self.write_Variables_data_EXII(EXODUS_OUTPUT);
        # Write actual mesh data
        self.write_Mesh_data_EXII(EXODUS_OUTPUT);
        # Write close file
        EXODUS_OUTPUT.write("}");
        EXODUS_OUTPUT.close();

## Function to convert the .ascii mesh file
    def ConvertToBinary(self, delete_ascii=True):
        '''
        This function will try to convert the written .ascii file to the binary .g file.
        This can be read by Paraview and Peridigm.
        For this purpose the function 'ncgen' is called, which is part of the netcdf
        program which is requried by Peridigm anyway.
        Remark: On Windows maybe nessecary to give self.binaryfilename manually.
        '''
        print(subprocess.check_output(["ncgen","-o",self.binaryfilename,self.filename]));
        if delete_ascii:
            print(subprocess.check_output(["rm",self.filename]));
