/**
 * 累计收益额
 */
function calculateTotalReturnPercent(trades, initialCapital) {
  let totalProfitAmount = trades.reduce((totalReturn, trade) => totalReturn + trade['profit_amount'], 0);

  return ((totalProfitAmount / initialCapital) * 100).toFixed(2);
}

function investYears(trades) {
  let firstTradeDate = new Date(trades[0].date_desc.split(' - ')[0]);
  let lastTradeDate = new Date(trades[trades.length - 1].date_desc.split(' - ')[0]);

  return (lastTradeDate - firstTradeDate) / (365 * 24 * 60 * 60 * 1000);
}

/**
 * 年化收益率
 */
function calculateAnnualizedReturn(totalReturnPercent, years) {
  totalReturnPercent /= 100;

  const annualizedReturn = Math.pow((totalReturnPercent + 1), 1 / years) - 1;

  return (annualizedReturn * 100).toFixed(2);
}

/**
 * 最大回撤
 */
function calculateMaximumDrawdown(trades) {
  let maxDrawdown = 0;
  let maxCapital = trades[0].capital;
  let minCapital = trades[0].capital;

  for (let i = 1; i < trades.length; i++) {
    if (trades[i].capital >= maxCapital) {
      maxCapital = trades[i].capital
      minCapital = maxCapital;
    }
    if (trades[i].capital <= minCapital) {
      minCapital = trades[i].capital
      let drawdown = ((maxCapital - minCapital) / maxCapital * 100).toFixed(2);
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    }
  }

  return maxDrawdown;
}

/**
 * 胜率
 */
function calculateWinningPercentage(trades) {
  const winningTrades = trades.filter(trade => trade.profit_amount > 0);
  return ((winningTrades.length / trades.length) * 100).toFixed(2);
}

/**
 * 每笔平均盈亏
 */
function calculateAvgProfit(trades) {
  let totalProfitPercent = trades.reduce((totalReturn, trade) => totalReturn + trade['profit_percent'], 0);
  return ((totalProfitPercent / trades.length)).toFixed(2);
}

/**
 * 交易频率
 */
function calculateTradeFrequency(trades) {
  const firstTradeDate = new Date(trades[0].date_desc.split(' - ')[0]);
  const lastTradeDate = new Date(trades[trades.length - 1].date_desc.split(' - ')[0]);
  const tradingDays = (lastTradeDate - firstTradeDate) / (24 * 60 * 60 * 1000) / 7 * 5;

  return (trades.length / tradingDays).toFixed(2);
}
