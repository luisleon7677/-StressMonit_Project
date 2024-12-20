const icon = document.getElementById("main-icon");
const barraLateral=document.querySelector(".barra-lateral");
const span = document.querySelector("span");
const spans = document.querySelectorAll("span");
const menu = document.querySelector(".menu");
const main = document.querySelector("main");

const logout = document.getElementById("boton-nav");

logout.addEventListener("click",()=>{
    window.location.href="/";
});
menu.addEventListener("click",()=>{
    barraLateral.classList.toggle("max-barra-lateral");
    if(barraLateral.classList.contains("max-barra-lateral")){
        menu.children[0].style.display = "none";
        menu.children[1].style.display = "block";
    }
    else{
        menu.children[0].style.display = "block";
        menu.children[1].style.display = "none";
    }

    if(window.innerWidth<=320){
        barraLateral.classList.add("mini-barra-lateral");
    main.classList.add("min-main");
    spans.forEach((span)=>{
        span.classList.add("oculto");
    });
    }
})

icon.addEventListener("click",()=>{
    barraLateral.classList.toggle("mini-barra-lateral");
    main.classList.toggle("min-main");
    spans.forEach((span)=>{
        span.classList.toggle("oculto");
    });
    
});