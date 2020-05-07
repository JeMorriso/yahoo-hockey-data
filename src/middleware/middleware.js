// Promisified mysql functions
const { queryPromise, closePromise } = require('../js/db');
// utility functions
const { getDaysArray } = require('../js/utils')

const getChartData = async (req, res, next) => {
  var start_date, end_date, category_snake_case; 
  
  // defaults
  if (req.body.start_date === undefined || req.body.end_date === undefined) {
    start_date = res.locals.min_date;
    // Don't show future dates on graph
    // TODO: test this is working correctly
    if (Date.now() < new Date(res.locals.max_date).getTime()) {
      // end_date = new Date().toISOString().substring(0,10);

      // for now, because league is paused. 
      end_date = "2020-03-02";
    } else {
      end_date = res.locals.max_date;
    }
  } else {
    start_date = req.body.start_date;
    end_date = req.body.end_date;
  }
  // default
  if (req.body.category === undefined) {
    category_snake_case = req.app.locals.category_snake_case;
  } else {
    // get the snake case version of the category
    try {
      sql = "select category_snake_case from scoring_category where category_name = ?;";
      let result = await queryPromise(sql, req.body.category);
      category_snake_case = result[0].category_snake_case;
    } catch (err) {
      console.log(err);
    } 
  }

  const daysArray = getDaysArray(new Date(start_date), new Date(end_date));
  try {
    // figure out if category is skater or goalie
    sql = "select position_type, category_name from scoring_category where category_snake_case = ?;";
    let result = await queryPromise(sql, category_snake_case);

    const position_type = result[0].position_type; 
    console.log(position_type);
    statsTable = `${position_type}_stats`;

    // const is block-scoped!
    res.locals.category = result[0].category_name;

    sql = `select name from fantasy_team;`;
    result = await queryPromise(sql);
    console.log(result);
    const teams = result.map(x => x.name);
    console.log(teams);

    // create object with teams as keys for adding list of stats as values
    var teamStats = {};
    teams.forEach(team => teamStats[team] = { 'datapoints': [], 'cumulative': [] })

    // can't figure out how to avoid wrapping category in single quotes which breaks the query.
      // Since the category is not user provided, we don't need to worry about sql injection
    sql = `
      select name, sum(${category_snake_case}) as stat, date_ as date
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
    `;
    result = await queryPromise(sql, [statsTable, start_date, end_date]);
    // assign results to correct team
    result.forEach(x => {
      teamStats[x.name].datapoints.push(x.stat);
    })
    // make cumulative 
    for (const team of Object.keys(teamStats)) {
      var cumulativeStats = [];
      // if initial value of zero is not provided then callback starts at index 1
      teamStats[team].datapoints.reduce( (acc, curr, i) => {
        // not sure why .push() doesn't work here - different return type probably
        return cumulativeStats[i] = acc + curr;
      }, 0);
      teamStats[team].cumulative = cumulativeStats;
    }
  } catch (err) {
    console.log(err);
  } finally {
    // do not close the pool! Won't work on subsequent requests
    // await closePromise();
  }

  res.locals.teamStats = teamStats;

  res.locals.colours = ['rgb(2,55, 190, 11)', 'rgb(251, 86, 7)', 'rgb(255, 0, 110)', 'rgb(131, 56, 236)', 'rgb(58, 134, 255)', 'rgb(239, 71, 111)', 'rgb(255, 209, 102)', 'rgb(6, 214, 160)', 'rgb(17, 138, 178)', 'rgb(7, 59, 76)', 'rgb(21, 96, 100)', 'rgb(251, 143, 103)']
  res.locals.dates = [];
  daysArray.forEach(date => res.locals.dates.push(date)); 

  next();
};

// Minimum and Maximum dates for flatpickr and default chart
const getMinMaxDates = async (req, res, next) => {
  sql = "select start_date, end_date from league";
  // const is block-scoped
  const result = await queryPromise(sql);
  res.locals.min_date = result[0].start_date;
  res.locals.max_date = result[0].end_date;

  next();
};

const getCategories = async (req, res, next) => {
  // TODO: fix these broken categories
  sql = `
    select category_name from scoring_category 
    where category_snake_case != 'shorthanded_points'
    and category_snake_case != 'goals_against_average'
    and category_snake_case != 'shutouts'
    and category_snake_case != 'game_winning_goals'
    and category_snake_case != 'wins';
    `;
  const result = await queryPromise(sql);
  res.locals.categories = [];
  result.forEach(el => res.locals.categories.push(el.category_name));
  next();
}

module.exports = { getMinMaxDates, getChartData, getCategories }

