// 计算带有时间信息的均线
function calMaWithTime(data, period) {
  const averages = [];

  for (let i = 0; i < data.length; i++) {
    let sum = 0;

    for (let j = Math.max(0, i - period + 1); j <= i; j++) {
      sum += data[j].close;
    }

    const average = sum / Math.min(period, i + 1);
    averages.push({time: data[i].time, value: average});
  }

  return averages;
}

// 计算带有时间信息的MACD
function calMacdWithTime(data, shortPeriod, longPeriod, signalPeriod) {
  const shortEMA = calEmaWithTime(data, shortPeriod, 'close');
  const longEMA = calEmaWithTime(data, longPeriod, 'close');

  const macdLine = [];
  for (let i = 0; i < longEMA.length; i++) {
    macdLine.push({time: longEMA[i].time, value: shortEMA[i].value - longEMA[i].value});
  }

  const signalLine = calEmaWithTime(macdLine, signalPeriod, 'value');

  // 计算MACD柱状图
  const histogram = [];
  for (let i = 0; i < macdLine.length; i++) {
    histogram.push({time: macdLine[i].time, value: (macdLine[i].value - signalLine[i].value) * 2});
  }

  return {macdLine, signalLine, histogram};
}

// 计算带有时间信息的指数移动平均线
function calEmaWithTime(data, period, field) {
  const smoothingFactor = 2 / (period + 1);
  const ema = [{time: data[0].time, value: data[0][field]}]; // 初始值等于第一个数据点的值

  for (let i = 1; i < data.length; i++) {
    const currentEMA =
      (data[i][field] - ema[i - 1].value) * smoothingFactor + ema[i - 1].value;
    ema.push({time: data[i].time, value: currentEMA});
  }

  return ema;
}