void runShort()
{
    if (fastMaValue < slowMaValue) {
        Print("死叉，重置顶分型: ", curTime);
        highestFractalPrice = -999999;
    }

    bool bCondition1 = fastMaValue > slowMaValue;
    bool bCondition2 = fastMaValue <= lifeMaValue;
    bool bCondition3 = slowMaValue <= lifeMaValue;
    bool bCondition4 = highestFractalPrice > -999999;

    Print("买入空单条件: ", curTime, " | ", bCondition1, " | ", bCondition2, " | ", bCondition3, " | ", bCondition4);

    if (foundTopFtractal && bCondition1 && bCondition2 && bCondition3 && bCondition4) {
        exeBuyShort(highestFractalPrice);
    }

    ////////////////////////////////

    bool sCondition1_1 = fastMaValue <= slowMaValue;
    bool sCondition1_2 = macdLine > 0;

    bool sCondition2_1 = slowMaValue > lifeMaValue;

    Print("平仓空单条件: ", curTime, " | ", sCondition1_1, " | ", sCondition1_2, " | ", sCondition2_1);

    if ((sCondition1_1 && sCondition1_2) || sCondition2_1) {
        exeCloseShort();
    }
}

// 执行空单购买
void exeBuyShort(double fractalPrice)
{
    Print("尝试买入空单", curTime);
    if (CountOrder(OP_SELL) > 0) {
        Print("放弃买入空单: 已经有持仓了");
        return;
    }

    if (fabs(1 - fractalPrice / Ask)  * 100 > 0.8) {
        Print("放弃买入空单: 止损太高了");
        return;
    }

    Print("执行买入空单", curTime);
    double stopPrice = NormalizeDouble(fractalPrice + X_SLIPPAGE * Point, Digits);
    if (!OrderSend(Symbol(), OP_SELL, 1.0, Ask, X_SLIPPAGE, stopPrice, 0, "TEST-COMMENT", MAGICMA, 0, Green)) {
        Print("开空单出错", GetLastError());
    }
}

// 执行空单关闭
void exeCloseShort()
{
    Print("尝试平仓空单", curTime);
    TryCloseOrder(OP_SELL);
}