curl -X POST -d 'http://172.18.0.2:5000/' http://192.168.1.108:5000/bootstrap

curl -X POST -d 'http://172.18.0.2:5000/' http://172.18.0.3:5000/bootstrap

curl -X POST -d 'http://192.168.1.108:5000/' http://172.18.0.3:5000/bootstrap

curl -X POST -d 'http://192.168.1.108:5000/' http://192.168.1.108:5000/init_data


curl -X POST -H "Content-Type: application/json" -d '{"Name": "Atta ur Rehman Khan", "Education": ["University of Malaya", "COMSATS University"], "Awards": 0}' http://192.19.0.3:5000/insert_data