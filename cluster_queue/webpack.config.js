const webpack = require('webpack');
const config = {
  entry: {
    results: __dirname + '/react/results.jsx',
    activity: __dirname + '/react/activity.jsx'
  },
  module: {
    rules: [{
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      },

      {
        test: /\.(png|svg|jpg|gif)$/,
        use: ['file-loader'],
      },
      {
        test: /\.jsx$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        include: __dirname + '/react/',
        query: {
          presets: ["@babel/env", "@babel/preset-react"]
        }
      },
    ]
  },
  output: {
    path: __dirname + '/static',
    publicPath: 'static/',
    filename: 'webpack-[name].js',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },

};

module.exports = config;
