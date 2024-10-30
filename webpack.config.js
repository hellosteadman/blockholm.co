const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './sidekick/theme/assets/js/init.js',
    mode: 'production',
    output: {
        path: path.resolve(__dirname, './sidekick/theme/static/js'),
        filename: 'theme.js',
        devtoolModuleFilenameTemplate: '[absolute-resource-path]'
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                exclude: /\.png|jpg|jpeg|gif|svg$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader',
                    'sass-loader'
                ]
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: 'babel-loader'
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin(
            {
                filename: '../css/theme.css'
            }
        )
    ],
    devtool: 'source-map',
    watch: true
}
