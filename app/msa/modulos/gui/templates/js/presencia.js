function mostrar_div_presencia(){
    console.log("Mostrando div presencia...")
    var elem = document.createElement('div');
    elem.id = "presencia-div";
    //elem.style.cssText = 'position:absolute;width:100%;height:100%;opacity:0.3;z-index:100;background:#000';
    document.body.appendChild(elem);
    elem.classList.add('presencia-box');
    elem.addEventListener('click', function() {
        console.log("Click en div presencia, enviando evento...")
        send("registrar_presencia_touch");
    });
    elem.style.display = 'block';
}

function ocultar_div_presencia(){
    var elem = document.getElementById("presencia-div");
    if (elem !== null){
        console.log("Ocultando div presencia...");
        elem.remove();
    }
}