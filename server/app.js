var fs = require('express'),
    http = require('http'),
    ws = require('ws');

var port1 = 8090;

var wsServer1 = new ws.Server({port: port1, perMessageDeflate: false});

var robotWs;
var browserWs;

wsServer1.on('connection', function (socket, upgradeReq) {
    console.log(
        'New WebSocket Connection: ',
        (upgradeReq || socket.upgradeReq).socket.remoteAddress,
        (upgradeReq || socket.upgradeReq).headers['user-agent'], port1);

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

console.log('Awaiting WebSocket connections on ws://127.0.0.1:' + port1 + '/');

var port2 = 8091;

var wsServer2 = new ws.Server({port: port2, perMessageDeflate: false});

wsServer2.on('connection', function (socket, upgradeReq) {
    console.log(
        'New WebSocket Connection: ',
        (upgradeReq || socket.upgradeReq).socket.remoteAddress,
        (upgradeReq || socket.upgradeReq).headers['user-agent'], port2
    );

    socket.on('close', function (code, message) {
        console.log('Disconnected WebSocket');
    });
});

wsServer2.broadcast = function (data) {
    wsServer2.clients.forEach(function each(client) {
        if (client.readyState === ws.OPEN) {
            client.send(data);
        }
    });
};

console.log('Awaiting WebSocket connections on ws://127.0.0.1:' + port2 + '/');

var portStream1 = 8092;

http.createServer(function (request, response) {
    response.connection.setTimeout(0);

    console.log(
        'Stream Connected: ' +
        request.socket.remoteAddress + ':' +
        request.socket.remotePort
    );

    request.on('data', function (data) {
        wsServer2.broadcast(data);

        if (request.socket.recording) {
            request.socket.recording.write(data);
        }
    });

    request.on('end', function () {
        console.log('close');
        if (request.socket.recording) {
            request.socket.recording.close();
        }
    });
}).listen(portStream1);

console.log('Listening for Webcam incomming MPEG-TS Stream on http://127.0.0.1:' + portStream1);

var httpPort = 8080;

http.createServer(function (request, response) {
    var filePath = '.' + request.url;
    if (filePath === './')
        filePath = './index.html';

    var contentType = 'text';

    if (filePath.endsWith('css'))
        contentType += '/css';
    else if (filePath.endsWith('js'))
        contentType += '/javascript';
    else
        contentType += '/html';

    fs.readFile(filePath, function (error, content) {
        if (error) {
            if (error.code === 'ENOENT') {
                fs.readFile('./404.html', function (error, content) {
                    response.writeHead(200, {'Content-Type': contentType});
                    response.end(content, 'utf-8');
                });
            }
            else {
                response.writeHead(500);
                response.end('Sorry, check with the site admin for error: ' + error.code + ' ..\n');
                response.end();
            }
        }
        else {
            response.writeHead(200, {'Content-Type': contentType});
            response.end(content, 'utf-8');
        }
    });

}).listen(httpPort);

console.log('Server running at http://127.0.0.1:' + httpPort + '/');