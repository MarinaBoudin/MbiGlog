from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import requests
from subprocess import run,PIPE
import sys
import os
import subprocess

def findPDBFileFromUnknownSequence(fichier, type_de_sequence):
    type_de_sequence=type_de_sequence.replace("\n","")
    fichier = fichier.replace("\n","")
    find = os.getcwd()+"/DjangoProjects/proteo/find_PDB_ID_from_sequence.sh"
    shellscript = subprocess.Popen([find,"%s"%(fichier),"%s"%(type_de_sequence)], stdin=subprocess.PIPE)
    returncode = shellscript.returncode
    # res=os.system('sh ./find_PDB_ID_from_sequence.sh %s %s'%(fichier,type_de_sequence))
    print(returncode)

def get_fasta(name):
    cwd=os.getcwd()
    path ="../media/"+name
    findPDBFileFromUnknownSequence(path,"proteine")


def clean_media():
    cwd = os.getcwd();
    shellscript = subprocess.Popen([cwd+"/DjangoProjects/proteo/clean_media_PDB.sh"], stdin=subprocess.PIPE)
    returncode = shellscript.returncode
    return returncode

def handle_uploaded_file(f):
    print("coucou")
    with open('DjangoProjects/proteo/static/proteo/current_mol.pdb', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
# Create your views here.
def home(request):
    clean_media()
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name.replace(".txt",""), myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'proteo/home.html', {'uploaded_file': uploaded_file_url})
    return render(request, "proteo/home.html", locals())

def Onedimension(request):
    clean_media()
    if request.method == 'POST' and request.FILES['myfile']:
        os.system('sh ./clean_media_PDB.sh')
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name.replace(".txt",""), myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'proteo/1D.html', {'uploaded_file': uploaded_file_url})
    return render(request,'proteo/1D.html',locals())


def Twodimension(request):
    return render(request,'proteo/2D.html',locals())

def Threedimension(request):
    clean_media()
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name.replace(".txt",""), myfile)
        if (".fasta" in myfile.name):
            get_fasta(filename)
        uploaded_file_url = fs.url(filename)
        return render(request, 'proteo/3D.html', {'uploaded_file': uploaded_file_url})
    return render(request,'proteo/3D.html',locals())

def ViewThree(request):
    return render(request,'proteo/visu3D.html',locals())

def model(request):
    inp=request.POST.get('par2')
    return render(request,'proteo/modeling/'+inp+'.obj',locals())

def ext(request):
    inp=request.POST.get('par')
    out=run([sys.executable,'MbiGlog/DjangoProjects/proteo/pymol_export_dl0.py',inp],shell=False,stdout=PIPE)
    print(out)
    return render(request,'proteo/2D.html',{'data':out})

def external(request):
    inp=request.POST.get('param')
    out=run([sys.executable,'MbiGlog/DjangoProjects/proteo/psipred.py',inp],shell=False,stdout=PIPE)
    print(out)
    data=read(inp)
    return render(request,'proteo/2D.html',{'data1':data})

def read(id_pdb):
    #lecture fichier
    path='/'+id_pdb+'.horiz'
    f = open(path,"r")
    data = f.read()
    f.close()
    return data
