// node 8.5.0+
const util = require('util');
const db = require('../js/db');

const { queryPromise, closePromise } = [db.query, db.end].map(util.promisify);

module.exports = { queryPromise, closePromise }