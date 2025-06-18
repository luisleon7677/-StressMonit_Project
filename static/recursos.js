const boton = document.getElementById("modal");
const Tab = document.getElementById("modalTab");
const btnsVer = document.querySelectorAll('.btnVer');
boton.addEventListener('click',()=>{
    Tab.classList.remove("modal") //remuevo la clase visible
    Tab.classList.add("modal-close") //agrego la clase ocultar
});

btnsVer.forEach(btnVer=>{
    btnVer.addEventListener('click',()=>{
    Tab.classList.remove("modal-close") //remuevo la clase ocultar
    Tab.classList.add("modal") //agrego la clase ver
    })
});