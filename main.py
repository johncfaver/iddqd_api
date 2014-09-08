#!/usr/bin/env python

import tornado.ioloop, tornado.log
import os, logging
from handlers import *

if __name__ == '__main__':

    handlers = [
        (r'/', index),
        (r'/molfile',getMol),
        (r'/molfile3d',getMol),
        (r'/molfile2d',get2DMol),
        (r'/molinfo',getInfo),
        (r'/fail',fail),
        (r'/(.*)',fail)
    ]
    
    options = dict()
    options['debug']            = False
    options['login_url']        = '/fail'
    options['iddqd_home']       = '/var/www/iddqd'

    tornado.log.access_log.setLevel(logging.INFO)
    tornado.log.app_log.setLevel(logging.INFO)
    tornado.log.gen_log.setLevel(logging.INFO)

    my_access_log = logging.handlers.RotatingFileHandler("iddqd_access.log",maxBytes=5000000,backupCount=3)
    my_app_log    = logging.handlers.RotatingFileHandler("iddqd_app.log",maxBytes=5000000,backupCount=3)
    my_gen_log    = logging.handlers.RotatingFileHandler("iddqd_general.log",maxBytes=5000000,backupCount=3)

    for handler in [my_access_log, my_app_log, my_gen_log]:
        handler.setFormatter(tornado.log.LogFormatter())

    tornado.log.access_log.addHandler(my_access_log)
    tornado.log.app_log.addHandler(my_app_log)
    tornado.log.gen_log.addHandler(my_gen_log)

    app = myApp(handlers,**options)

    ssl_options = { "certfile" : os.path.join(options['iddqd_home'],'config/iddqd-prod.crt'),
                    "keyfile"  : os.path.join(options['iddqd_home'],'config/iddqd-prod.key') }

    app.listen(8888,ssl_options=ssl_options)
    tornado.ioloop.IOLoop.instance().start()


