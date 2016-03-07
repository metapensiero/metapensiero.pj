// -*- coding: utf-8 -*-
// :Progetto:  metapensiero.pj -- webpack config
// :Creato:    dom 06 mar 2016 20:17:46 CET
// :Autore:    Alberto Berti <alberto@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

var path = require('path');


module.exports = {
    context: __dirname + "/js",
    entry: "./colorflash/colorflash.js",
    output: {
        path: __dirname + "/www/colorflash",
        filename: "bundle.js"
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                loader: 'babel',
                query: {
                    presets: ['es2015'],
                    plugins: ['transform-runtime']
                }
            }
        ],
        preLoaders: [
            {
                test: /\.js$/,
                loader: "source-map-loader"

            }

        ]
    },
    resolve: {
        alias: {
            mylib: path.resolve('./js/mylib')
        }
    },
    devtool: "#source-map"
};
