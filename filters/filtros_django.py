#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of ubuntufaq
# Copyright (C) 2011  Carlos Garcia Gomez  neorazorx@gmail.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib, random, urllib
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatewords, linebreaksbr, urlize
from google.appengine.ext import webapp
from datetime import datetime

register = webapp.template.create_template_register()

@register.filter
def cortamail(email=None):
    if email:
        return str(email).split('@')[0]
    else:
        return 'anonimo'

@register.filter
def autor(a=None):
    if a:
        try:
            return mark_safe('<a href="/u/'+urllib.quote(a.email())+'">'+cortamail(a.nickname())+'</a>')
        except:
            return a
    else:
        return 'anónimo'

@register.filter
def tags(cadena=None):
    retorno = ''
    if cadena:
        ts = cadena.split(', ')
        for t in ts:
            if retorno != '':
                retorno += ', '
            retorno += '<a href="/tag/' + t + '">' + t + '</a>'
    return mark_safe(retorno)

@register.filter
def alltags(tags):
    retorno = ''
    if tags:
        tmax = 0
        tmin = 100
        for t in tags:
            tmax = max(tmax, t[1])
            tmin = min(tmin, t[1])
        tags.sort(key=lambda a: a[0].lower())
        for t in tags:
            if retorno != '':
                retorno += ' '
            if t[1] == tmin:
                retorno += '<a class="min" title="' + str(t[1]) + '" href="/tag/' + t[0] + '">' + t[0] + '</a>'
            elif t[1] == tmax:
                retorno += '<a class="max" title="' + str(t[1]) + '" href="/tag/' + t[0] + '">' + t[0] + '</a>'
            else:
                retorno += '<a title="' + str(t[1]) + '" href="/tag/' + t[0] + '">' + t[0] + '</a>'
    return mark_safe('<div class="alltags">'+retorno+'</div>')

@register.filter
def traducir(fecha):
    texto = str(fecha)
    texto = texto.replace('hour', 'hora')
    texto = texto.replace('minute', 'minuto')
    texto = texto.replace('day', 'día')
    texto = texto.replace('week', 'semana')
    texto = texto.replace('months', 'meses')
    texto = texto.replace('month', 'mes')
    texto = texto.replace('year', 'año')
    return mark_safe(texto)

@register.filter
def menu_cabecera(vista, seleccion=''):
    if vista == seleccion:
        return mark_safe('id="menusel"')
    else:
        return ''

@register.filter
def avatar(email=None, size=80):
    imagen = '<img src="/img/anonymous.gif" alt="anonymous" />'
    if email:
        imagen = '<img src="http://www.gravatar.com/avatar/' + hashlib.md5(str(email)).hexdigest()
        imagen += '?s=' + str(size) + '&amp;d=' + urllib.quote('http://www.ubufaq.com/img/guy-' + str(size) + '.jpg')
        imagen += '" alt="avatar" />'
    elif size == 40:
        imagen = '<img src="/img/anonymous-40.gif" alt="anonymous" />'
    return mark_safe(imagen)

@register.filter
def karmsg(puntos=0):
    texto = 'este usuario ya dispone de su propio ejército: &iexcl;' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    if puntos < 5:
        texto = 'usuario poco participativo...'
    elif puntos < 25:
        texto = '&iexcl;Ha salvado a ' + str(puntos) + ' <a href="/ayuda#gatitos">gatitos</a>!'
    return mark_safe(texto)

@register.filter
def puntos(puntos=0):
    if puntos > 1:
        return mark_safe('<a href="/ayuda#karma">' + str(puntos) + '</a>')
    else:
        return ''

@register.filter
def estado_pregunta(estado=0):
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
        retorno = 'pendiente de confirmación'
    elif estado == 12:
        retorno = 'duplicada'
    elif estado == 13:
        retorno = 'erronea'
    elif estado == 14:
        retorno = 'antigua'
    return mark_safe(retorno)

@register.filter
def muestra_os(ua=''):
    if ua == 'rss-scanner.py':
        return ua
    else:
        os = 'unknown'
        browser = 'unknown'
        # detecting os
        for aux in ['mac', 'iphone', 'ipad', 'ipod', 'windows', 'linux', 'android']:
            if ua.lower().find( aux ) != -1:
                os = aux
        # detecting browser
        for aux in ['safari', 'opera', 'chrome', 'firefox', 'explorer']:
            if ua.lower().find( aux ) != -1:
                browser = aux
        return mark_safe('<span title="' + ua + '">' + os + '+' + browser + '</span>')

@register.filter
def miniatura(url=''):
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
                texto += '<li><a href="/question/' + str(p.key()) + '#' + str(r.key()) + '">' + r.fecha.strftime("%d/%m/%Y") + '</a> <b>' + cortamail(r.autor) + '</b> responde - ' + truncatewords(r.contenido, 20) + '</li>\n'
        texto += '</ul>'
    
    # cerramos etiquetas
    if primera:
        texto += '</ul>'
    else:
        texto += '</ul></ul>'
    return mark_safe(texto)


@register.filter
def ultimas_respuestas(pregunta, respuestas):
    if respuestas:
        retorno = '<ul>'
        for r in respuestas:
            if r.id_pregunta == str(pregunta):
                retorno += '<li><b>' + cortamail(r.autor) + '</b> responde: ' + truncatewords(r.contenido, 20) + "</li>\n"
        return mark_safe(retorno+'</ul>')
    else:
        return ''


@register.filter
def respuestas_destacadas(respuestas):
    if respuestas:
        retorno = ''
        for r in respuestas:
            if r.destacada:
                if retorno == '':
                    retorno = '<tr><td colspan="2" valign="top"><div class="info_respuesta_d"><b>Respuestas destacadas:</b></div>'
                retorno += '<div class="respuesta_d">' + urlize(linebreaksbr(r.contenido)) + '</div>'
        retorno += '</td></tr><tr><td colspan="2">&nbsp;</td></tr>'
        return mark_safe(retorno)
    else:
        return ''


@register.filter
def tipo_enlace(enlace):
    retorno = ''
    if enlace.tipo_enlace == None:
        if enlace.url[:23] == 'http://www.youtube.com/':
            tipo_enlace = 'youtube'
        elif enlace.url[:21] == 'http://www.vimeo.com/':
            tipo_enlace = 'vimeo'
        elif enlace.url[-4:] in ['.ogv', '.OGV', '.mp4', '.MP4'] or enlace.url[-5:] in ['.webm', '.WEBM']:
            tipo_enlace = 'vhtml5'
        elif enlace.url[-4:] in ['.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF'] or enlace.url[-5:] in ['.jpeg', '.JPEG']:
            tipo_enlace = 'imagen'
        elif enlace.url[-4:] in ['.deb', '.DEB']:
            tipo_enlace = 'deb'
        elif enlace.url[-4:] in ['.deb', '.DEB', '.tgz', '.TGZ', '.bz2', '.BZ2'] or enlace.url[-3:] in ['.gz', '.GZ']:
            tipo_enlace = 'package'
    if enlace.tipo_enlace == 'texto':
        if enlace.autor:
            retorno = '<div class="avatar">'+avatar(enlace.autor.email())+'<br/>'+puntos(enlace.puntos)+'</div>'
        else:
            retorno = '<div class="avatar">'+avatar()+'<br/>'+puntos(enlace.puntos)+'</div>'
    elif enlace.tipo_enlace == 'youtube':
        retorno = '<iframe title="YouTube video player" class="youtube-player" type="text/html" width="425" height="349" src="http://www.youtube.com/embed/'+enlace.url.split('?v=')[1]+'" frameborder="0"></iframe>'
    elif enlace.tipo_enlace == 'vimeo':
        retorno = '<iframe src="http://player.vimeo.com/video/'+enlace.url.split('/')[3]+'" width="400" height="300" frameborder="0"></iframe>'
    elif enlace.tipo_enlace == 'vhtml5':
        retorno = '<video src="'+enlace.url+'" controls="controls">¡Tu navegador no soporta el tag de vídeo en html5!</video>'
    elif enlace.tipo_enlace == 'imagen':
        retorno = '<a href="'+enlace.url+'" target="_Blank">'+miniatura(enlace.url)+'</a></center>'
    elif enlace.tipo_enlace == 'deb':
        retorno = '<a href="'+enlace.url+'"><img src="/img/application-x-deb.png" alt="'+enlace.descripcion+'"/></a>'
    elif enlace.tipo_enlace == 'package':
        retorno = '<a href="'+enlace.url+'"><img src="/img/emblem-package.png" alt="'+enlace.descripcion+'" title="clic para descargar"/></a>'
    return mark_safe(retorno)


@register.filter
def paginar(datos):
    texto = '<div class="paginacion"><span>' + str(datos[0]) + ' páginas</span>\n'
    
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
        texto += '<span><a href="' + datos[2] + str(datos[0] - 1) + '">última &gt;&gt;</a></span>\n'
    
    texto += '</div>'
    
    if datos[0] > 1:
        return mark_safe(texto)
    else:
        return mark_safe("")

