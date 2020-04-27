const mysql = require('mysql');

require('dotenv').config();

// use connection pool so that connection does not close by itself on Heroku
const db = mysql.createPool({
  host: process.env.HOST,
  user: process.env.USER,
  password: process.env.PASSWORD,
  database: process.env.DATABASE
});

module.exports = db;