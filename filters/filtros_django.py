#!/usr/bin/env python

import hashlib, random, urllib
from django.utils.safestring import mark_safe
from google.appengine.ext import webapp
from datetime import datetime

register = webapp.template.create_template_register()

@register.filter
def cortamail(email):
    if email:
        return str(email).split('@')[0]
    else:
        return 'anonimo'

@register.filter
def menu_cabecera(vista, seleccion=''):
    if vista == seleccion:
        return mark_safe('id="menusel"')
    else:
        return ''

@register.filter
def avatar(email, size=80):
    imagen = '<img src="/img/anonymous.gif" alt="anonymous" />'
    if email:
        imagen = '<img src="http://www.gravatar.com/avatar/' + hashlib.md5(str(email)).hexdigest()
        imagen += '?s=' + str(size) + '&amp;d=' + urllib.quote('http://www.ubufaq.com/img/guy-' + str(size) + '.jpg')
        imagen += '" alt="avatar" />'
    elif size == 40:
        imagen = '<img src="/img/anonymous-40.gif" alt="anonymous" />'
    return mark_safe(imagen)

@register.filter
def karmsg(puntos):
    texto = 'este usuario ya dispone de su propio ej&eacute;rcito: &iexcl;' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    if puntos < 5:
        texto = 'usuario poco participativo...'
    elif puntos < 25:
        texto = '&iexcl;Ha salvado a ' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    return mark_safe(texto)

@register.filter
def puntos(puntos):
    if puntos > 1:
        return mark_safe('<a href="/ayuda#karma">' + str(puntos) + '</a>')
    else:
        return ''

@register.filter
def estado_pregunta(estado):
    retorno = 'estado desconocido'
    if estado == 0:
        retorno = 'nueva'
    elif estado == 1:
        retorno = 'incompleta'
    elif estado == 2:
        retorno = 'abierta'
    elif estado == 3:
        retorno = 'parcialmente solucionada'
    elif estado == 10:
        retorno = 'solucionada'
    elif estado == 11:
        retorno = 'pendiente de confirmaci&oacute;n'
    elif estado == 12:
        retorno = 'duplicada'
    elif estado == 13:
        retorno = 'erronea'
    elif estado == 14:
        retorno = 'antigua'
    return mark_safe(retorno)

@register.filter
def muestra_os(os):
    salida = '<span title="' + os + '">' + os[:30] + '</span>'
    if os.lower().find('android') != -1:
        salida = '<span title="' + os + '">Android</span>'
    elif os.lower().find('linux') != -1:
        salida = '<span title="' + os + '">Linux</span>'
    elif os.lower().find('windows') != -1:
        salida = '<span title="' + os + '">Windows</span>'
    elif os.lower().find('ipod') != -1:
        salida = '<span title="' + os + '">iPod</span>'
    elif os.lower().find('ipad') != -1:
        salida = '<span title="' + os + '">iPad</span>'
    elif os.lower().find('iphone') != -1:
        salida = '<span title="' + os + '">iPhone</span>'
    elif os.lower().find('mac') != -1:
        salida = '<span title="' + os + '">Mac</span>'
    return mark_safe(salida)

@register.filter
def miniatura(url):
    mini = '<img class="galeria" src="' + str(url) + '" alt="imagen"/>'
    if url[:19] == 'http://i.imgur.com/':
        aux = str(url).split('.')
        mini = '<img class="galeria" src="http://i.imgur.' + aux[2] + 's.' + aux[3] + '" width="180" alt="imagen"/>'
    return mark_safe(mini)

@register.filter
def sin_solucionar(preguntas, respuestas):
    texto = '<ul>'
    estado = -1
    primera = True
    for p in preguntas:
        if p.estado != estado:
            # agrupamos por estado
            if primera:
                primera = False
            else:
                texto += '</ul><br/>'
            estado = p.estado
            
            # mostramos el estado
            if estado == 0:
                texto += '<li><b>Preguntas nuevas</b>:</li>\n'
            elif estado == 1:
                texto += '<li><b>Preguntas incompletas</b>:</li>\n'
            elif estado == 2:
                texto += '<li><b>Preguntas abiertas</b>:</li>\n'
            elif estado == 3:
                texto += '<li><b>Preguntas parcialmente solucionadas</b>:</li>\n'
            texto += '<ul>'
        
        # titulo de la pregunta
        texto += '<li>' + p.creado.strftime("%d/%m/%Y") + ', '
        texto += '<b>' + cortamail(p.autor) + '</b> pregunta: '
        texto += '<a href="/question/' + str(p.key()) + '" title="' + p.contenido + '\n\n' + str(p.respuestas) + ' respuestas">' + p.titulo + '</a></li>\n'
        
        # respuestas
        texto += '<ul>'
        for r in respuestas:
            if r.id_pregunta == str(p.key()):
                texto += '<li><a href="/question/' + str(p.key()) + '#' + str(r.key()) + '">' + r.fecha.strftime("%d/%m/%Y") + '</a> <b>' + cortamail(r.autor) + '</b> responde - ' + r.contenido[:99] + '</li>\n'
        texto += '</ul>'
    
    # cerramos etiquetas
    if primera:
        texto += '</ul>'
    else:
        texto += '</ul></ul>'
    return mark_safe(texto)

@register.filter
def paginar(datos):
    texto = '<div class="paginacion"><span>' + str(datos[0]) + ' p&aacute;ginas</span>\n'
    
    # primera
    if datos[1] > 0:
        texto += '<span><a href="' + datos[2] + '0">&lt;&lt; primera</a></span>\n'
    
    # anteriores
    for pag in range(datos[1] - 5, datos[1]):
        if pag >= 0:
            texto += '<span><a href="' + datos[2] + str(pag) + '">' + str(pag) + '</a></span>\n'
    
    # actual
    texto += '<span id="actual"><a href="' + datos[2] + str(datos[1]) + '">' + str(datos[1]) + '</a></span>\n'
    
    # siguientes
    for pag in range(datos[1] + 1, datos[1] + 6):
        if pag < datos[0]:
            texto += '<span><a href="' + datos[2] + str(pag) + '">' + str(pag) + '</a></span>\n'
    
    # ultima
    if datos[1] < (datos[0] - 1):
        texto += '<span><a href="' + datos[2] + str(datos[0] - 1) + '">&uacute;ltima &gt;&gt;</a></span>\n'
    
    texto += '</div>'
    
    if datos[0] > 1:
        return mark_safe(texto)
    else:
        return ''

