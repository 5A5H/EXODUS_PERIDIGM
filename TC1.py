# Start Test Case 1
# Test contains a small mixed element mesh
from EP_lib import *
loadcheck()

# Create a EXODUS_PERIDIGM_MESH Class with specified filename to operate on
filepath='TestCase1/PD_Mesh.ascii';
EXFile = EXODUS_PERIDIGM_MESH(filepath)
# Display Docstring of the EXODUS_PERIDIGM_MESH Class
print(EXFile.__doc__);
# Read in nodal coordinates from a CSV file
EXFile.GetNodesFromCSVFile('TestCase1/nodes')
# Read in two element blocks form CSV files
EXFile.GetElementBlockFromCSVFile('TestCase1/element_blk1')
EXFile.GetElementBlockFromCSVFile('TestCase1/element_blk2')
# Read in two node sets form CSV files
EXFile.GetNodeSetFromCSVFile('TestCase1/node_set1')
EXFile.GetNodeSetFromCSVFile('TestCase1/node_set2')
# Perform EXODUS_PERIDIGM_MESH database check manually.
EXFile.check_database()
# Report current data in EXODUS_PERIDIGM_MESH Class before writing to output files.
EXFile.report()
# Write output file of type .ascii
EXFile.WriteToFile()
# Convert to binary format using 'ncgen'
EXFile.ConvertToBinary()