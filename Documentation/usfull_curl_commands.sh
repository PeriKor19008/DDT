curl -X POST -d 'http://172.18.0.2:5000/' http://192.168.1.108:5000/bootstrap

curl -X POST -d 'http://172.18.0.2:5000/' http://172.18.0.3:5000/bootstrap

curl -X POST -d 'http://192.168.1.108:5000/' http://172.18.0.3:5000/bootstrap

curl -X POST -d 'http://192.168.1.108:5000/' http://192.168.1.108:5000/init_data