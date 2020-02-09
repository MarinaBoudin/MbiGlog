/*
Boudin Marina

Projet Glog - groupe proteomics

*/
// Activation des onglets
function activer_onglet(){
  let three=document.getElementById("three");
  three.classList.add("activated");
}

function defaultStructureRepresentation( component ){
    // bail out if the component does not contain a structure
    if( component.type !== "structure" ) return;
    // add three representations
    component.addRepresentation( "cartoon", {
        aspectRatio: 3.0,
        scale: 1.5
    } );
    component.addRepresentation( "licorice", {
        sele: "hetero and not ( water or ion )",
        multipleBond: true
    } );
    component.addRepresentation( "spacefill", {
        sele: "water or ion",
        scale: 0.5
    } );
}

function add(path){
  stage.loadFile(path).then(function (mol) {
    mol.setPosition([20, 0, 0]);
    mol.setRotation([ 2, 0, 0 ]);
    mol.setScale(0.5);
    if (get_selection("colour")!=="structure"){
      mol.addRepresentation(get_selection("representation"), {color: get_selection("colour")});
    }
    else{
      mol.addRepresentation(get_selection("representation"));
    }
    stage.autoView();
  });
}

function addProt(){
  let input=document.getElementById("pdbidInput");
  var path = "rcsb://"+input.value+".mmtf";
  input.value="";
  input.blur();
  add(path);
}

function get_selection(id){
  let selected = document.getElementById(id);
  var rep = selected.options[selected.selectedIndex].value;
  return rep;
}

function display(id){
  console.log(id);
  let element= document.getElementById(id);
  element.style["display"]="block";
}

function main(){
  activer_onglet();
  let path = sessionStorage.getItem("Path");
  if (path!="null" && ( path.search(".fasta")==-1)){
    let a = document.getElementById("the_file");
    a.href=path;
    let button = document.getElementById("my_mol");
    button.addEventListener("click",function(){
      add(path);
    });
    button.style["display"]="inline";
    for (element in path_elements){
      display(path_elements[element]);
    };
  }
  let plus = document.getElementById("plus").addEventListener("click",addProt)
  let clear = document.getElementById("clear").addEventListener("click",function(){
    stage.removeAllComponents();
  });
  let spin = document.getElementById("spin").addEventListener("click",function(){
    stage.setSpin((!(bool_spin)));
    bool_spin=(!(bool_spin));
  });
  sessionStorage.setItem("Path",null);
}

var stage;
var bool_spin=false;
stage = new NGL.Stage("visualisation");
stage.viewer.container.addEventListener("dblclick", function (){
    stage.toggleFullscreen();
});
path_elements=["controls1","controls2","controls3","div_path"];

window.onload=main;
