var TXT="Que se desea administrar?";

function GetData(P) {
    var D={};
    var url     = 'http://192.16.10.39/constinfoclientesiemens/getdata.php';
    var data    = new FormData();
    data.append("GetData", P);//construc de la data a enviar
    //Construccion de la peticion
    var requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    };

    //Realizar peticion
    console.log(url);
    fetch(url, requestOptions).then(response => response.text()).then(result => {
        if (result==="{}"){
            console.log("No Data");
        }
        else{
           //D = JSON.parse(result.replace(/_/g, " "));
           console.log(result);
           return result;
            //Recorre los posibles grupos de datos
//            for (var key in D) {
//                var FT="<tr><td>"+D[key].DO+"</td><td>"+D[key].FechaManifiesto+"</td><td>"+D[key].CustomClearanceDate+"</td><td><button onclick=\"NoPo(this)\" class=\"btn btn-warning\" type=\"button\" id=\""+key+"\">No P.O</button></td><td><button onclick=\"Avisos(this)\" class=\"btn btn-dark\" type=\"button\" id=\""+key+"\">AVISOS</button></td><td><button onclick=\"Comentarios(this)\" class=\"btn btn-primary\" type=\"button\" id=\""+key+"\">COMENTARIOS</button></td></tr>";
//                $("#T").show();
//                $("#DT").append(FT);
//            }
        }
        
        
    }).catch(error => {
        console.error('Error:', error);
        return false;
    });
       
    
}


function textos(S){
    switch(S){
        case "HISTORIAL":
            $("#TXT").text("Revisa la actividad que han tenido los clientes y otro tipo de usuarios al interactuar con el API de consultas");
        break;
        case "USUARIOS":
            $("#TXT").text("Administra los usuarios de quienes interactúan con este API de consultas");
        break;
        case "OPERACIONES":
            $("#TXT").text("Administra los métodos y las conexiones que estos mismos realizan");
        break;
        case "EMPRESAS":
            $("#TXT").text("Revisa o modifica las filiares de nuestros clientes");
        break;
        case "AGREGAR USUARIO":
            $("#TXT").text("El nuevo usuario debe ser vinculado a una empresa previamente creada e interactuara con métodos del API previamente creados.");
        break;
        case "AGREGAR METODO":
            $("#TXT").text("Incorporar y parametrizar un nuevo par de datos que se usara en el cuerpo de la petición (parámetro : Valor).");
        break;
        case "AGREGAR EMPRESA":
            $("#TXT").text("Incorporar una nueva empresa para asociarla con un usuario");
        break;
    }
}

function IrA(S){
    
    HTML="";
    S=S.replace("AGREGAR ","");
    switch(S){
        case "USUARIOS":
            S="USUARIO";
        break;
        case "OPERACIONES":
            S="METODO";
        break;
        case "EMPRESAS":
            S="EMPRESA";
        break;
        case "USUARIO":
            HTML=`
                <input type="text" id="usr" class="swal2-input" placeholder="USUARIO">
                <input type="password" id="psw" class="swal2-input" placeholder="CONTRASEÑA">
                <select id="empresa"></select>
            `;
        break;
        case "EMPRESA":
            D=GetData(S);
            HTML=`
                <input type="text" id="nit" class="swal2-input" placeholder="NIT">
                <input type="text" id="nombre" class="swal2-input" placeholder="NOMBRE">
            `;
        break;
    }
    if (S==="<-"){
        $("#M").html("<tbody><tr><td>USUARIOS</td></tr><tr><td>OPERACIONES</td></tr><tr><td>EMPRESAS</td></tr><tr><td>HISTORIAL</td></tr></tbody>");  
        TXT = "Que desea administrar?";
    }
    else if(S==="HISTORIAL"){
        $("#M").html("<tbody><tr><td><-</td></tr></tbody>");
        TXT = "La información que aparece a continuación es solo para consulta (la tabla solo trae hasta 100 datos).";
    }
    else if(S==="AGREGAR USUARIO" || S==="AGEGAR METODO" || S==="AGREGAR EMPRESA"){
        Swal.fire({
            title:"NUEVO"+S,
            html:HTML,
            confirmButtonText: 'Enviar',
            showCancelButton: true,
            focusConfirm: false
        }).then(function(result){
            if(result.value){
                Swal.fire('Los datos se han guardado', '', 'success')
            }
        });
    }
    else{
        $("#M").html("<tbody><tr><td><-</td></tr><tr><td>AGREGAR "+S+"</td></tr></tbody>");
        TXT = "Consultar o editar la información con ayuda de la tabla que aparece a continuación (la tabla solo trae hasta 100 datos).";
    }
    $("#TXT").text(TXT);
    
}


$(document).ready(function () {
    //GetData();
    
    $("#M").on("mouseenter","tr",function(){
        var S = $(this).text();
        textos(S);
    });    
    $("#M").on("mouseleave","tr",function(){
        $("#TXT").text(TXT);
    });
    
    $("#M").on("click","tr",function(){
        var OPT = $(this).text();
        IrA(OPT);
    });
    
});





























function NoPo(boton) {
    s = D[boton.id].PONumber;
    S = s.replace(/-/g,"</td></tr><tr><td>");
    Swal.fire({
        width: '80%',
        height: '80%',
        title: 'No P.O.',
        html: "<table class=\"table\"><tbody><tr><td>"+S+"</td></tr></tbody></table>",
        customClass: {
            container: 'scrollable-swal',
            confirmButton: 'btn-warning'
        },
        confirmButtonText: 'Salir'
    });
}

function Avisos(boton) {
    s = D[boton.id].Avisos;
    S = s.replace(/\/\//g,"</td></tr><tr><td>");
    Swal.fire({
        width: '80%',
        height: '80%',
        title: 'AVISOS',
        html: "<table class=\"table table-dark\"><tbody><tr><td>"+S+"</td></tr></tbody></table>",
        customClass: {
            container: 'scrollable-swal',
            confirmButton: 'btn-warning'
        },
        confirmButtonText: 'Salir'
    });
}

function Comentarios(boton) {
    s = D[boton.id].Comments;
    S = s.replace(/\/\//g,"</td></tr><tr><td>");
    Swal.fire({
        width: '80%',
        height: '80%',
        title: 'COMENTARIOS',
        html: "<table class=\"table table-dark2\"><tbody><tr><td>"+S+"</td></tr></tbody></table>",
        customClass: {
            container: 'scrollable-swal',
            confirmButton: 'btn-warning'
        },
        confirmButtonText: 'Salir'
    });
}