#!/bin/bash

if [ $# -ne 2 ]
then
  echo USAGE \: ./find_PDB_ID_from_sequence.sh sequence type_sequence
  echo sequence = fichier fasta
  echo type_sequence = gene ou proteine
  echo EXEMPLE \: ./find_PDB_ID_from_sequence.sh 1zni.fasta proteine
else
  pwd
  if [ $2 = "gene" ]
  then
    ID_PDB=$(perl DjangoProjects/proteo/web_blast.pl blastx pdb $1 | grep % | head -1 | cut -c -4)
  elif [ $2 = "proteine" ]
  then
    ID_PDB=$(perl DjangoProjects/proteo/web_blast.pl blastp pdb $1 | grep % | head -1 | cut -c -4)
  fi
  python3 DjangoProjects/proteo/pdb_download.py $ID_PDB
  mv $ID_PDB ../media/
fi
