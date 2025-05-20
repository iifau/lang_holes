import xml.etree.ElementTree as ET
import os

def extract_adyghe(filename):
    inp_name = filename + ".xml"
    outp_name = filename + "_np.txt"
    tree = ET.parse(inp_name)
    root = tree.getroot()
    with open(outp_name, "w") as f:
        for se in root.findall('.//se[@lang="adyghe"]'):
            if se.text is not None:
                f.write(se.text + "\n")

directory = "" # TO FILL
names = os.listdir(directory)

for name in names:
    extract_adyghe(name)