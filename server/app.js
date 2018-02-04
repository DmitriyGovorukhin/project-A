var express = require('express');
var ws = require('ws');

var port = 8082;

var app = express();

app.use(express.static('static'));

app.listen(port, function () {
    console.log('Server started and listening ' + port);
});

var wsport = 8091;

var wsServer1 = new ws.Server({port: wsport, perMessageDeflate: false});

var robotWs;
var browserWs;

wsServer1.on('connection', function (socket, upgradeReq) {
    console.log(
        'New WebSocket Connection: ',
        (upgradeReq || socket.upgradeReq).socket.remoteAddress,
        (upgradeReq || socket.upgradeReq).headers['user-agent'], wsport);

    socket.on('close', function (code, message) {
        console.log('disconnected');
    });

    socket.onmessage = function (event) {
        console.log('> ' + event.data);

        if (robotWs !== null && robotWs !== undefined) {
            robotWs.send(event.data)
        }

        var val = JSON.parse(event.data);

        if (val["client"] === "robot")
            robotWs = socket;

        if (val["client"] === "browser")
            browserWs = socket;
    };
});

console.log('Awaiting WebSocket connections on ws://127.0.0.1:' + wsport + '/');

