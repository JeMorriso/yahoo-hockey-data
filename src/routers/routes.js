const express = require('express');

//  JSON chart API
const { getMinMaxDates, getChartData, getCategories } = require('../middleware/middleware')

const router = express.Router();

// Middlewares
// Min / Max is above in middleware stack so getChartData can use start and end dates
router.use('/chart', getMinMaxDates);
router.use('/chart', getChartData);
router.use('/flatpickr', getMinMaxDates);
router.use('/league', getCategories);

router.get('/', (req, res) => {
  res.render('index');
});

// this route is getting called by AJAX client-side graph javascript
router.post('/chart', (req, res, next) => {
  // add debugging statement in for heroku logs
  console.log("Request Headers: ");
  console.log(req.headers);

  // res.setHeader('Access-Control-Allow-Origin', '*')

  // add debugging statement in for heroku logs
  console.log("Response Headers: ");
  console.log(res._headers);

  // not sure if this is best practice
  res.json({ category: res.locals.category, 
    dates: res.locals.dates, 
    colours: res.locals.colours, 
    teamStats: res.locals.teamStats
  });
});

router.post('/flatpickr', (req, res) => {
  res.json({ 
    min_date: res.locals.min_date,
    max_date: res.locals.max_date
  });
});

router.get('/league', (req, res) => {
  res.render('league', { categories: res.locals.categories });
});

router.get('/matchups', (req, res) => {
  res.send('graphs and standings');
});

module.exports = router;