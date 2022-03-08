import os
import time
import json
import websocket
import psutil

last_total_bytes = None
last_time = None

def get_network_usage():
	global last_total_bytes
	global last_time
	bytes_sent = psutil.net_io_counters().bytes_sent
	bytes_received = psutil.net_io_counters().bytes_recv
	if last_total_bytes == None:
		last_total_bytes = bytes_received + bytes_sent
		last_time = time.time_ns()
		return 0.0
	else:
		total_bytes = bytes_received + bytes_sent
		current_time = time.time_ns()
		return (total_bytes - last_total_bytes)/((current_time - last_time)/1000000000)

def get_sys_info():
	cpu_usage = psutil.cpu_percent(interval=None)
	memory_usage = psutil.virtual_memory().percent
	disk_usage = psutil.disk_usage('/').percent
	cpu_temperature = psutil.sensors_temperatures(fahrenheit=False)["cpu_thermal"][0].current
	network_usage = get_network_usage()
	return {"cpu": cpu_usage, "memory": memory_usage, "disk": disk_usage, "network": network_usage, "temperature": cpu_temperature}

gf_api_token = os.getenv('GF_TOKEN')
gf_url = os.getenv('GF_URL')
gf_headers = {'Authorization': 'Bearer ' + gf_api_token}
gf_ws = websocket.WebSocket(skip_utf8_validation=True)
gf_ws.connect(gf_url, header=gf_headers)
gf_connected = True

print(get_sys_info())

while True:
	sys_info = get_sys_info()
	sys_info_json = json.dumps(sys_info)

	try:
		if gf_connected:
			gf_ws.send(sys_info_json)
		else:
			gf_ws.connect(gf_url, header=gf_headers)
			gf_ws.send(sys_info_json)
	except Exception as e:
		gf_ws.close(websocket.STATUS_ABNORMAL_CLOSED)
		gf_connected = False

gf_ws.close()
