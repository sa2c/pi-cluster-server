const webpack = require('webpack');
const config = {
    entry: __dirname + '/react/results.jsx',
    module: {
        rules: [
            {
                test: /\.jsx$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                include: __dirname,
                query:git clone https://github.com/bhauman/devcards.git {
                    presets: [ "es2015", "react", "react-hmre" ]
                }
            }
        ]
    },
  output: {
    path: __dirname + '/static',
    filename: 'app.js',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },

};

module.exports = config;
