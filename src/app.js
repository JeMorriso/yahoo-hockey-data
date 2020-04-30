const express = require('express');
const path = require('path');

const port = process.env.PORT || 3000;

const app = express();

const routes = require('./routers/routes');

// query parser is enabled by default - see Express docs
app.set('view engine', 'ejs');

// serve the public directory
app.use(express.static(path.join(__dirname, '../public')));
app.use("/dist", express.static(path.join(__dirname, '../dist')))

// endpoints in routes file start with '/'
app.use('/', routes)

// set global variables that are available to each route through req.app.locals
app.locals.start_date = '2019-10-02';
// default date is Today
  // ISO 8601 format same as start_date + time data so get substring
// app.locals.end_date = new Date().toISOString().substring(0,10);
app.locals.end_date = '2020-03-02'

// default to goals
app.locals.category_snake_case = 'goals';

app.listen(port, () => {
  console.log('app listening on port', port);
});