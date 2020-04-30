const express = require('express');

// Promisified mysql functions
const { queryPromise, closePromise } = require('../js/db');

const router = express.Router();

router.get('/', (req, res) => {
  res.render('index');
});

// callback must declared as async because we are using 'await' inside
router.get('/chart', async (req, res) => {
  if (req.query.start_date !== undefined) {
    start_date = req.query.start_date;
  } else {
    start_date = req.app.locals.start_date;
  }
  // console.log(start_date);

  if (req.query.end_date !== undefined) {
    end_date = req.query.end_date;
  } else {
    end_date = req.app.locals.end_date;
  }
  // console.log(end_date);

  if (req.query.category_snake_case !== undefined) {
    category_snake_case = req.query.category_snake_case;
  } else {
    category_snake_case = req.app.locals.category_snake_case;
  }
  // console.log(category_snake_case);

  // figure out if category is skater or goalie
  sql = "select position_type, category_name from scoring_category where category_snake_case = ?";

  try {
    var result = await queryPromise(sql, category_snake_case);

    const position_type = result[0].position_type; 
    console.log(position_type);
    statsTable = `${position_type}_stats`;

    // const is block-scoped!
    var category = result[0].category_name;

    // can't figure out how to avoid wrapping category in single quotes which breaks the query.
      // Since the category is not user provided, we don't need to worry about sql injection
    sql = `
      select name, sum(${category_snake_case}), date_ as date
      from fantasy_team as t
      join roster as r
      on t.id = r.team_id
      join (
        select * 
        from ??
        where date_ >= ? and date_ <= ?
      ) as s
      on s.player_id = r.player_id and s.date_ >= r.start_date and s.date_ <= r.end_date
      group by team_id, date_
      order by name, date_;
    `
    
    result = await queryPromise(sql, [statsTable, start_date, end_date]);
    console.log(result);

  } catch (err) {
    console.log(err);
  } finally {
    // do not close the pool! Won't work on subsequent requests
    // await closePromise();
  }

  res.json({ category, start_date, end_date })
})

router.get('/league', (req, res) => {
  res.render('league');
})

router.get('/matchups', (req, res) => {
  res.send('graphs and standings');
})

module.exports = router;