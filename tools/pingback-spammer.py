#!/usr/bin/env python

import sys, urllib2, re
from xmlrpclib import ServerProxy, Fault
from xml.dom import minidom

class pingback:
    def get_pingurl(self, trackback_url):
        PINGBACK_RE = re.compile('<link rel="pingback" href="([^" ]+)"="" ?="">')
        pingurl = None
        
        if trackback_url:
            try:
                remote = urllib2.urlopen(trackback_url)
            except:
                pass
            
            try:
                # first look for a X-Pingback header
                pingurl = remote.info().getheader('X-Pingback')
            except:
                pingurl = None
            
            if pingurl == None:
                try:
                    # then try to find a <link> element
                    pingurl = PINGBACK_RE.findall( remote.read() )
                    pingurl = pingurl[0]
                except:
                    pingurl = None
        
        return pingurl
    
    def do_ping(self, origen, destino):
        pingurl = self.get_pingurl(destino)
        
        errores = {
            0: 'codigo generico de fallo.',
            16: 'El URI de origen no existe.',
            17: 'El URI de origen no contiene un enlace al URI de destino, y por lo tanto no puede ser usado como origen.',
            32: 'El URI especificado como de destino no existe.',
            33: 'El URI de destino especificado no puede ser usado como destino. O bien no existe, o no es un recurso habilitado-pingback.',
            48: 'El pingback ya ha sido registrado anteriormente.',
            49: 'Acceso denegado.',
            50: 'El servidor no puede comunicarse con un servidor upstream, o ha recibido un error de un servidor upstream, y por lo tanto no puede completar la solicitud. Esto es similar al error de HTTP: 402 Bad Gateway. Este error DEBERIA ser usado por servidores proxy de pingback al propagar los errores.'
            }
        
        if pingurl:
            try:
                proxy = ServerProxy(pingurl)
                proxy.pingback.ping(origen, destino)
                print "pingback realizado a " + pingurl
            except Fault, e:
                print "error: " + errores.get(e.faultCode, 'desconocido')
            except:
                print "error desconocido!"
        else:
            print "imposible obtener pingurl de: " + destino
    
    def __init__(self):
        continuar = True
        
        try:
            pingbacks = minidom.parse( urllib2.urlopen('http://www.ubufaq.com/pingbacks') )
        except:
            continuar = False
        
        if continuar:
            for nodo in pingbacks.getElementsByTagName('item'):
                origen = nodo.getElementsByTagName('link')[0].childNodes[0].data
                destino = nodo.getElementsByTagName('source')[0].childNodes[0].data
                fecha = nodo.getElementsByTagName('pubDate')[0].childNodes[0].data
                
                if len( sys.argv ) < 2:
                    self.do_ping(origen, destino)
                elif sys.argv[1] != '' and fecha == sys.argv[1]:
                    self.do_ping(origen, destino)
        else:
            print 'Error al leer los pingbacks'

if __name__ == "__main__":
   pingback()
