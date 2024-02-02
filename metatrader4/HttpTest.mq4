extern string SERVER_IP = "enjoy.test";

string SendResquest(string httpType, string url, string bodyData = "", string headers = "", int timeout = 10000)
{
    uchar bodyDataCharArray[];
    uchar resultDataCharArray[];
    string resultHeader;

    ArrayResize(bodyDataCharArray, StringToCharArray(bodyData, bodyDataCharArray) - 1);

    int response = WebRequest(httpType, url, headers, timeout, bodyDataCharArray, resultDataCharArray, resultHeader);
    if (response != 200) {
        Print("Error when trying to call API: ", response);
        Print("Error code: ", GetLastError());
        Print("url: ", url);
        Print("body: ", bodyData);
        return "";
    }
    Print("API result:", response);

    return CharArrayToString(resultDataCharArray);
}

void OnTick() {
    string body = StringFormat(
        "%s,%s,%s,%s,%s,%s",
        TimeToStr(iTime(_Symbol, PERIOD_M15, 1)),
        DoubleToStr(iOpen(_Symbol, PERIOD_M15, 1)),
        DoubleToStr(iHigh(_Symbol, PERIOD_M15, 1)),
        DoubleToStr(iLow(_Symbol, PERIOD_M15, 1)),
        DoubleToStr(iClose(_Symbol, PERIOD_M15, 1)),
        DoubleToStr(iVolume(_Symbol, PERIOD_M15, 1))
    );
    string url = StringFormat("http://%s/metatrade.php", SERVER_IP);
    string response = SendResquest("POST", url, body, "Content-Type: application/text", 5000);

    Print("响应:", response);
}