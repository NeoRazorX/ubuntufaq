#!/usr/bin/env python

import hashlib, random, urllib
from google.appengine.ext import webapp
from datetime import datetime


register = webapp.template.create_template_register()


def cortamail(email):
    return str(email).split('@')[0]


def menu_cabecera(vista, seleccion=''):
    if vista == seleccion:
        return 'id="menusel"'
    else:
        return ''


def avatar(email, size=80):
    if email:
        return '<img src="http://www.gravatar.com/avatar/' + hashlib.md5(str(email)).hexdigest() + '?s=' + str(size) + '" alt="avatar" />'
    elif size == 40:
        return '<img src="/img/anonymous-40.gif" alt="anonymous" />'
    else:
        return '<img src="/img/anonymous.gif" alt="anonymous" />'


def karmsg(puntos):
    if puntos < 5:
        return 'usuario poco participativo...'
    elif puntos < 25:
        return '&iexcl;Ha salvado a ' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    else:
        return 'este usuario ya dispone de su propio ej&eacute;rcito: &iexcl;' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'


def puntos(puntos):
    if puntos > 1:
        return '<a href="/ayuda#karma">' + str(puntos) + '</a>'
    else:
        return ''


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
    
    return retorno


def randomsg(enlaces):
    retorno = '<a href="/actualidad#nuevo-enlace"><img src="/img/tux-want-you.png" alt="actualidad" title="Tux dice que compartas con nosotros enlaces de inter&eacute;s: un v&iacute;deo, una foto, un art&iacute;culo, un blog, etc."/></a>'
    for enl in enlaces:
        if enl.tipo_enlace == 'imagen' and random.randint(0, 1) == 0:
            retorno = '<a href="/images">' + miniatura(enl.url) + '</a>'
        elif enl.tipo_enlace == 'youtube' and random.randint(0, 1) == 0:
            retorno = '<iframe title="YouTube video player" class="youtube-player" type="text/html" width="320" height="265" src="http://www.youtube.com/embed/' + enl.url.split('?v=')[1] + '" frameborder="0"></iframe><br/><a href="/story/' + str(enl.key()) + '">comentarios</a>'
    return retorno

def muestra_os(os):
    if os.lower().find('android') != -1:
        return '<span title="' + os + '">Android</span>'
    elif os.lower().find('linux') != -1:
        return '<span title="' + os + '">Linux</span>'
    elif os.lower().find('windows') != -1:
        return '<span title="' + os + '">Windows</span>'
    elif os.lower().find('ipod') != -1:
        return '<span title="' + os + '">iPod</span>'
    elif os.lower().find('ipad') != -1:
        return '<span title="' + os + '">iPad</span>'
    elif os.lower().find('iphone') != -1:
        return '<span title="' + os + '">iPhone</span>'
    elif os.lower().find('mac') != -1:
        return '<span title="' + os + '">Mac</span>'
    else:
        return '<span title="' + os + '">' + os[:30] + '</span>'

def miniatura(url):
    if url[:19] == 'http://i.imgur.com/':
        aux = str(url).split('.')
        return '<img class="galeria" src="http://i.imgur.' + aux[2] + 's.' + aux[3] + '" width="180" alt="imagen"/>'
    else:
        return '<img class="galeria" src="http://api.thumbalizr.com/?url=' + urllib.quote( str(url) ) + '" alt="imagen"/>'

register.filter( cortamail )
register.filter( menu_cabecera )
register.filter( avatar )
register.filter( karmsg )
register.filter( puntos )
register.filter( estado_pregunta )
register.filter( randomsg )
register.filter( muestra_os )
register.filter( miniatura )

