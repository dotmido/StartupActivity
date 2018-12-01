from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from startup_setup import Startup, Base, Founder

engine = create_engine('sqlite:///startup.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith('founders'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            Founders = session.query(Founder).all()
            output = "<html><body>"
            for founder in Founders:
                output += "<h3>%s<h3>" % founder.name
            output += "</body></html>"
            self.wfile.write(output.encode())
        elif self.path.endswith('startups'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            Startups = session.query(Startup).all()
            output = "<html><body>"
            for startup in Startups:
                output += "<h3><a href='startup/{0}'>{1}</h3>".format(
                    startup.id, startup.name)
                output += "<a href='startups/%s/edit'>Edit</a>" % startup.id
                output += " <a href='startups/%s/delete'>Delete</a>" % startup.id
            output += "</body></html>"
            self.wfile.write(output.encode())
        elif 'startup/' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = "<html><body>"
            idfromPath = self.path.split("/")[2]
            startup = session.query(Startup).filter_by(id=idfromPath).one()
            if startup != []:
                output += "<h1> Name: %s </h1>" % startup.name
                output += "<br/><h2>ID: %s </h2>" % startup.id
            output += "</body></html>"
            self.wfile.write(output.encode())
        elif self.path.endswith('/startups/new'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = """<html><body>
                     <h1>Add new Startup</h1><br/>
                     <form action='/startups/new' method='POST'
                     enctype='multipart/form-data'>
                     <input type='text' name='StartupName'
                     placeholder='Startup name' />
                     <input type='submit' value='Add'/>
                     </form></body></html>"""
            self.wfile.write(output.encode())
        elif self.path.endswith('/edit'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            startupId = self.path.split('/')[2]
            output = """<html><body>
                        <h1>Edit startup with ID: {0}</h1>
                        <form method='POST' action='/startups/{1}/edit'
                        enctype='multipart/form-data'>
                        <input type='text' placeholder='new name here..'
                        name='NewName' />
                        <input type='submit' value='Rename'/></form>
                        </body></html>""".format(startupId, startupId)
            self.wfile.write(output.encode())
        elif self.path.endswith('/delete'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            startupId = self.path.split('/')[2]
            StartupName = session.query(
                Startup).filter_by(id=startupId).one().name
            output = """<html><body>
                       <h1>Are you sure you want to delete {0}</h1>
                       <form method='POST' action='/startups/{1}/delete'
                       enctype='multipart/form-data'>
                       <input type='submit' value='Delete' /></form>
                       </body></html>""".format(StartupName, startupId)
            self.wfile.write(output.encode())
        elif self.path.endswith('/startup/founders'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = "<html><body>"
            output += "<h1>List of founders</h1>"
            founders = session.query(Founder).all()
            for founder in founders:
                output += "<h3> %s <h3>" % founder.name
            output += "</body></html>"
            self.wfiel.write(output.encode())

    def do_POST(self):
        if self.path.endswith('/startups/new'):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('StartupName')
                newStartup = Startup(name=messagecontent[0])
                session.add(newStartup)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/startups')
                self.end_headers()
        elif self.path.endswith('/edit'):
            idfromPath = self.path.split('/')[2]
            startup = session.query(Startup).filter_by(id=idfromPath).one()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('NewName')
                startup.name = messagecontent[0]
                session.add(startup)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/startups')
                self.end_headers()
        elif self.path.endswith('/delete'):
            idfromPath = self.path.split('/')[2]
            startup = session.query(Startup).filter_by(id=idfromPath).one()
            if startup:
                session.delete(startup)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/startups')
                self.end_headers()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print('Web server running in port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server... ")
        server.socket.close()


if __name__ == '__main__':
    main()
