const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/flatpickr.js',
  output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'flatpickrBundle.js'
  },
  module: {
		rules: [
			{
				test: /.css$/,
				use: [
					{
						loader: 'style-loader'
					},
					{
						loader: 'css-loader',
						options: {
							sourceMap: true
						}
					}
				]
      }
    ]
  }
};