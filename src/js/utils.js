const getDaysArray = function(start, end) {
  for(var arr=[],dt=new Date(start); dt<=end; dt.setDate(dt.getDate()+1)){
      arr.push(dt.toISOString().substring(0,10));
  }
  return arr;
};

module.exports = { getDaysArray }