const express = require('express');

const router = express.Router();

router.get('/', (req, res) => {
  res.send('Bobby Orr Image goes here');
});

router.get('/league', (req, res) => {
  res.send('graphs and standings');
})

router.get('/matchup/:matchupId', (req, res) => {
  res.send('graphs and standings');
})

module.exports = router;