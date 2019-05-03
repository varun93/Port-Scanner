from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner
from db import get_results, create_master_task
import json
import ipaddress

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
	return render_template('index.html')

@flask_app.route('/get_results')
def scan_results():
	results = get_results()	
	return json.dumps(results)

@flask_app.route('/ping_scan', methods=['POST'])
def ping_scan():
	pass 


# TODO : do input validation
@flask_app.route('/submit_task', methods=['POST'])
def submit_task():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix'] 
	start_port = int(request.form['start_port']) 
	end_port = int(request.form['end_port']) 
	scan_mode = request.form['scan_mode'] 
	
	if not network_prefix or not network_prefix.strip():
		network_prefix = "32"

	# wrap in a try catch
	master_task_id = create_master_task(dest_ip, network_prefix, start_port, end_port)

	full_address = "{}/{}".format(dest_ip,network_prefix)
	address_list = ipaddress.ip_network(full_address)

	tasks = []
	for address in address_list:
		for port in range(start_port, end_port + 1):
			tasks.append((str(address),port,master_task_id))

	port_scanner = None
	
	# decide on a correct number currently set to 5
	if scan_mode == "normal_scan":
		port_scanner = grab_banner 
	elif scan_mode == "syn_scan":
		port_scanner = syn_scan
	elif scan_mode == "fyn_scan":
		port_scanner = fyn_scan 


	port_scanner.chunks(tasks, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})