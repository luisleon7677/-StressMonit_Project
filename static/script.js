document.addEventListener("DOMContentLoaded", function () {
    const icon = document.getElementById("main-icon");
    let itemBarraLateral = document.querySelectorAll("nav.navegacion > ul > li > a");
    const barraLateral = document.querySelector(".barra-lateral");
    const spans = document.querySelectorAll("span");3
    const menu = document.querySelector(".menu");
    const main = document.querySelector("main");

    // Agregar evento para el menú lateral
    menu.addEventListener("click", () => {
        barraLateral.classList.toggle("max-barra-lateral");

        if (barraLateral.classList.contains("max-barra-lateral")) {
            menu.children[0].style.display = "none";
            menu.children[1].style.display = "block";
        } else {
            menu.children[0].style.display = "block";
            menu.children[1].style.display = "none";
        }

        if (window.innerWidth <= 320) {
            barraLateral.classList.add("mini-barra-lateral");
            main.classList.add("min-main");
            spans.forEach((span) => {
                span.classList.add("oculto");
            });
        }
    });

    // Agregar evento para el icono de la barra lateral
    icon.addEventListener("click", () => {
        barraLateral.classList.toggle("mini-barra-lateral");
        main.classList.toggle("min-main");
        spans.forEach((span) => {
            span.classList.toggle("oculto");
        });
    });

    // Agregar eventos para los enlaces en la barra lateral
    itemBarraLateral.forEach((item) => {
        item.addEventListener('click',(evento)=>{

            
        
            
        })
    });

    // Funcionalidad de logout
    const logout = document.getElementById("logout");
    if (logout) {
        logout.addEventListener("click", (event) => {
            event.preventDefault(); // Evita la recarga de la página
            window.location.href = "/"; // Redirige al logout
        });
    } else {
        console.log("Elemento de logout no encontrado");
    }
});
botonLateral.addEventListener("click",()=>{
       
}
)

// Confirmación antes de eliminar (versión mejorada)
document.addEventListener('DOMContentLoaded', function() {
    // Manejar todos los formularios de eliminación
    document.querySelectorAll('form[action^="/eliminar_actividad"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar esta actividad permanentemente?')) {
                e.preventDefault();
            }
        });
    });
});
