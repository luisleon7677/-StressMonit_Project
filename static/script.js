document.addEventListener("DOMContentLoaded", function () {
    const icon = document.getElementById("main-icon");
    let itemBarraLateral = document.querySelectorAll("nav.navegacion > ul > li > a");
    const barraLateral = document.querySelector(".barra-lateral");
    const spans = document.querySelectorAll("span");
    const menu = document.querySelector(".menu");
    const main = document.querySelector("main");

    // Agregar evento para el menú lateral
    menu.addEventListener("click", () => {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            barraLateral.classList.toggle("active");
            // Toggle icons for mobile
            const menuIcon = menu.querySelector('ion-icon[name="menu-outline"]');
            const closeIcon = menu.querySelector('ion-icon[name="close-outline"]');
            if (menuIcon && closeIcon) {
                if (barraLateral.classList.contains("active")) {
                    menuIcon.style.display = "none";
                    closeIcon.style.display = "block";
                } else {
                    menuIcon.style.display = "block";
                    closeIcon.style.display = "none";
                }
            }
        } else {
            barraLateral.classList.toggle("mini-barra-lateral");
            main.classList.toggle("min-main");

            // Adjust barra-secundaria if it exists
            const barraSecundaria = document.querySelector(".barra-secundaria");
            if (barraSecundaria) {
                if (barraLateral.classList.contains("mini-barra-lateral")) {
                    barraSecundaria.style.left = "80px";
                    barraSecundaria.style.width = "calc(100% - 80px)";
                } else {
                    barraSecundaria.style.left = "260px";
                    barraSecundaria.style.width = "calc(100% - 260px)";
                }
            }
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
        item.addEventListener('click', (evento) => {




        })
    });

    // Funcionalidad de logout
    const logout = document.getElementById("logout");
    if (logout) {
        logout.addEventListener("click", (event) => {
            event.preventDefault(); // Evita la recarga de la página
            window.location.href = "/logout"; // Redirige al logout
        });
    } else {
        console.log("Elemento de logout no encontrado");
    }
});

// Confirmación antes de eliminar (versión mejorada)
document.addEventListener('DOMContentLoaded', function () {
    // Manejar todos los formularios de eliminación
    document.querySelectorAll('form[action^="/eliminar_actividad"]').forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm('¿Estás seguro de que quieres eliminar esta actividad permanentemente?')) {
                e.preventDefault();
            }
        });
    });
});


