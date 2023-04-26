'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

// '"http://api.kurush7.cloud.okteto.net/api/v2/"',
// '"http://localhost:5000/api/v2/"',

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_URL: '"http://api.kurush7.cloud.okteto.net/api/v2/"',
  CLIENT_ID: '"pRiDvVWqbMdVcqUcubD0Y54V"',
  CLIENT_SECRET: '"tMWy9xDK6CaCe6LfqpO3BIqkjVgm8eEUnMLAdHaV5IO32Riu"'
})
