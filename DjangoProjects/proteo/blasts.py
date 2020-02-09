'''
GLOG
GROUPE PROTEOMIQUE
10/02/2020
'''
import sys
import os

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts

def findPDBFileFromUnknownSequence(fichier, type_de_sequence):
    type_de_sequence=type_de_sequence.replace("\n","")
    fichier = fichier.replace("\n","")
    shellscript = subprocess.Popen(["/DjangoProjects/proteo/find_PDB_ID_from_sequence.sh","%s"%(fichier),"%s"%(type_de_sequence)], stdin=subprocess.PIPE)
    returncode = shellscript.returncode
    # res=os.system('sh ./find_PDB_ID_from_sequence.sh %s %s'%(fichier,type_de_sequence))
    print(returncode)

def main(argv):
    myargs=getopts(argv)
    if '-sequence' in myargs and '-type' in myargs:
        findPDBFileFromUnknownSequence(myargs['-sequence'], myargs['-type'])
    else :
        print("Arguments manquants ou invalides !")

if __name__=="__main__":
    main(sys.argv[1:])
