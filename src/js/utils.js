const getDaysArray = function(start, end) {
  // Daylight savings time bug straight to the face
  // start = new Date(start.setHours(start.getHours() + 1));
  end = new Date(end.setHours(end.getHours() + 1));

  for (var arr=[],dt=new Date(start); dt<=end; dt.setDate(dt.getDate()+1)) {
      console.log(dt);
      arr.push(dt.toISOString().substring(0,10));
  }
  return arr;
};

module.exports = { getDaysArray }