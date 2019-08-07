# from http.server import HTTPServer, BaseHTTPRequestHandler
import SimpleHTTPServer
import SocketServer
import json
from utils import *

# modular design opted. Hence, direct files imports opted out.
# open json file and give it to data variable as a dictionary.

# with open("targets.json") as data_file:
#     data = json.load(data_file)


# Defining a HTTP request Handler class
class ServiceHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # sets basic headers for the server
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type','text/json')
        # reads the length of the Headers
        length = int(self.headers['Content-Length'])
        # reads the contents of the request
        content = self.rfile.read(length)
        data_strm = str(content).strip('b\'')
        self.end_headers()
        return data_strm
        

    # VIEW Method Definition
    # Sample Curl Query: curl -X VIEW --data "tild23.pld.ai" server-url:port-no
    # Uses VIEW Method to show the Value for a given Key from the cb-exporter's targets.json file.
    def do_VIEW(self):
        # defining all the headers.
        display = {}
        data_strm = self._set_headers()
        display[data_strm] = get_util(data_strm)
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        # prints values from given key as input.
        self.wfile.write(json.dumps(display).encode())
    

    # GET Method Definition
    # Sample Curl Query: curl -X GET server-url:port-no
    # Uses GET Method to show all the keys and their respective values from the cb-exporter's targets.json file.
    def do_GET(self):
        # defining all the headers.
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        # prints all the keys and values of the json file.
        self.wfile.write(json.dumps(get_view()).encode())


    # POST Method Definition
    # Sample Curl Query: curl -X POST --data "Hostname,UserName,Password" server-url:port-no
    # Uses POST Method to get empty port-no to start cb-exporter process & update targets.json for both our HTTP server and Prometheus.
    def do_POST(self):
        data_strm = self._set_headers()
        data_strm_list = data_strm.split(',')
        # get free port number
        port_no = get_empty_port()
        # store key, values in reference targets.json file
        write_util(data_strm_list[0], data_strm_list[1], data_strm_list[2], port_no)
        # change Prometheus server's target file.
        write_targets(port_no,data_strm_list[0], data_strm_list[1], data_strm_list[2])
        # get messages & command that is executed to be posted as server response.
        eff_command, mssg_dgst = cbexport_start(data_strm_list[0])
        eff_mssg = "Command Executed: "+str(eff_command)+" Command Execution Message: "+str(mssg_dgst)
        # Curl command gets hanged after Popen process execution. Hence, every change is made before it.
        # change Prometheus server's target file.
        # write_targets(port_no," "," ")
        self.send_response(200)
        self.wfile.write(bytes(eff_mssg,'utf-8'))


    # DELETE Method Definition
    # Sample Curl Query: curl -X DELETE --data "Hostname" server-url:port-no
    # Uses DELETE Method to kill a cb-exporter process baed on port-no & update targets.json for both our HTTP server and Prometheus.
    def do_DELETE(self):
        # receive hostname value as key
        data_strm = self._set_headers()
        # delete value from cb-exporter's reference file.
        str_val, port_no = del_util(data_strm)
        eff_mssg = str_val+" Port Number in use: "+port_no
        # delete from targets.json file of Prometheus server
        del_targets(port_no)
        # kill the process with id in use
        cbexport_del(port_no)
        # delete from targets.json file of Prometheus server
        # del_targets(port_no)
        self.send_response(200)
        self.wfile.write(bytes(eff_mssg,'utf-8'))


# Python 3: HTTPServer testing worked fine on local machine.
# server = HTTPServer(('127.0.0.1',20997), ServiceHandler)

# Python 2: TCPServer for python for testing. A possbile reason for curl command hanging when tested on VM.
# server = SocketServer.TCPServer(('127.0.0.1',20997), ServiceHandler)

# Server Initialization
# Hard-coded URL: Change it as per need.
server = SocketServer.TCPServer(('10.17.81.23',43918), ServiceHandler)
server.serve_forever()
