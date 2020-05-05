const express = require('express');

//  JSON chart API
// const { getChartData } = require('../js/chart')
const { getMinMaxDates, getChartData } = require('../middleware/middleware')


const router = express.Router();

// Middlewares
router.use('/chart', getChartData);

router.get('/', (req, res) => {
  res.render('index');
});

// callback must declared as async because we are using 'await' inside
// this route is getting called by AJAX client-side graph javascript
router.get('/chart', async (req, res, next) => {
  // res.json(await getChartData(req));
  // not sure if this is best practice
  res.json({ category: res.locals.category, dates: res.locals.dates, colours: res.locals.colours, teamStats: res.locals.teamStats });
  // const noop = () => {};
})

router.get('/league', (req, res) => {
  res.render('league');
})

router.get('/matchups', (req, res) => {
  res.send('graphs and standings');
})

module.exports = router;