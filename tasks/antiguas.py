#!/usr/bin/env python

import logging
from google.appengine.ext import db
from datetime import datetime, timedelta
from base import *

class antiguas:
    def __init__(self):
        preguntas = db.GqlQuery("SELECT * FROM Pregunta WHERE fecha < :1 ORDER BY fecha ASC LIMIT 50",
                                datetime.today() - timedelta(days= 90))
        for p in preguntas:
            if p.estado not in[14, 13, 12, 10, 3]:
                p.estado = 14
                try:
                    p.put()
                    logging.info('Marcada como antigua la pregunta: ' + str(p.key()))
                except:
                    logging.error('Imposible marcar como antigua la pregunta: ' + str(p.key()))

if __name__ == "__main__":
    antiguas()

