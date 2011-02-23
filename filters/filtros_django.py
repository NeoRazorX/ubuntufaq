#!/usr/bin/env python

import hashlib, random, urllib
from django.utils.safestring import mark_safe
from google.appengine.ext import webapp
from datetime import datetime

register = webapp.template.create_template_register()

@register.filter
def cortamail(email):
    return str(email).split('@')[0]

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
    mini = '<img class="galeria" src="http://api.thumbalizr.com/?url=' + urllib.quote( str(url) ) + '" alt="imagen"/>'
    if url[:19] == 'http://i.imgur.com/':
        aux = str(url).split('.')
        mini = '<img class="galeria" src="http://i.imgur.' + aux[2] + 's.' + aux[3] + '" width="180" alt="imagen"/>'
    return mark_safe(mini)

