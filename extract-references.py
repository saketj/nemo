#!/bin/python

import sys, getopt, os, re
from xml.dom import minidom

def processXml(tmpFile, outputFile):
    xmldoc = minidom.parse(tmpFile)
    itemlist = xmldoc.getElementsByTagName('reference')
    f = open(outputFile, "w")
    i = 1
    for item in itemlist:
        row = "[%d] %s\n" % (i, item.firstChild.nodeValue.encode('utf-8').strip())
        row = re.sub("\[\d+\]\s+\[\d+\]", "[0]", row)
        f.write(row)
        i = i + 1
    f.close()


def main(argv):
    inputFile = ''
    outputFile = ''
    tmpFile = '/tmp/references.xml'
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print 'test.py -i <inputFile> -o <outputFile>'
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputFile> -o <outputFile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputFile = arg.strip()
      elif opt in ("-o", "--ofile"):
         outputFile = arg.strip()
    if len(inputFile) == 0 or len(outputFile) == 0:
        return
    cmd = "pdf-extract extract --references %s > %s" % (inputFile, tmpFile)
    os.system(cmd)
    processXml(tmpFile, outputFile)
    cmd = "rm -rf %s" % tmpFile
    os.system(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
