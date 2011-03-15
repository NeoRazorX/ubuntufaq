#!/usr/bin/env python

import logging, random
from google.appengine.ext import db
from google.appengine.api import memcache
from base import *

class tags:
    def __init__(self):
        # diccionario que almacena todos los tags
        self.pendientes = {}
        
        # elegimos aleatoriamente una tabla
        tabla = random.randint(0, 1) == 0
        
        if tabla == 0:
            seleccion = db.GqlQuery("SELECT * FROM Pregunta ORDER BY fecha DESC").fetch(25)
            logging.info('Actualizando tags de preguntas')
        else:
            seleccion = db.GqlQuery("SELECT * FROM Enlace ORDER BY fecha DESC").fetch(25)
            logging.info('Actualizando tags de enlaces')
        
        for ele in seleccion:
            if tabla == 0:
                tags = self.tag2list( ele.tags )
                link = '/question/' + str(ele.key())
                title = ele.titulo
            else:
                tags = self.tag2list( self.extraer_tags( ele.descripcion ) )
                link = '/story/' + str(ele.key())
                title = ele.descripcion[:249]
            self.procesar( tags, link, title )
        
        # actualizamos los datos de memcache
        self.actualizar()
    
    # devuelve un string con los tags (encontrados en texto) separados por comas
    def extraer_tags(self, texto):
        retorno = ''
        for tag in KEYWORD_LIST:
            if texto.lower().find(tag) != -1:
                if retorno == '':
                    retorno = tag
                else:
                    retorno += ', ' + tag
        if retorno == '':
            retorno = 'ubuntu, general'
        return retorno
    
    # a partir de un string de tags, devuelve una lista de cada uno de ellos
    def tag2list(self, tags):
        return tags.split(', ')
    
    # rellena pendientes con cada elemento, en funcion del tag
    def procesar(self, tags, link, title):
        elemento = {'link': link, 'title': title}
        for t in tags:
            if t in self.pendientes:
                self.pendientes[t].append( elemento )
            else:
                self.pendientes[t] = [elemento]
    
    # actualiza los elementos de memcache con los nuevos resultados obtenidos
    def actualizar(self):
        for tag in self.pendientes.keys():
            elementos = self.pendientes[tag]
            if memcache.get( 'tag_' + tag) is None:
                if memcache.add( 'tag_' + tag, elementos ):
                    logging.info('Almacenados los resultados del tag ' + tag + ' en memcache')
                else:
                    logging.error('Fallo al almacenar los resultados del tag ' + tag + ' en memcache')
            else:
                if memcache.replace( 'tag_' + tag, elementos ):
                    logging.info('Reemplazados los resultados del tag ' + tag + ' en memcache')
                else:
                    logging.error('Fallo al reemplazar los resultados del tag ' + tag + ' en memcache')

if __name__ == "__main__":
    tags()

