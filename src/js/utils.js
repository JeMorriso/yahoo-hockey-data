const getDaysArray = function(start, end) {
  // Daylight savings time bug straight to the face
  // start = new Date(start.setHours(start.getHours() + 1));
  end = new Date(end.setHours(end.getHours() + 1));

  for (var arr=[],dt=new Date(start); dt<=end; dt.setDate(dt.getDate()+1)) {
      arr.push(dt.toISOString().substring(0,10));
  }
  return arr;
};

const cleanGroupbyTeamResult = (teams, result, daysArray) => {
  let teamDateStat = {};
  teams.forEach(team => teamDateStat[team] = {});
  for (team in teamDateStat) {
    daysArray.forEach(day => {
      teamDateStat[team][day] = 0;
    })
  }
  for (row of result) {
    teamDateStat[row.name][row.date] = row.stat;
  }
  return teamDateStat;
} 

module.exports = { getDaysArray, cleanGroupbyTeamResult }