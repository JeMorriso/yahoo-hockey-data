const express = require('express');

//  JSON chart API
const { getChartData } = require('../js/chart')

const router = express.Router();

router.get('/', (req, res) => {
  res.render('index');
});

// callback must declared as async because we are using 'await' inside
router.get('/chart', async (req, res) => {
  res.json(await getChartData(req));
})

router.get('/league', (req, res) => {
  res.render('league');
})

router.get('/matchups', (req, res) => {
  res.send('graphs and standings');
})

module.exports = router;