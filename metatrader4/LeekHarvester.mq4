#property strict


#define MAGICMA 952736 // 开单特征数字

#define X_FAST_MA 15 // 短期均线
#define X_SLOW_MA 60 // 长期均线
#define X_LIFE_MA 432 // 生命均线

#define X_FAST_EMA 7 // 快速EMA周期
#define X_SLOW_EMA 14 // 慢速EMA周期
#define X_SIGNAL_SMA 6 // 信号线SMA周期

#define X_SLIPPAGE 35 // 滑点数

#include "tradeLong.mqh"
#include "tradeShort.mqh"


// 方向枚举
enum DirectionEnum
{
    None,
    Up,
    Down
};

// 合并K线结构
struct UnionCandle
{
    datetime time;
    double high;
    double low;
    DirectionEnum direction;
};

// 最新K线
UnionCandle latestCandle = {};

//////////////////// 条件数据 START
datetime curTime; // 当前时间

double fastMaValue; // 快线
double slowMaValue; // 慢线
double lifeMaValue; // 生命线

double macdLine; // macd主线

double lowestFractalPrice = 999999; // 底分型价
double highestFractalPrice = -999999; // 顶分型价
bool foundBottomFtractal = false;
bool foundTopFtractal = false;
//////////////////// 条件数据 END

int OnInit()
{
    int beforeN = 100;

    latestCandle.time = iTime(_Symbol, PERIOD_M15, beforeN);
    latestCandle.high = iHigh(_Symbol, PERIOD_M15, beforeN);
    latestCandle.low = iLow(_Symbol, PERIOD_M15, beforeN);
    latestCandle.direction = None;

    for(int i = beforeN - 1; i > 1; i --) {
        datetime preTime = iTime(_Symbol, PERIOD_M15, i);
        Print("分析前面的底分型: ", preTime);

        calcalateFractal(iTime(_Symbol, PERIOD_M15, i), iHigh(_Symbol, PERIOD_M15, i), iLow(_Symbol, PERIOD_M15, i));

        fastMaValue = iMA(_Symbol, PERIOD_M15, X_FAST_MA, 0, MODE_SMA, PRICE_CLOSE, i);
        slowMaValue = iMA(_Symbol, PERIOD_M15, X_SLOW_MA, 0, MODE_SMA, PRICE_CLOSE, i);

        if (fastMaValue > slowMaValue) {
            Print("金叉，重置分型: ", preTime);
            lowestFractalPrice = 999999;
        }
    }

    Print("EA 预加载..." );

    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
    Print("EA 运行结束，已经卸载。" );
}

void OnTick()
{
    datetime tickTime = iTime(_Symbol, PERIOD_M15, 1);
    if (tickTime <= curTime) {
        return;
    }

    //////////////////// 数据准备 START
    curTime = tickTime;

    foundBottomFtractal = false;
    foundTopFtractal = false;
    calcalateFractal(curTime, iHigh(_Symbol, PERIOD_M15, 1), iLow(_Symbol, PERIOD_M15, 1));

    fastMaValue = iMA(_Symbol, PERIOD_M15, X_FAST_MA, 0, MODE_SMA, PRICE_CLOSE, 1);
    slowMaValue = iMA(_Symbol, PERIOD_M15, X_SLOW_MA, 0, MODE_SMA, PRICE_CLOSE, 1);
    lifeMaValue = iMA(_Symbol, PERIOD_M15, X_LIFE_MA, 0, MODE_SMA, PRICE_CLOSE, 1);

    macdLine = iMACD(_Symbol, PERIOD_M15, X_FAST_EMA, X_SLOW_EMA, X_SIGNAL_SMA, PRICE_CLOSE, MODE_MAIN, 1);
    //////////////////// 数据准备 END

    runLong(); // 做多
    runShort(); // 做空

    Print("data=", curTime, "#", fastMaValue, "#", slowMaValue, "#", lifeMaValue, "#【", macdLine, "】#", lowestFractalPrice, "#", highestFractalPrice);
}

// 计算顶底分型
void calcalateFractal(datetime time, double high, double low)
{
    if (latestCandle.time >= time) {
        return;
    }
    if (latestCandle.high < high && latestCandle.low < low) {
        if (latestCandle.direction == Down) {
            foundBottomFtractal = true;
            Print("发现底分型:", latestCandle.time, " 价格=", latestCandle.low);
            if (latestCandle.low <= lowestFractalPrice) {
                lowestFractalPrice = latestCandle.low;
                Print("确认更低的底分型:", latestCandle.time, " 价格=", lowestFractalPrice);
            }
        }
        latestCandle.high = high;
        latestCandle.low = low;
        latestCandle.direction = Up;
    } else if (latestCandle.high > high && latestCandle.low > low) {
        if (latestCandle.direction == Up) {
            foundTopFtractal = true;
            Print("发现顶分型:", latestCandle.time, " 价格=", latestCandle.high);
            if (latestCandle.high >= highestFractalPrice) {
                highestFractalPrice = latestCandle.high;
                Print("确认更高的顶分型:", latestCandle.time, " 价格=", highestFractalPrice);
            }
        }
        latestCandle.high = high;
        latestCandle.low = low;
        latestCandle.direction = Down;
    } else {
        if (latestCandle.direction == Up) {
            latestCandle.high = fmax(latestCandle.high, high);
            latestCandle.low = fmax(latestCandle.low, low);
        } else if (latestCandle.direction == Down) {
            latestCandle.high = fmin(latestCandle.high, high);
            latestCandle.low = fmin(latestCandle.low, low);
        } else {
            latestCandle.high = fmax(latestCandle.high, high);
            latestCandle.low = fmin(latestCandle.low, low);
        }
    }

    latestCandle.time = time;
}

// 统计订单数
int CountOrder(int OP_Type)
{
    int count = 0;

    for (int i = 0; i < OrdersTotal(); i++)
    {
        if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES) == false)
        {
            continue;
        }
        if(OrderMagicNumber() != MAGICMA || OrderSymbol() != _Symbol)
        {
            continue;
        }
        if(OrderType() == OP_Type)
        {
            count++;
        }
    }

    return count;
}

// 尝试关闭订单
void TryCloseOrder(int OP_Type)
{
    for (int i = 0; i < OrdersTotal(); i++)
    {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES) == false)
        {
            continue;
        }
        if (OrderMagicNumber() != MAGICMA || OrderSymbol() != _Symbol)
        {
            continue;
        }
        if (OrderType() == OP_BUY && OP_Type == OP_BUY)
        {
            Print("关闭[多]单: ", OrderTicket());
            if(!OrderClose(OrderTicket(), OrderLots(), Bid, X_SLIPPAGE, White)) {
                Print("关闭[多]单出错", GetLastError());
            }
            continue;
        }
        if (OrderType() == OP_SELL && OP_Type == OP_SELL)
        {
            Print("关闭[空]单: ", OrderTicket());
            if (!OrderClose(OrderTicket(), OrderLots(), Ask, X_SLIPPAGE, White)) {
                Print("关闭[空]单出错", GetLastError());
            }
            continue;
        }
    }
}