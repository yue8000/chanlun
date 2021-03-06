# encoding: UTF-8

"""
缠论模块相关的GUI控制组件
"""
from vtGateway import VtSubscribeReq
from uiBasicWidget import QtGui, QtCore, BasicCell,BasicMonitor,TradingWidget
from eventEngine import *
import pyqtgraph as pg
import numpy as np
import pymongo
from pymongo.errors import *
from datetime import datetime, timedelta
#from vn.demo.ctpdemo.demoUi import *



########################################################################
class ChanlunEngineManager(QtGui.QWidget):
    """chanlun引擎管理组件"""
    signal = QtCore.pyqtSignal(type(Event()))

    # ----------------------------------------------------------------------
    def __init__(self, chanlunEngine, eventEngine, mainEngine, parent=None):
        """Constructor"""
        super(ChanlunEngineManager, self).__init__(parent)

        self.chanlunEngine = chanlunEngine
        self.eventEngine = eventEngine
        self.mainEngine = mainEngine

        self.penLoaded = False
        self.instrumentid = ''

        self.initUi()
        self.registerEvent()

        # 记录日志
        self.chanlunEngine.writeChanlunLog(u'缠论引擎启动成功')

        # ----------------------------------------------------------------------

    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(u'缠论策略')


        # 金融图
        self.PriceW = PriceWidget(self.eventEngine, self.chanlunEngine, self)

        # 期货代码输入框
        self.codeEdit = QtGui.QLineEdit()
        self.codeEdit.setPlaceholderText(u'在此输入期货代码')
        self.codeEdit.setMaximumWidth(200)
        # 按钮
        penButton = QtGui.QPushButton(u'分笔')
        segmentButton = QtGui.QPushButton(u'分段')
        shopButton = QtGui.QPushButton(u'买卖点')
        restoreButton = QtGui.QPushButton(u'还原')

        penButton.clicked.connect(self.pen)
        segmentButton.clicked.connect(self.segment)
        shopButton.clicked.connect(self.shop)
        restoreButton.clicked.connect(self.restore)

        # Chanlun组件的日志监控
        self.chanlunLogMonitor = QtGui.QTextEdit()
        self.chanlunLogMonitor.setReadOnly(True)
        self.chanlunLogMonitor.setMaximumHeight(200)

        # 设置布局
        self.hbox2 = QtGui.QHBoxLayout()
        self.hbox2.addWidget(self.codeEdit)
        self.hbox2.addWidget(penButton)
        self.hbox2.addWidget(segmentButton)
        self.hbox2.addWidget(shopButton)
        self.hbox2.addWidget(restoreButton)
        self.hbox2.addStretch()


        tickButton = QtGui.QPushButton(u'Tick')
        oneMButton = QtGui.QPushButton(u"1分")
        fiveMButton = QtGui.QPushButton(u'5分')
        fifteenMButton = QtGui.QPushButton(u'15分')
        thirtyMButton = QtGui.QPushButton(u'30分')
        dayButton = QtGui.QPushButton(u'日')
        weekButton = QtGui.QPushButton(u'周')
        monthButton = QtGui.QPushButton(u'月')

        tickButton.clicked.connect(self.openTick)

        self.vbox1 = QtGui.QVBoxLayout()

        self.vbox2 = QtGui.QVBoxLayout()
        self.vbox1.addWidget(self.PriceW)
        self.vbox2.addWidget(tickButton)
        self.vbox2.addWidget(oneMButton)
        self.vbox2.addWidget(fiveMButton)
        self.vbox2.addWidget(fifteenMButton)
        self.vbox2.addWidget(thirtyMButton)
        self.vbox2.addWidget(dayButton)
        self.vbox2.addWidget(weekButton)
        self.vbox2.addWidget(monthButton)
        self.vbox2.addStretch()

        self.hbox3 = QtGui.QHBoxLayout()
        self.hbox3.addStretch()
        self.hbox3.addLayout(self.vbox1)
        self.hbox3.addLayout(self.vbox2)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        #vbox.addWidget(self.scrollArea)
        self.vbox.addWidget(self.chanlunLogMonitor)
        self.setLayout(self.vbox)

        self.codeEdit.returnPressed.connect(self.updateSymbol)

    def updateSymbol(self):
        """合约变化"""
        # 读取组件数据
        instrumentid = str(self.codeEdit.text())
        # 获取合约
        # instrument = self.__chanlunEngine.selectInstrument(instrumentid)

        # 重新注册事件监听
        self.eventEngine.unregister(EVENT_TICK + self.instrumentid, self.signal.emit)
        self.eventEngine.register(EVENT_TICK + instrumentid, self.signal.emit)

        # 订阅合约
        # self.__mainEngine.subscribe(instrumentid, instrument['ExchangeID'])

        # 订阅合约[仿照ctaEngine.py写的]
        contract = self.mainEngine.getContract(instrumentid)
        if contract:
            req = VtSubscribeReq()
            req.symbol = contract.symbol

            self.mainEngine.subscribe(req, contract.gatewayName)
        else:
            self.writeChanlunLog(u'交易合约%s无法找到' % (instrumentid))

        # 更新目前的合约
        self.instrumentid = instrumentid

    # ----------------------------------------------------------------------
    def openTick(self):
        """切换成tick图"""
        self.chanlunEngine.writeChanlunLog(u'打开tick图')
        self.vbox1.removeWidget(self.PriceW)


    # ----------------------------------------------------------------------
    def segment(self):
        """加载分段"""
        self.chanlunEngine.writeChanlunLog(u'分段')

    # ----------------------------------------------------------------------
    def shop(self):
        """加载买卖点"""
        self.chanlunEngine.writeChanlunLog(u'买卖点')

    # ----------------------------------------------------------------------
    def restore(self):
        """还原初始k线状态"""

        self.chanlunEngine.writeChanlunLog(u'还原')

    # ----------------------------------------------------------------------
    def pen(self):
        """加载分笔"""
        if not self.pen:
            self.chanlunEngine.loadSetting()
     #       self.initStrategyManager()  此处应该修改成分笔的函数
        self.pen = True
        self.chanlunEngine.writeChanlunLog(u'分笔加载成功')

    # ----------------------------------------------------------------------
    def updateChanlunLog(self, event):
        """更新缠论相关日志"""

        self.eventEngine.register(EVENT_CHANLUN_LOG, self.signal.emit)

        log = event.dict_['data']
        print 'chanlun:'
        print type(log)
        content = '\t'.join([log.logTime, log.logContent])
        self.chanlunLogMonitor.append(content)

    # ----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.signal.connect(self.registerEvent)
        self.eventEngine.register(EVENT_CHANLUN_LOG, self.signal.emit)

########################################################################
class PriceWidget(QtGui.QWidget):
    """用于显示价格走势图"""
    signal = QtCore.pyqtSignal(type(Event()))

    # tick图的相关参数、变量
    listlastPrice = np.empty(1000)

    fastMA = 0
    midMA = 0
    slowMA = 0
    listfastMA = np.empty(1000)
    listmidMA = np.empty(1000)
    listslowMA = np.empty(1000)
    tickFastAlpha = 0.0333    # 快速均线的参数,30
    tickMidAlpha = 0.0167     # 中速均线的参数,60
    tickSlowAlpha = 0.0083    # 慢速均线的参数,120

    ptr = 0
    ticktime = None  # tick数据时间

    # K线图EMA均线的参数、变量
    EMAFastAlpha = 0.0167    # 快速EMA的参数,60
    EMASlowAlpha = 0.0083  # 慢速EMA的参数,120
    fastEMA = 0        # 快速EMA的数值
    slowEMA = 0        # 慢速EMA的数值
    listfastEMA = []
    listslowEMA = []

    # K线缓存对象
    barOpen = 0
    barHigh = 0
    barLow = 0
    barClose = 0
    barTime = None
    barOpenInterest = 0
    num = 0

    # 保存K线数据的列表对象
    listBar = []
    listClose = []
    listHigh = []
    listLow = []
    listOpen = []
    listOpenInterest = []

    # 是否完成了历史数据的读取
    initCompleted = True
    # 初始化时读取的历史数据的起始日期(可以选择外部设置)
    startDate = None
    symbol = 'ag1706'

    class CandlestickItem(pg.GraphicsObject):
        def __init__(self, data):
            pg.GraphicsObject.__init__(self)
            self.data = data  ## data must have fields: time, open, close, min, max
            self.generatePicture()

        def generatePicture(self):
            ## pre-computing a QPicture object allows paint() to run much more quickly,
            ## rather than re-drawing the shapes every time.
            self.picture = QtGui.QPicture()
            p = QtGui.QPainter(self.picture)
            p.setPen(pg.mkPen(color='w', width=0.4))  # 0.4 means w*2
            # w = (self.data[1][0] - self.data[0][0]) / 3.
            w = 0.2
            for (t, open, close, min, max) in self.data:
                p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
                if open > close:
                    p.setBrush(pg.mkBrush('g'))
                else:
                    p.setBrush(pg.mkBrush('r'))
                p.drawRect(QtCore.QRectF(t-w, open, w*2, close-open))
            p.end()

        def paint(self, p, *args):
            p.drawPicture(0, 0, self.picture)

        def boundingRect(self):
            ## boundingRect _must_ indicate the entire area that will be drawn on
            ## or else we will get artifacts and possibly crashing.
            ## (in this case, QPicture does all the work of computing the bouning rect for us)
            return QtCore.QRectF(self.picture.boundingRect())

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, chanlunEngine, parent=None):
        """Constructor"""
        super(PriceWidget, self).__init__(parent)

        self.__eventEngine = eventEngine
        self.__mainEngine = chanlunEngine
        # MongoDB数据库相关
        self.__mongoConnected = False
        self.__mongoConnection = None
        self.__mongoTickDB = None

        # 调用函数
        self.__connectMongo()
        self.initUi(startDate=None)
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self, startDate=None):
        """初始化界面"""
        self.setWindowTitle(u'Price')

        self.vbl_1 = QtGui.QHBoxLayout()
        # self.vbl_1.setColumnStretch(1,1)
        # self.vbl_1.setRowStretch(1,1)
        # self.initplotTick()  # plotTick初始化

        # self.vbl_2 = QtGui.QVBoxLayout()
        self.initplotKline()  # plotKline初始化
        # self.initplotTendency()  # plot分时图的初始化

        # 整体布局
        # self.hbl = QtGui.QHBoxLayout()
        self.setLayout(self.vbl_1)
        # self.hbl.addLayout(self.vbl_2)
        # self.setLayout(self.hbl)

        self.initHistoricalData()  # 下载历史Tick数据并画图
        # self.plotMin()   #使用数据库中的分钟数据画K线

    #----------------------------------------------------------------------
    def initplotTick(self):
        """"""
        self.pw1 = pg.PlotWidget(name='Plot1')
        self.vbl_1.addWidget(self.pw1)
        self.pw1.setRange(xRange=[-360, 0])
        self.pw1.setLimits(xMax=5)
        self.pw1.setDownsampling(mode='peak')
        self.pw1.setClipToView(True)

        self.curve1 = self.pw1.plot()
        self.curve2 = self.pw1.plot()
        self.curve3 = self.pw1.plot()
        self.curve4 = self.pw1.plot()

    #----------------------------------------------------------------------
    def initplotKline(self):
        """Kline"""
        self.pw2 = pg.PlotWidget(name='Plot2')  # K线图
        self.vbl_1.addWidget(self.pw2)
        self.pw2.setMinimumWidth(1500)
        # self.vbl_1.setStretchFactor(self.pw2,-1)
        self.pw2.setDownsampling(mode='peak')
        self.pw2.setClipToView(True)

        self.curve5 = self.pw2.plot()
        self.curve6 = self.pw2.plot()

        self.candle = self.CandlestickItem(self.listBar)
        self.pw2.addItem(self.candle)
        ## Draw an arrowhead next to the text box
        # self.arrow = pg.ArrowItem()
        # self.pw2.addItem(self.arrow)

    #----------------------------------------------------------------------
    def initplotTendency(self):
        """"""
        self.pw3 = pg.PlotWidget(name='Plot3')
        self.vbl_2.addWidget(self.pw3)
        self.pw3.setDownsampling(mode='peak')
        self.pw3.setClipToView(True)
        self.pw3.setMaximumHeight(200)
        self.pw3.setXLink('Plot2')   # X linked with Plot2

        self.curve7 = self.pw3.plot()

    def plotMin(self):
        print "plotMinK start"
        self.initCompleted = True
        cx = self.__mongoMinDB[self.symbol].find()
        print cx.count()
        if cx:
            for data in cx:
                self.barOpen = data['open']
                self.barClose = data['close']
                self.barLow = data['low']
                self.barHigh = data['high']
                self.barOpenInterest = data['openInterest']
                # print self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest
                self.onBar(self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest)
                self.num += 1

        print "plotMinK success"


    #----------------------------------------------------------------------
    def initHistoricalData(self,startDate=None):
        """初始历史数据"""
        print "download histrical data"
        self.initCompleted = True  # 读取历史数据完成
        td = timedelta(days=1)     # 读取3天的历史TICK数据

        if startDate:
            cx = self.loadTick(self.symbol, startDate-td)
        else:
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            cx = self.loadTick(self.symbol, today-td)

        print cx.count()

        if cx:
            for data in cx:
                tick = Tick(data['symbol'])

                tick.openPrice = data['lastPrice']
                tick.highPrice = data['upperLimit']
                tick.lowPrice = data['lowerLimit']
                tick.lastPrice = data['lastPrice']

                tick.volume = data['volume']
                tick.openInterest = data['openInterest']

                tick.upperLimit = data['upperLimit']
                tick.lowerLimit = data['lowerLimit']

                tick.time = data['time']
                # tick.ms = data['UpdateMillisec']

                tick.bidPrice1 = data['bidPrice1']
                tick.bidPrice2 = data['bidPrice2']
                tick.bidPrice3 = data['bidPrice3']
                tick.bidPrice4 = data['bidPrice4']
                tick.bidPrice5 = data['bidPrice5']

                tick.askPrice1 = data['askPrice1']
                tick.askPrice2 = data['askPrice2']
                tick.askPrice3 = data['askPrice3']
                tick.askPrice4 = data['askPrice4']
                tick.askPrice5 = data['askPrice5']

                tick.bidVolume1 = data['bidVolume1']
                tick.bidVolume2 = data['bidVolume2']
                tick.bidVolume3 = data['bidVolume3']
                tick.bidVolume4 = data['bidVolume4']
                tick.bidVolume5 = data['bidVolume5']

                tick.askVolume1 = data['askVolume1']
                tick.askVolume2 = data['askVolume2']
                tick.askVolume3 = data['askVolume3']
                tick.askVolume4 = data['askVolume4']
                tick.askVolume5 = data['askVolume5']

                self.onTick(tick)

        print('load historic data completed')

    #----------------------------------------------------------------------
    # def plotTick(self):
    #     """画tick图"""
    #     if self.initCompleted:
    #         self.curve1.setData(self.listlastPrice[:self.ptr])
    #         self.curve2.setData(self.listfastMA[:self.ptr], pen=(255, 0, 0), name="Red curve")
    #         self.curve3.setData(self.listmidMA[:self.ptr], pen=(0, 255, 0), name="Green curve")
    #         self.curve4.setData(self.listslowMA[:self.ptr], pen=(0, 0, 255), name="Blue curve")
    #         self.curve1.setPos(-self.ptr, 0)
    #         self.curve2.setPos(-self.ptr, 0)
    #         self.curve3.setPos(-self.ptr, 0)
    #         self.curve4.setPos(-self.ptr, 0)

    #----------------------------------------------------------------------
    def plotKline(self):
        """K线图"""
        if self.initCompleted:
            # 均线
            self.curve5.setData(self.listfastEMA, pen=(255, 0, 0), name="Red curve")
            self.curve6.setData(self.listslowEMA, pen=(0, 255, 0), name="Green curve")

            # 画K线
            self.pw2.removeItem(self.candle)
            self.candle = self.CandlestickItem(self.listBar)
            self.pw2.addItem(self.candle)
            self.plotText()   # 显示开仓信号位置

    #----------------------------------------------------------------------
    def plotTendency(self):
        """持仓"""
        if self.initCompleted:
            self.curve7.setData(self.listOpenInterest, pen=(255, 255, 255), name="White curve")

    #----------------------------------------------------------------------
    def plotText(self):
        lenClose = len(self.listClose)

        if lenClose >= 5:                                       # Fractal Signal
            if self.listClose[-1] > self.listClose[-2] and self.listClose[-3] > self.listClose[-2] and self.listClose[-4] > self.listClose[-2] and self.listClose[-5] > self.listClose[-2] and self.listfastEMA[-1] > self.listslowEMA[-1]:
                ## Draw an arrowhead next to the text box
                # self.pw2.removeItem(self.arrow)
                self.arrow = pg.ArrowItem(pos=(lenClose-1, self.listLow[-1]), angle=90, brush=(255, 0, 0))#红色
                self.pw2.addItem(self.arrow)
            elif self.listClose[-1] < self.listClose[-2] and self.listClose[-3] < self.listClose[-2] and self.listClose[-4] < self.listClose[-2] and self.listClose[-5] < self.listClose[-2] and self.listfastEMA[-1] < self.listslowEMA[-1]:
                ## Draw an arrowhead next to the text box
                # self.pw2.removeItem(self.arrow)
                self.arrow = pg.ArrowItem(pos=(lenClose-1, self.listHigh[-1]), angle=-90, brush=(0, 255, 0))#绿色
                self.pw2.addItem(self.arrow)

    #----------------------------------------------------------------------
    def updateMarketData(self, event):
        """更新行情"""
        print "update"
        data = event.dict_['data']
        print data
        symbol = data['InstrumentID']
        tick = Tick(symbol)
        tick.openPrice = data['OpenPrice']
        tick.highPrice = data['HighestPrice']
        tick.lowPrice = data['LowestPrice']
        tick.lastPrice = data['LastPrice']

        tick.volume = data['Volume']
        tick.openInterest = data['OpenInterest']

        tick.upperLimit = data['UpperLimitPrice']
        tick.lowerLimit = data['LowerLimitPrice']

        tick.time = data['UpdateTime']
        tick.ms = data['UpdateMillisec']

        tick.bidPrice1 = data['BidPrice1']
        tick.bidPrice2 = data['BidPrice2']
        tick.bidPrice3 = data['BidPrice3']
        tick.bidPrice4 = data['BidPrice4']
        tick.bidPrice5 = data['BidPrice5']

        tick.askPrice1 = data['AskPrice1']
        tick.askPrice2 = data['AskPrice2']
        tick.askPrice3 = data['AskPrice3']
        tick.askPrice4 = data['AskPrice4']
        tick.askPrice5 = data['AskPrice5']

        tick.bidVolume1 = data['BidVolume1']
        tick.bidVolume2 = data['BidVolume2']
        tick.bidVolume3 = data['BidVolume3']
        tick.bidVolume4 = data['BidVolume4']
        tick.bidVolume5 = data['BidVolume5']

        tick.askVolume1 = data['AskVolume1']
        tick.askVolume2 = data['AskVolume2']
        tick.askVolume3 = data['AskVolume3']
        tick.askVolume4 = data['AskVolume4']
        tick.askVolume5 = data['AskVolume5']

        self.onTick(tick)  # tick数据更新

        # # 将数据插入MongoDB数据库，实盘建议另开程序记录TICK数据
        # self.__recordTick(data)

    #----------------------------------------------------------------------
    def onTick(self, tick):
        """tick数据更新"""
        from datetime import time

        # 首先生成datetime.time格式的时间（便于比较）,从字符串时间转化为time格式的时间
        hh, mm, ss = tick.time.split(':')
        if(len(ss) > 2):
            ss1, ss2 = ss.split('.')
            self.ticktime = time(int(hh), int(mm), int(ss1), microsecond=int(ss2)*100)
        else:
            self.ticktime = time(int(hh), int(mm), int(ss), microsecond=tick.ms)

        # 计算tick图的相关参数
        if self.ptr == 0:
            self.fastMA = tick.lastPrice
            self.midMA = tick.lastPrice
            self.slowMA = tick.lastPrice
        else:
            self.fastMA = (1-self.tickFastAlpha) * self.fastMA + self.tickFastAlpha * tick.lastPrice
            self.midMA = (1-self.tickMidAlpha) * self.midMA + self.tickMidAlpha * tick.lastPrice
            self.slowMA = (1-self.tickSlowAlpha) * self.slowMA + self.tickSlowAlpha * tick.lastPrice
        self.listlastPrice[self.ptr] = tick.lastPrice
        self.listfastMA[self.ptr] = self.fastMA
        self.listmidMA[self.ptr] = self.midMA
        self.listslowMA[self.ptr] = self.slowMA

        self.ptr += 1
        print("----------")
        print(self.ptr)
        if self.ptr >= self.listlastPrice.shape[0]:
            tmp = self.listlastPrice
            self.listlastPrice = np.empty(self.listlastPrice.shape[0] * 2)
            self.listlastPrice[:tmp.shape[0]] = tmp

            tmp = self.listfastMA
            self.listfastMA = np.empty(self.listfastMA.shape[0] * 2)
            self.listfastMA[:tmp.shape[0]] = tmp

            tmp = self.listmidMA
            self.listmidMA = np.empty(self.listmidMA.shape[0] * 2)
            self.listmidMA[:tmp.shape[0]] = tmp

            tmp = self.listslowMA
            self.listslowMA = np.empty(self.listslowMA.shape[0] * 2)
            self.listslowMA[:tmp.shape[0]] = tmp

        # K线数据
        # 假设是收到的第一个TICK
        if self.barOpen == 0:
            # 初始化新的K线数据
            self.barOpen = tick.lastPrice
            self.barHigh = tick.lastPrice
            self.barLow = tick.lastPrice
            self.barClose = tick.lastPrice
            self.barTime = self.ticktime
            self.barOpenInterest = tick.openInterest
            self.onBar(self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest)
        else:
            # 如果是当前一分钟内的数据
            if self.ticktime.minute == self.barTime.minute:
                if self.ticktime.second >= 30 and self.barTime.second < 30: # 判断30秒周期K线
                    # 先保存K线收盘价
                    self.num += 1
                    self.onBar(self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest)
                    # 初始化新的K线数据
                    self.barOpen = tick.lastPrice
                    self.barHigh = tick.lastPrice
                    self.barLow = tick.lastPrice
                    self.barClose = tick.lastPrice
                    self.barTime = self.ticktime
                    self.barOpenInterest = tick.openInterest
                # 汇总TICK生成K线
                self.barHigh = max(self.barHigh, tick.lastPrice)
                self.barLow = min(self.barLow, tick.lastPrice)
                self.barClose = tick.lastPrice
                self.barTime = self.ticktime
                self.listBar.pop()
                self.listfastEMA.pop()
                self.listslowEMA.pop()
                self.listOpen.pop()
                self.listClose.pop()
                self.listHigh.pop()
                self.listLow.pop()
                self.listOpenInterest.pop()
                self.onBar(self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest)
            # 如果是新一分钟的数据
            else:
                # 先保存K线收盘价
                self.num += 1
                self.onBar(self.num, self.barOpen, self.barClose, self.barLow, self.barHigh, self.barOpenInterest)
                # 初始化新的K线数据
                self.barOpen = tick.lastPrice
                self.barHigh = tick.lastPrice
                self.barLow = tick.lastPrice
                self.barClose = tick.lastPrice
                self.barTime = self.ticktime
                self.barOpenInterest = tick.openInterest

    #----------------------------------------------------------------------
    def onBar(self, n, o, c, l, h, oi):
        self.listBar.append((n, o, c, l, h))
        self.listOpen.append(o)
        self.listClose.append(c)
        self.listHigh.append(h)
        self.listLow.append(l)
        self.listOpenInterest.append(oi)

        #计算K线图EMA均线
        if self.fastEMA:
            self.fastEMA = c*self.EMAFastAlpha + self.fastEMA*(1-self.EMAFastAlpha)
            self.slowEMA = c*self.EMASlowAlpha + self.slowEMA*(1-self.EMASlowAlpha)
        else:
            self.fastEMA = c
            self.slowEMA = c
        self.listfastEMA.append(self.fastEMA)
        self.listslowEMA.append(self.slowEMA)

        # 调用画图函数
        # self.plotTick()      # tick图
        self.plotKline()     # K线图
        # self.plotTendency()  # K线副图，持仓量

    #----------------------------------------------------------------------
    def __connectMongo(self):
        """连接MongoDB数据库"""
        try:
            self.__mongoConnection = pymongo.MongoClient("localhost", 27017)
            self.__mongoConnected = True
            self.__mongoTickDB = self.__mongoConnection['VnTrader_Tick_Db']
            self.__mongoMinDB = self.__mongoConnection['VnTrader_1Min_Db']
        except ConnectionFailure:
            pass

    #----------------------------------------------------------------------
    def __recordTick(self, data):
        """将Tick数据插入到MongoDB中"""
        if self.__mongoConnected:
            symbol = data['InstrumentID']
            data['date'] = self.today
            self.__mongoTickDB[symbol].insert(data)

    #----------------------------------------------------------------------
    def loadTick(self, symbol, startDate, endDate=None):
        """从MongoDB中读取Tick数据"""
        cx = self.__mongoTickDB[symbol].find()
        print cx.count()
        return cx
        # if self.__mongoConnected:
        #     collection = self.__mongoTickDB[symbol]
        #
        #     # 如果输入了读取TICK的最后日期
        #     if endDate:
        #         cx = collection.find({'date': {'$gte': startDate, '$lte': endDate}})
        #     else:
        #         cx = collection.find({'date': {'$gte': startDate}})
        #     return cx
        # else:
        #     return None

    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        print "connect"
        # self.__mainEngine.putMarketEvent()
        self.signal.connect(self.updateMarketData)
        self.__eventEngine.register(EVENT_MARKETDATA, self.signal.emit)

class Tick:
    """Tick数据对象"""

    #----------------------------------------------------------------------
    def __init__(self, symbol):
        """Constructor"""
        self.symbol = symbol        # 合约代码

        self.openPrice = 0          # OHLC
        self.highPrice = 0
        self.lowPrice = 0
        self.lastPrice = 0

        self.volume = 0             # 成交量
        self.openInterest = 0       # 持仓量

        self.upperLimit = 0         # 涨停价
        self.lowerLimit = 0         # 跌停价

        self.time = ''              # 更新时间和毫秒
        self.ms = 0

        self.bidPrice1 = 0          # 深度行情
        self.bidPrice2 = 0
        self.bidPrice3 = 0
        self.bidPrice4 = 0
        self.bidPrice5 = 0

        self.askPrice1 = 0
        self.askPrice2 = 0
        self.askPrice3 = 0
        self.askPrice4 = 0
        self.askPrice5 = 0

        self.bidVolume1 = 0
        self.bidVolume2 = 0
        self.bidVolume3 = 0
        self.bidVolume4 = 0
        self.bidVolume5 = 0

        self.askVolume1 = 0
        self.askVolume2 = 0
        self.askVolume3 = 0
        self.askVolume4 = 0
        self.askVolume5 = 0











