const express = require('express');

const port = process.env.PORT || 3000;

const app = express();

const routes = require('./routers/routes');

app.set('view engine', 'ejs');

// endpoints in routes file start with '/'
app.use('/', routes)

app.listen(port, () => {
  console.log('app listening on port', port);
});