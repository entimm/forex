void runLong()
{
    if (fastMaValue > slowMaValue) {
        Print("金叉，重置底分型: ", curTime);
        lowestFractalPrice = 999999;
    }

    bool bCondition1 = fastMaValue < slowMaValue;
    bool bCondition2 = fastMaValue >= lifeMaValue;
    bool bCondition3 = slowMaValue >= lifeMaValue;
    bool bCondition4 = lowestFractalPrice < 999999;

    Print("买入多单条件: ", curTime, " | ", bCondition1, " | ", bCondition2, " | ", bCondition3, " | ", bCondition4);

    if (foundBottomFtractal && bCondition1 && bCondition2 && bCondition3 && bCondition4) {
        exeBuyLong(lowestFractalPrice);
    }

    ////////////////////////////////

    bool sCondition1_1 = fastMaValue >= slowMaValue;
    bool sCondition1_2 = macdLine < 0;

    bool sCondition2_1 = slowMaValue < lifeMaValue;

    Print("平仓多单条件: ", curTime, " | ", sCondition1_1, " | ", sCondition1_2, " | ", sCondition2_1);

    if ((sCondition1_1 && sCondition1_2) || sCondition2_1) {
        exeCloseLong();
    }
}

// 执行多单购买
void exeBuyLong(double fractalPrice)
{
    Print("尝试买入多单", curTime);
    if (CountOrder(OP_BUY) > 0) {
        Print("放弃买入多单: 已经有持仓了");
        return;
    }

    if (fabs(1 - fractalPrice / Ask)  * 100 > 0.8) {
        Print("放弃买入多单: 止损太高了");
        return;
    }

    Print("执行买入多单", curTime);
    double stopPrice = NormalizeDouble(fractalPrice - X_SLIPPAGE * Point, Digits);
    if (!OrderSend(Symbol(), OP_BUY, 1.0, Ask, X_SLIPPAGE, fractalPrice, 0, "TEST-COMMENT", MAGICMA, 0, Red)) {
        Print("开多单出错", GetLastError());
    }
}

// 执行多单关闭
void exeCloseLong()
{
    Print("尝试平仓多单", curTime);
    TryCloseOrder(OP_BUY);
}