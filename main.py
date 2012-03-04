#!/usr/bin/env python2.5
#-*- coding: utf-8 -*-
import web, math
web.config.debug = False
urls = ('/', 'index',
        '/-', 'api',
        '/(\w+)\+', 'stats',
        '/(\w+)', 'redirect',)
app = web.application(urls, globals(), autoreload=True)
db = web.database(dbn='sqlite', db='likamag.db')
render = web.template.render('tpl/')

site = "http://example.com/"

class magic:
    codeset = 'omyg5dNIF81Uiws4hzeKPBJX9lack72bj0xvqyrOMYGDRW6SHZnfu3ELACVQY'
    base = len(codeset)
    def to(self, id):
        encoded = ''
        while id > 0:
            position = int(id % self.base)
            encoded = ''.join([self.codeset[position:position+1], encoded])
            id = math.floor(id/self.base)
        return encoded        
    def frm(self, encoded):
        id = 0
        for index, char in enumerate(encoded[::-1]):
            id += self.codeset.find(char) * math.pow(self.base,index)
        return int(id)
        
class index:        
    def GET(self):
        return render.foo()

class api:
    def check(self,url):
        q,r = db.select('links', limit=1, where="url=$u", vars={'u': url}),[]
        for s in q:
            r.append(s)
        return r        
    def GET(self):
        if not web.input().url:
            return web.seeother('/')  
        if not web.input().url.startswith('magnet:?'):
            return 'magnets only'
        dct = {}
        for item in web.input().url[8:].split('&'):
            key,value = item.split('=')
            if dct.get(key):
                dct[key] += str(value)
            else:
                dct[key] = str(value)
        xt = dct['xt']
        if xt and not self.check(xt):
            i = db.insert('links', url = xt, clx = 0)
            return site+magic().to(int(i))
        elif xt and self.check(xt):
            return site+magic().to(int(self.check(xt)[0].id))
        else:
            return 'error'
            
class redirect:
    def GET(self, code):
        q,r = db.select('links', limit=1, where="id=$i", vars={'i': magic().frm(code)}),[]
        for s in q:
            r.append(s)
        if not r:
            return web.seeother('/')
        else:
            db.update('links', where="id=$i", vars={'i': magic().frm(code)}, clx=r[0].clx+1)
            return web.redirect('magnet:?xt='+r[0].url)
            
class stats:
    def GET(self, code):
        q,r = db.select('links', limit=1, where="id=$i", vars={'i': magic().frm(code)}),[]
        for s in q:
            r.append(s)
        if not r:
            return web.seeother('/')
        else:
            return """%s%s 
            
%s

%s""" % (site, code, r[0].url, r[0].clx)
            
if __name__ == "__main__":
    app.run()