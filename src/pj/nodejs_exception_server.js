
var port = 1 * process.argv[2];

require('exception-server').runServer({'port': port}, function() {
    process.stdout.write('Server ready, PYXC-PJ. Go, go, go!\n');
});
