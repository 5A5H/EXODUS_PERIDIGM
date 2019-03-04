# Mainfile for EXODUS_PERIDIGM file writer

# Execute provided tests
ExecTest = 0; # 0 -> no test, 1 -> test TestCase1, 2 -> test TestCase2

if ExecTest==1:
    print('Starting Test Case 1');
    execfile('TC1.py');
elif ExecTest==2:
    print('Starting Test Case 2');
    execfile('TC2.py');
else:
    print('No Test');
    # Work on an own file, e.g:
    # EXFile = EXODUS_PERIDIGM_MESH('path/to/outputfile.ascii')
    # Add Nodes via File:
    # EXFile.GetNodesFromCSVFile('path/to/nodes')
    # Add Element Blocks:
    # EXFile.GetElementBlockFromCSVFile('path/to/element_blk')
    # Add Node Set:
    # EXFile.GetNodeSetFromCSVFile('path/to/node_set1')
    # Write output files:
    # EXFile.WriteToFile()
    #
    # EXFile.ConvertToBinary()
    # Remark: Take a look at the TestCases