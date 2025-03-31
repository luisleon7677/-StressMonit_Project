
//obtengo los elementos del modal
var modal = document.getElementById('modal-recurso');
var btns = document.querySelectorAll('.mostrarModal');
var span = document.getElementById('cerrarModal');


//mostrar el modal al hacer clilc en boton
btns.forEach(function(btn){
    btn.onclick = function(){
        modal.style.display = "block";
    }
})
//cerrar el modal cuando el usuario haga clil en cerrar

span.onclick = function(){
    modal.style.display = "none";
}