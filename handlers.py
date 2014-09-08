#!/usr/bin/env python

import tornado.web
import psycopg2, json, os

class myApp(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        """Initialize application-wide database connection
        """
        configfile = os.path.join(kwargs['iddqd_home'],'config/iddqd-config.json') 
        with open(configfile) as cfile:
            conf = json.load(cfile)
        dbhost = conf['postgresql']['host'].encode('utf-8')
        dbport = conf['postgresql']['port']
        dbname = conf['postgresql']['database'].encode('utf-8')
        dbuser = conf['postgresql']['user'].encode('utf-8')
        dbpass = conf['postgresql']['pass'].encode('utf-8')
        self.db = psycopg2.connect("host={0} port={1} dbname={2} user={3}  \
                    password={4}".format(dbhost,dbport,dbname,dbuser,dbpass))
        tornado.web.Application.__init__(self, *args, **kwargs)

class myHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        """To be authenticated, client must send 
           user/pass with every POST request.
        """
        try:
            #Require local ip address?
            ip = self.request.remote_ip
            assert(ip[:11] in ['192.168.20.','192.168.25.'] or ip == '127.0.0.1')

            client_username = self.get_argument("username",None)
            client_password = self.get_argument("password",None)
            assert(client_username is not None and client_password is not None)
            q = self.application.db.cursor()
            q.execute('SELECT username FROM users WHERE username = %s AND \
                        password = crypt(%s,password) ',
                        [client_username,client_password])
            row = q.fetchone()
            if row:
                return str(row[0])
            else:
                self.write('Error: Authentication failed.')
                return None
        except Exception:
            self.write('Error: Authentication failed.')
            return None

########
class index(myHandler):
    def get(self):
        self.write('Options: \n')
        self.write('\t/molfile?molid=_\n')
        self.write('\t/molfile?molname=_\n')
        self.write('\t/molfile2d?molid=_\n')
        self.write('\t/molfile2d?molname=_\n')
        self.write('\t/info?molname=_\n')
        self.write('\t/info?molid=_\n')

class getMol(myHandler):
    def post(self):
        if self.get_current_user() is None:
            self.finish()
            return
        molid = self.get_argument("molid",None)
        molname = self.get_argument("molname",None)
        if molname and not molid:
            q = self.application.db.cursor()
            q.execute('SELECT molid FROM molecules WHERE molname ILIKE %s',[molname])
            row = q.fetchone()
            if row:
                molid = str(row[0])
            else:
                self.write('Error: Molecule not found!')
                return
        if molid:
            try:
                fname = os.path.join(self.application.settings['iddqd_home'],'public/uploads/structures/'+str(molid)+'-3d.mol')
                with open(fname) as molfile:
                    for line in molfile.readlines():
                        self.write(line)
            except:
                self.write('Error: Problem reading mol file.')
                return
        else:
            self.write('Error: No molecule requested.')

class get2DMol(myHandler):
    def post(self):
        if self.get_current_user() is None:
            self.finish()
            return
        molid = self.get_argument("molid",None)
        molname = self.get_argument("molname",None)
        if molname and not molid:
            q = self.application.db.cursor()
            q.execute('SELECT molid FROM molecules WHERE molname ILIKE %s',[molname])
            row = q.fetchone()
            if row:
                molid = str(row[0])
            else:
                self.write('Error: Molecule not found!')
                return
        if molid:
            try:
                fname = os.path.join(self.application.settings['iddqd_home'],'public/uploads/structures/'+str(molid)+'.mol')
                with open(fname) as molfile:
                    for line in molfile.readlines():
                        self.write(line)
            except:
                self.write('Error: Problem reading mol file.')
                return
        else:
            self.write('Error: No molecule requested.')

class getInfo(myHandler):
    def post(self):
        if self.get_current_user() is None:
            self.finish()
            return
        molid = self.get_argument("molid",None)
        molname = self.get_argument("molname",None)
        q = self.application.db.cursor()
        if molname and not molid:
            q.execute('SELECT molid,molweight,dateadded,username,molformula         \
                         FROM molecules m LEFT JOIN users u on u.userid=m.authorid  \
                         WHERE molname ILIKE %s',[molname])
            row = q.fetchone()
            if row:
                molid,molweight,dateadded,author,molformula = row 
            else:
                self.write('Error: Molecule not found!')
                return
        if molid and not molname:
            q.execute('SELECT molname,molweight,dateadded,username,molformula \
                        FROM molecules m LEFT JOIN users u on u.userid=m.authorid \
                        WHERE molid=%s',[molid])
            row = q.fetchone()
            if row:
                molname,molweight,dateadded,author,molformula = row 
            else:
                self.write('Error: Molecule not found!')
                return
        if molid:
            q.execute('SELECT t.nickname,string_agg(d.value::text,\',\'),dt.type,dt.units \
                        FROM moldata d LEFT JOIN targets t ON t.targetid=d.targetid     \
                        LEFT JOIN datatypes dt ON dt.datatypeid=d.datatype              \
                        WHERE d.molid=%s AND dt.class in (1,2)                          \
                        GROUP BY t.nickname,dt.type,dt.units                            \
                        ORDER BY dt.type',[molid])
            response = dict()
            response['molname']     = molname
            response['molid']       = molid
            response['molweight']   = molweight
            response['dateadded']   = str(dateadded)
            response['author']      = author
            response['molformula']  = molformula
            response['data']        = []
            for row in q.fetchall():
                rowdict = dict()
                rowdict['type'] = row[2]
                rowdict['units'] = row[3]
                rowdict['target'] = row[0]
                rowdict['values'] = [ float(value) for value in row[1].split(',')]
                response['data'].append(rowdict)
            self.write(response)

class fail(myHandler):
    def get(self,req=None):
        self.write('Error: Fail \n')


