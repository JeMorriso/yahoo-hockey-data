const express = require('express');

//  JSON chart API
// const { getChartData } = require('../js/chart')
const { getMinMaxDates, getChartData } = require('../middleware/middleware')

const router = express.Router();

// Middlewares
// Min / Max is above in middleware stack so getChartData can use start and end dates
router.use('/chart', getMinMaxDates);
router.use('/chart', getChartData);

router.get('/', (req, res) => {
  res.render('index');
});

// callback must declared as async because we are using 'await' inside
// this route is getting called by AJAX client-side graph javascript
router.get('/chart', async (req, res, next) => {
  // not sure if this is best practice
  res.json({ category: res.locals.category, 
    dates: res.locals.dates, 
    colours: res.locals.colours, 
    teamStats: res.locals.teamStats,
    min_date: res.locals.min_date,
    max_date: res.locals.max_date,
  });
})

router.get('/league', (req, res) => {
  res.render('league');
})

router.get('/matchups', (req, res) => {
  res.send('graphs and standings');
})

module.exports = router;