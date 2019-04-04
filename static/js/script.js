function keyPress(e){
	console.log(e);
	if(e.key == "Enter"){
		e.preventDefault();
		e.stopPropagation();
		document.getElementById("uploadButton").click();
	}
}
function check(val){
	var resp = "nao";
	if(val == 1)
		resp = "sim";
	radios = document.getElementsByClassName(resp);
	for(var i=0 ; i < radios.length;i++){
		radios[i].click();
	}
}
function voltar(event){
	event.preventDefault();
	ref = window.location.href +"back";
	window.location.href = ref;
}