var express = require('express');
var ws = require('websocket ');

var port = 8080;

var app = express();

app.use(express.static('static'));

app.listen(port, function () {
    console.log('Server started and listening ' + port);
});
