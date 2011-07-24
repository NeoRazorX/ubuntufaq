
function menu_cabecera(eleccion)
{
    document.getElementById('menupregunta').setAttribute("class", "caca");
    document.getElementById('menuenlace').setAttribute("class", "caca");
    document.getElementById('menubuscar').setAttribute("class", "caca");
    document.getElementById('menumapa').setAttribute("class", "caca");
    document.getElementById('pregunta').style.display = 'none';
    document.getElementById('enlace').style.display = 'none';
    document.getElementById('buscar').style.display = 'none';
    document.getElementById('buscar2').style.display = 'none';
    document.getElementById('mapa').style.display = 'none';
    
    switch( eleccion )
    {
        case 'enlace':
            document.getElementById('menuenlace').setAttribute("class", "menusel");
            document.getElementById('enlace').style.display = 'block';
            break;
        
        case 'buscar':
            document.getElementById('menubuscar').setAttribute("class", "menusel");
            document.getElementById('buscar').style.display = 'block';
            document.getElementById('buscar2').style.display = 'block';
            break;
        
        case 'mapa':
            document.getElementById('menumapa').setAttribute("class", "menusel");
            document.getElementById('mapa').style.display = 'block';
            break;
        
        default:
            document.getElementById('menupregunta').setAttribute("class", "menusel");
            document.getElementById('pregunta').style.display = 'block';
            break;
    }
}

function enviar_pregunta()
{
    var titulo = document.publicar.titulo.value;
    var contenido = document.publicar.contenido.value;
    var mensaje;
    var continuar = true;
    
    if(titulo == '' || titulo == "¡Haz tu pregunta!")
    {
        continuar = false;
        mensaje = "¡Debes modificar el título!";
        document.publicar.titulo.focus();
        document.publicar.titulo.select();
    }
    else if(contenido == '' || contenido == "¡Haz tu pregunta!")
    {
        continuar = false;
        mensaje = "¡Debes modificar la descripción!";
        document.publicar.contenido.focus();
        document.publicar.contenido.select();
    }
    
    if(continuar)
    {
        document.publicar.action = '/add_p';
        document.publicar.submit();
    }
    else
    {
        alert( mensaje );
    }
}

function enviar_enlace()
{
    var url = document.publicar.url.value;
    var descripcion = document.publicar.descripcion.value;
    var mensaje;
    var continuar = true;
    
    if(url == '' || url == 'http://')
    {
        continuar = false;
        mensaje = "¡Debes modificar la URL del enlace!";
        document.publicar.url.focus();
        document.publicar.url.select();
    }
    else if(descripcion == '' || descripcion == "Descripción del enlace (450 caracteres max.).")
    {
        continuar = false;
        mensaje = "¡Debes modificar la descripción!";
        document.publicar.descripcion.focus();
        document.publicar.descripcion.select();
    }
    else if(descripcion.length > 450)
    {
        continuar = false;
        mensaje = "¡La descripción del enlace es demasiado larga! Max. 450 caracteres, actual=" + descripcion.length;
        document.publicar.descripcion.focus();
        document.publicar.descripcion.select();
    }
    
    if(continuar)
    {
        document.publicar.action = '/add_e';
        document.publicar.submit();
    }
    else
    {
        alert( mensaje );
    }
}

function enviar_respuesta()
{
    if(document.respuesta.contenido.value != '') {
        document.respuesta.submit();
    }
    else
    {
        alert('¡Escribe algo!');
        document.respuesta.contenido.focus();
        document.respuesta.contenido.select();
    }
}

function enviar_comentario()
{
    if(document.comentario.contenido.value != '')
    {
        document.comentario.submit();
    }
    else
    {
        alert('¡Escribe algo!');
        document.comentario.contenido.focus();
        document.comentario.contenido.select();
    }
}

function hundir_enlace(id)
{
    if( confirm('¿Realmente desea hundir el enlace?') )
    {
        window.location.href = '/hun_e?id=' + id;
    }
}

function borrar_pregunta(id)
{
    if( confirm('¿Realmente desea eliminar la pregunta?') )
    {
        window.location.href = '/del_p?id=' + id;
    }
}

function borrar_respuesta(id, r)
{
    if( confirm('¿Realmente desea eliminar la respuesta?') )
    {
        window.location.href = '/del_r?id=' + id + '&r=' + r;
    }
}

function borrar_enlace(id)
{
    if( confirm('¿Realmente desea eliminar el enlace?') )
    {
        window.location.href = '/del_e?id=' + id;
    }
}

function borrar_comentario(id, c)
{
    if( confirm('¿Realmente desea eliminar el comentario?') )
    {
        window.location.href = '/del_c?id=' + id + '&c=' + c;
    }
}

function enviar_privado()
{
    var texto = document.privado.texto.value;
    var mensaje;
    var continuar = true;
    
    if(texto == '')
    {
        continuar = false;
        mensaje = "¡Escribe algo!";
        document.privado.texto.focus();
        document.privado.texto.select();
    }
    else if(texto.length > 450)
    {
        continuar = false;
        mensaje = "¡El texto es demasiado larga! Max. 450 caracteres, actual=" + texto.length;
        document.privado.texto.focus();
        document.privado.texto.select();
    }
    
    if(continuar)
    {
        document.privado.submit();
    }
    else
    {
        alert( mensaje );
    }
}
