const mysql = require('mysql');
const util = require('util');

require('dotenv').config();

// use connection pool so that connection does not close by itself on Heroku
const db = mysql.createPool({
  host: process.env.HOST,
  user: process.env.USER,
  password: process.env.PASSWORD,
  database: process.env.DATABASE
});

// const { queryPromise, closePromise } = [db.query, db.end].map(util.promisify);
// const queryPromise = util.promisify(db.query);
// const closePromise = util.promisify(db.end);

// need to bind 'this' to mysql pool because otherwise get 'undefined' for Pool prototype in mysql module
const queryPromise = util.promisify(db.query).bind(db);
const closePromise = util.promisify(db.end).bind(db);

module.exports = { queryPromise, closePromise }