// Promisified mysql functions
const { queryPromise, closePromise } = require('../js/db');
// utility functions
const { getDaysArray, cleanGroupbyTeamResult } = require('../js/utils')

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
    statsTable = `${position_type}_stats`;

    // const is block-scoped!
    res.locals.category = result[0].category_name;

    sql = `select name from fantasy_team;`;
    result = await queryPromise(sql);
    console.log(result);
    const teams = result.map(x => x.name);

    // create object with teams as keys for adding list of stats as values
    var teamStats = {};
    teams.forEach(team => teamStats[team] = { 'datapoints': [], 'cumulative': [], 'rollingAverage': [] });

    // can't figure out how to avoid wrapping category in single quotes which breaks the query.
      // Since the category is not user provided, we don't need to worry about sql injection
    sql = `
      select name, sum(${category_snake_case}) as stat, date_ as date
      from fantasy_team as t
      join (select * from roster where selected_position != 'BN') as r
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
    let i = 0;
    // TODO: fix bug here
    result.forEach(x => {
      // post-increment; i increments when loop not entered, and for each loop iteration
      while (daysArray[i++ % daysArray.length] !== x.date) {
        teamStats[x.name].datapoints.push(0);
      }
      teamStats[x.name].datapoints.push(x.stat);
    })
    // make cumulative - want to have start value be relative to beginning of season instead of zero, so make second db query
    sql = `
      select name, sum(${category_snake_case}) as stat, date_ as date
      from fantasy_team as t
      join (select * from roster where selected_position != 'BN') as r
      on t.id = r.team_id
      join (
        select * 
        from ??
        where date_ < ?
      ) as s
      on s.player_id = r.player_id and s.date_ >= r.start_date and s.date_ <= r.end_date
      group by team_id
      order by name;
    `;
    let result2 = await queryPromise(sql, [statsTable, start_date]);

    // cumulative stats
    for (const team of Object.keys(teamStats)) {
      var cumulativeStats = [];
      var initQ = 0;
      // find initial quantity
      if (Array.isArray(result2) && result2.length) {
        teamElement = result2.find(el => el.name == team);
        if (typeof teamElement !== 'undefined') {
          initQ = teamElement.stat;
        }
      }
      // if initial value is not provided then callback starts at index 1
      // set acc to start at cumulative quantity for each team up to that date
      teamStats[team].datapoints.reduce( (acc, curr, i) => {
        // not sure why .push() doesn't work here - different return type probably
        return cumulativeStats[i] = acc + curr;
      }, initQ);
      teamStats[team].cumulative = cumulativeStats;
    }

    // increment times by 1 hour for DST
    let s = new Date(start_date);
    s = new Date(s.setHours(s.getHours() + 1))
    let e = new Date(end_date);
    e = new Date(e.setHours(e.getHours() + 1))
    // week-long rolling averages
    let rollingStart = new Date(s);
    rollingStart.setDate(rollingStart.getDate() - 3);
    let rollingEnd = new Date(e);
    rollingEnd.setDate(rollingEnd.getDate() + 3);
    rollingDaysArray = getDaysArray(rollingStart, rollingEnd);

    // third query for calculating rolling averages taking +/- 3 days
    sql = `
      select name, sum(${category_snake_case}) as stat, date_ as date
      from fantasy_team as t
      join (select * from roster where selected_position != 'BN') as r
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
    let result3 = await queryPromise(sql, [statsTable, rollingStart, rollingEnd]);

    rollingTeamDateStat = cleanGroupbyTeamResult(teams, result3, rollingDaysArray);

    // rolling average stats
    for (const team of Object.keys(teamStats)) {
      let sum = 0;
      rollingDaysArray.slice(0,7).forEach(day => {
        sum += rollingTeamDateStat[team][day];
      })
      teamStats[team].rollingAverage.push(sum/7);
      rollingDaysArray.slice(4,-3).forEach((day, i) => {
        sum -= rollingTeamDateStat[team][rollingDaysArray[i]];
        sum += rollingTeamDateStat[team][rollingDaysArray[i+7]];
        teamStats[team].rollingAverage.push(sum/7);
      });
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

