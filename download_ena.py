#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 10:29:35 2021

@author: nkleinbo
"""

import getopt, sys, os, io, re

fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]

unixOptions = "hf:o:"
gnuOptions = ["help", "file=", "output="]

usage = """
usage: python3 download_ena.py
       -f <path to file with accessions>
       -o <output directory for reads>
example: python3 download_ena.py -f genbank.acc -o results/
"""

try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    print (str(err))
    sys.exit(2)

accession_file = None
downloadpath = None
    
for currentArgument, currentValue in arguments:
    if currentArgument in ("-h", "--help"):
        print (usage)
        exit()
    elif currentArgument in ("-f", "--file"):
        print (("Location of accession file: (%s)") % (currentValue))
        accession_file = currentValue
    elif currentArgument in ("-o", "--output"):
        print (("Results will be stored in: (%s)") % (currentValue))
        downloadpath = currentValue

if (downloadpath is None or accession_file is None):
    print (usage)
    exit()
 
if not (os.path.isdir(downloadpath)):
    os.mkdir(downloadpath)
    
accessions = open(accession_file, "r")
accessions_samples = {}
for acc in accessions:
    result = os.popen('curl -X GET "https://www.ebi.ac.uk/ena/browser/api/text/'+acc.rstrip()+'?lineLimit=0&annotationOnly=true" -H "accept: text/plain"').read()
    s = io.StringIO(result)
    for line in s:
        x = re.search("BioSample; (.*).", line.rstrip())
        if x is not None:
            accessions_samples[acc.rstrip()] = x.group(1)
accessions.close()    

accessions_runs = {}
accessions_descriptions = {}
for key in accessions_samples:
    biosample = accessions_samples[key]
    result = os.popen('curl -X GET "https://www.ebi.ac.uk/ena/portal/api/links/sample?accession='+biosample+'&format=json&result=read_run" -H "accept: /"').read()
    s = io.StringIO(result)
    for line in s:
        x = re.search("\"run_accession\":\"(.*)\",\"description\":\"(.*Illumina.*)\"", line.rstrip())
        if x is not None:
            accessions_runs[key.rstrip()] = x.group(1)
            accessions_descriptions[key.rstrip()] = x.group(2)
            
summary = open(os.path.join(downloadpath,"summary.tsv"), "w")
print(accessions_runs)
for key in accessions_runs:
    os.system("/home/ubuntu/enaBrowserTools/python3/enaDataGet -f fastq -d "+downloadpath+" "+accessions_runs[key])
    os.rename(downloadpath+"/"+accessions_runs[key], downloadpath+"/"+key)
    summary.write(key+"\t"+accessions_samples[key]+"\t"+accessions_runs[key]+"\t"+accessions_descriptions[key]+"\n")

summary.close()
