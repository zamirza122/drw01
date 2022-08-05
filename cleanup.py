import json
import requests
import urllib3

CML = {
    "host": "10.10.20.161",
    "username": "developer",
    "password": "C1sco12345"
}

NODE_TO_RESET = [ 'csr1000v', 'nxosv9000' ]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CML_URL = "https://" + CML["host"] + "/api"
CML_USER = CML["username"]
CML_PASS = CML["password"]

labname = "CML Lab " + CML["host"]

def get_token(url, user, password):
	api_call = "/v0/authenticate"
	url += api_call

	headers = {
		'Content-Type': 'application/json',
		'accept': 'application/json'
	}

	payload = {
		"username": user,
		"password": password
	}

	response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False).json()
	return response


def get_labs(token, url):
	api_call = "/v0/labs"
	url += api_call
	token = 'Bearer' + ' ' + token

	headers = {
		'accept': 'application/json',
		'Authorization': token
	}

	response = requests.get(url, headers=headers, verify=False).json()
	print("#" + " " + "Simulated labs on CML" + ": " + str(len(response)) + " at " + labname)
	return response

def get_nodes(token, url):
	api_call = "/nodes"
	url += api_call
	token = 'Bearer' + ' ' + token

	headers = {
		'accept': 'application/json',
		'Authorization': token
	}

	response = requests.get(url, headers=headers, verify=False).json()
	return response

def get_node_details(token, url, nodeid):
	api_call = "/nodes/" + nodeid
	url += api_call
	token = 'Bearer' + ' ' + token

	headers = {
		'accept': 'application/json',
		'Authorization': token
	}

	response = requests.get(url, headers=headers, verify=False).json()
	return response

def restart_labs(token, url, labids):
	token = 'Bearer' + ' ' + token
	headers = {
		'accept': 'application/json',
		'Authorization': token
	}
	
	for labid in labids:
		api_call = "/v0/labs/" + labid
		laburl = url + api_call
		guiurl = url.rstrip('api')
		guiurl = guiurl + "lab/" + labid

		response  = requests.get(laburl, headers=headers, verify=False).json()
		lab_state = str(response['state'])
		print("{0:42}{1:22}{2:18}{3:18}".
			format(str(response['lab_title']), str(response['created']), str(response['state']), str(guiurl)))
		# Only restart active labs
		if( lab_state == 'STARTED'):
			print('Restarting nodes in lab with labid =',labid)
			nodeids = get_nodes(auth_token, laburl)
			for nodeid in nodeids:
				node = get_node_details(auth_token, laburl, nodeid)
				data = node['data']
				if( data['node_definition'] in NODE_TO_RESET):
					print(f'Resetting node {nodeid} label {data["label"]}')
					url2 = laburl + '/nodes/' + nodeid + '/state/stop'
					response = requests.put(url2, headers=headers, verify=False).json()
					url3 = laburl + '/nodes/' + nodeid + '/state/start'
					response = requests.put(url3, headers=headers, verify=False).json()


if __name__ == "__main__":
	auth_token = get_token(CML_URL, CML_USER, CML_PASS)
	print("#"*113)
	labids = get_labs(auth_token, CML_URL)
	print("#"*113)
	restart_labs(auth_token, CML_URL, labids)
	print("#"*113)