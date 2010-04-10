# -*- coding: utf-8 -*-
# Copyright (C) 2009  Kamil Selwa <selwak@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#inspired on http://www.thegibson.org/blog/archives/689

import cgi
from urlparse import urlparse, urljoin, parse_qsl
from urllib import unquote
import subprocess
import tempfile, time
import os
import urllib, simplejson
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#as - autosave
EDITOR = ["/usr/bin/vim", "-o", "-c", "as", "2"]
PORT = 9292

def createTemplate(string):
    f = tempfile.NamedTemporaryFile(delete=False, suffix='.css', mode='w+')
    f.write(string)
    f.close()
    return f.name
    
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_error(404, "Not Found: %s" % self.path)

    def do_POST(self):
        try:
            clength = 0
            cl = self.headers.getheader('content-length')

            if cl != None:
                clength = int(cl)
            else:
                self.send_response(411)
                self.end_headers()
                return

            body = self.rfile.read(clength)
            #css = dict([[e[0],unquote(e[1])] for e in [d.split("=") for d in body.split("&")]])
            css = dict( parse_qsl(body) )
            ## write css into files
            stylesheets = []
            stylesheets_tmp = []
            css_hrefs = css['href'].split(",")
            i = 0
            href = css['origin']
            origin = urlparse(css['origin'])

            for sylesheet in css['rules'].split("||"):
                
                if css_hrefs[i] is "": #we got inline style
                    css_name = createTemplate(sylesheet)
                else: # we got external css
                    if origin.scheme is "file": # local style
                        css_name = urljoin(href, css_hrefs[i])    
                    else: # remote style
                        remote_css = urllib.urlopen(css_hrefs[i])
                        css_name = createTemplate(remote_css.read())
                        
                stylesheets_tmp.append(css_name)
                stylesheets.append( {'href':css_hrefs[i], 'new_href':css_name, } )
                ++i 
            
            print "Spawning editor... "
            p = subprocess.Popen(EDITOR + stylesheets_tmp, close_fds=True)

            # hold connection open until editor finishes
            p.wait()
            print "%s stylesheets sent" % i
            self.send_response(200)
            self.send_header( 'Content-type', 'text/javascript')
            self.end_headers()

            self.wfile.write( simplejson.dumps(stylesheets) )
        except :
            self.send_error(404, "Not Found: %s" % self.path)
    
def main():
    import platform
    t = platform.python_version_tuple()
    if int(t[0]) == 2 and int(t[1]) < 6:
        print "Python 2.6+ required"
        # uses tempfile.NamedTemporaryFile delete param
        return
    try:
        httpserv = HTTPServer(('localhost', PORT), Handler)
        print "listening for css on %s" % PORT
        httpserv.table = {}
        httpserv.serve_forever()
    except KeyboardInterrupt:
        httpserv.socket.close()

if __name__ == '__main__':
    main()

