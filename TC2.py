# Start Test Case 2
# Test contains a rather large mixed element mesh
from EP_lib import *
loadcheck()

# Create a EXODUS_PERIDIGM_MESH Class with specified filename to operate on
filepath='TestCase2/PD_Mesh.ascii';
EXFile = EXODUS_PERIDIGM_MESH(filepath)
# Read in nodal coordinates from a CSV file
EXFile.GetNodesFromCSVFile('TestCase2/nodes')
# Read in four element blocks form CSV files
EXFile.GetElementBlockFromCSVFile('TestCase2/element_blk1')
EXFile.GetElementBlockFromCSVFile('TestCase2/element_blk2')
EXFile.GetElementBlockFromCSVFile('TestCase2/element_blk3')
EXFile.GetElementBlockFromCSVFile('TestCase2/element_blk4')
# Read in two node sets form CSV files
EXFile.GetNodeSetFromCSVFile('TestCase2/node_set1')
EXFile.GetNodeSetFromCSVFile('TestCase2/node_set2')
EXFile.GetNodeSetFromCSVFile('TestCase2/node_set3')
EXFile.GetNodeSetFromCSVFile('TestCase2/node_set4')
# Perform EXODUS_PERIDIGM_MESH database check manually.
EXFile.check_database()
# Report current data in EXODUS_PERIDIGM_MESH Class before writing to output files.
EXFile.report()
# Write output file of type .ascii
EXFile.WriteToFile()
# Convert to binary format using 'ncgen'
EXFile.ConvertToBinary()