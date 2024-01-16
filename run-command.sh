curl -X POST http://172.19.0.2:5000/initialize
curl -X POST http://172.19.0.2:5000/first
sleep "1"
# curl -X POST http://172.19.0.3:5000/initialize
# curl -X POST http://172.19.0.4:5000/initialize
# curl -X POST http://172.19.0.5:5000/initialize
# curl -X POST http://172.19.0.6:5000/initialize
# curl -X POST http://172.19.0.7:5000/initialize
curl -X POST http://172.17.159.9:5000/initialize
sleep "1"
# curl -X POST -d 'http://172.17.159.9:5000' http://172.19.0.2:5000/join
curl -X POST -d 'http://172.19.0.2:5000' http://172.17.159.9:5000/join