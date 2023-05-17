'use strict';

const pantallas = [
    {
        "id": "botonera",
        "template": "botonera",
        "button_filter": ".boton-menu",
        "callback_click": click_boton,
        "context_tiles": ["titulo"]
    },
    {
        "id": "lockscreen",
        "template": "lockscreen"
    }
];

const contexto = [
    {
        "id": "titulo",
        "container": ".barra-titulo",
        "template": "titulo",
        "template_data_callback": popular_titulo,
        "callback_show": function(){
            document.querySelector(".barra-titulo").style.display = 'block';
        },
        "callback_hide": function(){
            document.querySelector(".barra-titulo").style.display = 'none';
        }
    }
];
