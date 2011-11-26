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

import hashlib, urllib, base64, math, re, logging
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatewords, linebreaksbr, urlize
from google.appengine.ext import webapp
from datetime import datetime

register = webapp.template.create_template_register()

@register.filter
def fuckcode(value):
    bbdata = [
        (r'\[b\](.+?)\[/b\]', r'<b>\1</b>'),
        (r'\[i\](.+?)\[/i\]', r'<i>\1</i>'),
        (r'\[u\](.+?)\[/u\]', r'<u>\1</u>'),
        (r'\[code\](.+?)\[/code\]', r'<div class="codigo">\1</div>'),
        (r'\[big\](.+?)\[/big\]', r'<big>\1</big>'),
        (r'\[small\](.+?)\[/small\]', r'<small>\1</small>')
    ]
    for bbset in bbdata:
        p = re.compile(bbset[0], re.DOTALL)
        value = p.sub(bbset[1], value)
    # links
    p = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.DOTALL)
    value = p.sub(urlizer, value)
    # mentions
    aux_mentions = re.findall(r'@[0-9]+\b', value)
    for mention in aux_mentions:
        value = value.replace(mention, '<a href="#'+mention[1:]+'">'+mention+'</a>')
    return mark_safe(value)

@register.filter
def urlizer(link):
    if link.group(0)[-4:].lower() in ['.jpg', '.gif', '.png'] or link.group(0)[-5:].lower() in ['.jpeg']:
        return '<a target="_Blank" href="'+link.group(0)+'">'+miniatura(link.group(0))+'</a>'
    elif link.group(0)[:31] == 'http://www.youtube.com/watch?v=':
        return '<div><iframe width="420" height="345" src="http://www.youtube.com/embed/' + link.group(0).split('?v=')[1] + '" frameborder="0" allowfullscreen></iframe></div>'
    else:
        return '<a target="_Blank" href="' + link.group(0) + '">' + link.group(0) + '</a>'

@register.filter
def resalta_tag(texto, tag):
    if texto:
        return mark_safe( texto.lower().replace(tag, '<u>'+tag+'</u>') )
    else:
        return ''

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
            return mark_safe('<a href="/u/'+urllib.quote(base64.b64encode(a.email()))+'">'+cortamail(a.nickname())+'</a>')
        except:
            return a
    else:
        return 'anónimo'

@register.filter
def tag(value, t=0, c=0):
    if value:
        if t == 3:
            return mark_safe('<a class="max" title="' + str(c) + '" class="tag" href="/search/' + value + '">' + value + '</a>')
        elif t == 2:
            return mark_safe('<a class="min" title="' + str(c) + '" class="tag" href="/search/' + value + '">' + value + '</a>')
        elif t == 1:
            return mark_safe('<a title="' + str(c) + '" href="/search/' + value + '">' + value + '</a>')
        else:
            return mark_safe('<a class="tag" href="/search/' + value + '">' + value + '</a>')
    else:
        return ''

@register.filter
def tags(cadena=None):
    retorno = ''
    if cadena:
        ts = cadena.split(', ')
        for t in ts:
            if retorno != '':
                retorno += ', '
            retorno += tag(t)
    return mark_safe(retorno)

@register.filter
def alltags(tags):
    retorno = ''
    vtags = []
    if tags:
        for t in tags:
            if t[1] > 0:
                vtags.append(t)
    if vtags:
        tmedia = 0
        for t in vtags:
            tmedia += t[1]
        try:
            tmedia = tmedia / len(tags)
        except:
            tmedia = 10
        vtags.sort(key=lambda a: a[0].lower())
        for t in vtags:
            if retorno != '':
                retorno += ' '
            if t[1] < tmedia:
                retorno += tag(t[0], 2, t[1])
            elif t[1] > tmedia:
                retorno += tag(t[0], 3, t[1])
            else:
                retorno += tag(t[0], 1, t[1])
        return mark_safe('<div class="alltags">'+retorno+'</div>')
    else:
        return mark_safe('<div class="mensaje">Sin resultados.</div>')

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
    texto = 'usuario poco participativo ... ¿Un zombi quizás?'
    if puntos >= 19:
        texto = 'fuente ilimitada de karma, máquina insaciable de conocimientos ... ojalá todos os parecieseis a él ¿Qué? ¿Lo he dicho en voz alta?'
    elif puntos >= 15:
        texto = 'cerebro incansable, a ' + str(20 - puntos) + ' puntos de la perfección.'
    elif puntos >= 10:
        texto = 'mente despierta ... ¡Despierta! ¡Tienes que enviar más enlaces! Esta web no se mantiene sola ¿O si?'
    elif puntos >= 6:
        texto = 'lee, escribe, piensa ... ¿Cuándo piensa enviar algún enlace interesante?'
    elif puntos >= 2:
        texto = 'necesita mejorar.'
    elif puntos > 0:
        texto = 'este usuario sabe leer y escribir ... pero no le pidas mucho más.'
    return mark_safe(texto)

@register.filter
def puntos(puntos=0):
    if puntos <= 0:
        return ''
    else:
        return mark_safe('<a class="puntos" href="/ayuda#karma">' + str(puntos) + ' puntos</a>')

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
        for aux in ['safari', 'opera', 'chrome', 'firefox', 'msie']:
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
    texto = ''
    estado = -1
    for p in preguntas:
        if p.estado != estado:
            if estado >= 0:
                texto += '</ul><br/>'
            
            # agrupamos por estado
            estado = p.estado
            
            # mostramos el estado
            if estado == 0:
                texto += '<div class="titulo"><span>Preguntas nuevas</span></div>\n'
            elif estado == 1:
                texto += '<div class="titulo"><span>Preguntas incompletas</span></div>\n'
            elif estado == 2:
                texto += '<div class="titulo"><span>Preguntas abiertas</span></div>\n'
            elif estado == 3:
                texto += '<div class="titulo"><span>Preguntas parcialmente solucionadas</span></div>\n'
            elif estado == 11:
                texto += u'<div class="titulo"><span>Preguntas pendientes de confirmación</span></div>\n'
            else:
                texto += '<div class="titulo"><span>Estado desconocido</span></div>\n'
            texto += '<ul class="tags">'
        
        # titulo de la pregunta
        texto += '<li class="pregunta">' + p.creado.strftime("%d/%m/%Y") + ', '
        texto += '<a href="/question/' + str(p.key()) + '" title="' + p.contenido + '\n\nAutor: ' + cortamail(p.autor) + ' | ' + str(p.respuestas) + ' respuestas">' + p.titulo + '</a></li>\n'
        
        # respuestas
        texto += '<ul>'
        for r in respuestas:
            if r.id_pregunta == str(p.key()):
                texto += '<li><a href="/question/' + str(p.key()) + '#' + str(r.key()) + '">' + r.fecha.strftime("%d/%m/%Y") + '</a> <b>' + cortamail(r.autor) + '</b> responde - ' + truncatewords(r.contenido, 20) + '</li>\n'
        texto += '</ul>'
    if estado >= 0:
        texto += '</ul>'
    return mark_safe(texto)


@register.filter
def ultimas_respuestas(pregunta, respuestas):
    if respuestas:
        retorno = '<ul>'
        for r in respuestas:
            if r.id_pregunta == str(pregunta):
                retorno += '<li>' + truncatewords(r.contenido, 20) + "</li>\n"
        return mark_safe(retorno+'</ul>')
    else:
        return ''


@register.filter
def respuestas_destacadas(respuestas):
    retorno = ''
    destacadas = []
    if len(respuestas) > 4:
        i = 1
        media = 0
        for r in respuestas:
            if r.valoracion > 0:
                media += r.valoracion
        media = math.ceil(float(media)/len(respuestas))
        for r in respuestas:
            if r.valoracion > media:
                destacadas.append([i, r.valoracion])
            i += 1
    if len(destacadas) > 0:
        while len(destacadas) > 0:
            elemento = destacadas[0]
            for r in destacadas:
                if r[1] > elemento[1]:
                    elemento = r
            destacadas.remove(elemento)
            if retorno == '':
                retorno = '<tr><td></td><td valign="top"><div class="respuesta_d">Respuestas destacadas: '
            retorno += '<a href="#' + str(elemento[0]) + '">@' + str(elemento[0]) + '</a> &nbsp; '
        if retorno != '':
            retorno += '</div></td><td></td></tr>'
    return mark_safe(retorno)


@register.filter
def tipo_enlace(enlace):
    retorno = ''
    if enlace.url[:23] == 'http://www.youtube.com/':
        enlace.tipo_enlace = 'youtube'
        retorno = '<iframe title="YouTube video player" class="youtube-player" type="text/html" width="425" height="349" src="http://www.youtube.com/embed/'+enlace.url.split('?v=')[1]+'" frameborder="0"></iframe>'
    elif enlace.url[:21] == 'http://www.vimeo.com/':
        enlace.tipo_enlace = 'vimeo'
        retorno = '<iframe src="http://player.vimeo.com/video/'+enlace.url.split('/')[3]+'" width="400" height="300" frameborder="0"></iframe>'
    elif enlace.url[-4:] in ['.ogv', '.OGV', '.mp4', '.MP4'] or enlace.url[-5:] in ['.webm', '.WEBM']:
        enlace.tipo_enlace = 'vhtml5'
        retorno = '<video src="'+enlace.url+'" controls="controls"></video>'
    elif enlace.url[-4:] in ['.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF'] or enlace.url[-5:] in ['.jpeg', '.JPEG']:
        enlace.tipo_enlace = 'imagen'
        retorno = '<a href="'+enlace.url+'" target="_Blank">'+miniatura(enlace.url)+'</a></center>'
    elif enlace.url[-4:] in ['.deb', '.DEB']:
        enlace.tipo_enlace = 'deb'
        retorno = '<a href="'+enlace.url+'"><img src="/img/application-x-deb.png" alt="'+enlace.descripcion+'"/></a>'
    elif enlace.url[-4:] in ['.deb', '.DEB', '.tgz', '.TGZ', '.bz2', '.BZ2'] or enlace.url[-3:] in ['.gz', '.GZ']:
        enlace.tipo_enlace = 'package'
        retorno = '<a href="'+enlace.url+'"><img src="/img/emblem-package.png" alt="'+enlace.descripcion+'" title="clic para descargar"/></a>'
    else:
        enlace.tipo_enlace = 'texto'
        retorno = '<a href="'+enlace.url+'" target="_Blank">'+enlace.url+'</a>'
    return mark_safe(retorno)


@register.filter
def show_stats(stats):
    if stats:
        try:
            pc_p_cache = int((float(stats['preguntas_cache'])/stats['preguntas'])*100)
        except:
            pc_p_cache = 0
        try:
            pc_e_cache = int((float(stats['enlaces_cache'])/stats['enlaces'])*100)
        except:
            pc_e_cache = 0
        texto = "<table class='stats'>\n<tr>\n"
        texto += "<td>\n<ul>\n<li>Preguntas: "+str(stats.get('preguntas',0))+"</li>\n<ul>\n<li>En cache: "+str(stats.get('preguntas_cache',0))+" ("+str(pc_p_cache)+"%)</li>\n<li>Respuestas: "+str(stats.get('respuestas',0))+"</li>\n<li>Respuestas por pregunta: "+str(stats.get('rpp',0))+"</li>\n</ul>\n</ul>\n</td>"
        texto += "<td>\n<ul>\n<li>Enlaces: "+str(stats.get('enlaces',0))+"</li>\n<ul>\n<li>En cache: "+str(stats.get('enlaces_cache',0))+" ("+str(pc_e_cache)+"%)</li>\n<li>Comentarios: "+str(stats.get('comentarios',0))+"</li>\n<li>Comentarios por enlace: "+str(stats.get('cpe',0))+"</li>\n</ul>\n</ul>\n</td>"
        texto += "<td>\n<ul>\n<li>Usuarios: "+str(stats.get('usuarios',0))+"</li>\n<ul>\n<li>Usuario m&aacute;s valorado: "+autor(stats.get('top_user', None))+"</li>\n<li>Seguimientos: "+str(stats.get('seguimientos',0))+"</li>\n</ul>\n</ul>\n</td>\n"
        texto += "<td>\n<ul>\n<li>Tags: "+str(stats.get('tags', 0))+"</li>\n<li>Votos: "+str(stats.get('votos', 0))+"</li>\n</ul>\n</td>"
        texto += "</tr>\n</table>\n"
        return mark_safe(texto)


@register.filter
def paginar(datos):
    texto = '<div class="paginacion"><span>' + str(datos[0]) + ' páginas</span>\n'
    # primera
    if datos[1] > 0:
        texto += '<a href="' + datos[2] + '0">&lt;&lt; primera</a>\n'
    # anteriores
    for pag in range(datos[1] - 5, datos[1]):
        if pag >= 0:
            texto += '<a href="' + datos[2] + str(pag) + '">' + str(pag) + '</a>\n'
    # actual
    texto += '<a id="actual" href="' + datos[2] + str(datos[1]) + '">' + str(datos[1]) + '</a>\n'
    # siguientes
    for pag in range(datos[1] + 1, datos[1] + 6):
        if pag < datos[0]:
            texto += '<a href="' + datos[2] + str(pag) + '">' + str(pag) + '</a>\n'
    # ultima
    if datos[1] < (datos[0] - 1):
        texto += '<a href="' + datos[2] + str(datos[0] - 1) + '">última &gt;&gt;</a>\n'
    texto += '</div>'
    if datos[0] > 1:
        return mark_safe(texto)
    else:
        return ''
