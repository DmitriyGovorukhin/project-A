var express = require('express');
var ws = require('ws');

var port = 8082;

var app = express();

app.use(express.static('static'));

app.listen(port, function () {
    console.log('Server started and listening ' + port);
});

/*var wsport = 8091;

var wss = new ws.Server({port: wsport});*/
