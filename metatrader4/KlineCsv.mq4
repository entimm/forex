#property strict

string fileName;

datetime curTime; // 当前时间

int OnInit()
{
    fileName = StringFormat("MT_%s_%s.csv", _Symbol, "F15");
    int fileHandle = FileOpen(fileName, FILE_WRITE|FILE_CSV, ',');
    if (fileHandle == INVALID_HANDLE)
    {
        Print("无法打开文件 ", fileName);
        return(INIT_FAILED);
    }

    FileWrite(fileHandle, "date,open,high,low,close,volume");

    int bars = iBars(_Symbol, PERIOD_M15);
    bars = 1000;
    for (int i = bars - 1; i >= 1; i--)
    {
        datetime time = iTime(_Symbol, PERIOD_M15, i);
        double open = iOpen(_Symbol, PERIOD_M15, i);
        double high = iHigh(_Symbol, PERIOD_M15, i);
        double low = iLow(_Symbol, PERIOD_M15, i);
        double close = iClose(_Symbol, PERIOD_M15, i);
        long volume = iVolume(_Symbol, PERIOD_M15, i);

        string line = StringFormat(
            "%s,%f,%f,%f,%f,%lld",
            TimeToString(time, TIME_DATE|TIME_MINUTES),
            open, high, low, close, volume
        );

        FileWrite(fileHandle, line);

        Print("K线数据已成功写入 ", line);

        curTime = time;
    }

    FileClose(fileHandle);

    return(INIT_SUCCEEDED);
}

void OnTick()
{
    datetime tickTime = iTime(_Symbol, PERIOD_M15, 1);
    if (tickTime <= curTime) {
        return;
    }
    curTime = tickTime;

    int fileHandle = FileOpen(fileName, FILE_WRITE|FILE_CSV|FILE_READ, ',');
    if (fileHandle == INVALID_HANDLE)
    {
        Print("无法打开文件 ", fileName);
        return;
    }

    datetime time = iTime(_Symbol, PERIOD_M15, 1);
    double open = iOpen(_Symbol, PERIOD_M15, 1);
    double high = iHigh(_Symbol, PERIOD_M15, 1);
    double low = iLow(_Symbol, PERIOD_M15, 1);
    double close = iClose(_Symbol, PERIOD_M15, 1);
    long volume = iVolume(_Symbol, PERIOD_M15, 1);

    string line = StringFormat(
        "%s,%f,%f,%f,%f,%lld",
        TimeToString(time, TIME_DATE|TIME_MINUTES),
        open, high, low, close, volume
    );
    FileSeek(fileHandle, 0, SEEK_END);
    FileWrite(fileHandle, line);

    Print("K线数据已成功写入 ", line);

    FileClose(fileHandle);
}
