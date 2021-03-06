import socket
import sys
import time
import datetime
import copy
  
sock = None
def once_run(*commands):
  global sock
  HOST, PORT = "codebb.cloudapp.net", 17429
  
  data=OUR_USERNAME + " " + OUR_PASSWORD + "\n" + "\n".join(commands) + "\nCLOSE_CONNECTION\n"
  return_lines = []

  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print socket.gettimeout()
    sock.settimeout(3)

    sock.connect((HOST, PORT))
    sock.sendall(data)
    sfile = sock.makefile()
    rline = sfile.readline()
    while rline:
      #print(rline.strip())
      return_lines.append(rline.strip())
      rline = sfile.readline()
  finally:
    sock.close()

  return return_lines

def run(commands):
  while True:
    try:
      data = once_run(commands)
      return data
    except KeyboardInterrupt:
      raise
    except:
      print "Warning: network failed"

def subscribe():
  HOST, PORT = "codebb.cloudapp.net", 17429
  
  data=OUR_USERNAME + " " + OUR_PASSWORD + "\nSUBSCRIBE\n"

  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((HOST, PORT))
    sock.sendall(data)
    sfile = sock.makefile()
    rline = sfile.readline()
    while rline:
      print(rline.strip())
      rline = sfile.readline()
  finally:
    sock.close()


OUR_USERNAME = "Team4"
OUR_PASSWORD = "1234a"

securities = {}
orders = {}
my_cash = 0
my_securities = {}
my_orders = {}


# Query all the securities
def get_securities():
  inp = run("SECURITIES")[0].split()[1:]
  for i in range(len(inp)/4):
    securities[inp[4*i]] = (float(inp[4*i+1]), float(inp[4*i+2]), float(inp[4*i+3]))

def get_cash():
  global my_cash
  my_cash = float(run("MY_CASH")[0].split()[1])

def get_my_securities():
  global my_securities
  my_securities = {}
  inp = run("MY_SECURITIES")[0].split()[1:]
  for i in range(len(inp)/3):
    my_securities[inp[3*i]] = (int(inp[3*i+1]), float(inp[3*i+2]))

def get_my_orders():
  global my_orders
  my_orders = {}
  inp = run("MY_ORDERS")[0].split()[1:]
  for i in range(len(inp)/4):
    my_orders[inp[4*i+1]] = (inp[4*i], float(inp[4*i+2]), float(inp[4*i+3]))

def get_orders(stock):
  inp = run("ORDERS " + stock)[0].split()[1:]
  out = []
  for i in range(len(inp)/4):
    out.append( (inp[4*i], inp[4*i+1], float(inp[4*i+2]), int(inp[4*i+3])) )
  orders[stock] = out


# Max buy and min sell prices
def get_buy_and_sell_prices(order):
  cur_buy = 0
  cur_sell = 1000
  for bid_ask, name, price, nshare in order:
    if bid_ask == "BID":
      if price > cur_buy:                                                                                                                                  
        cur_buy = price
    if bid_ask == "ASK":
      if price < cur_sell:
        cur_sell = price
  return (cur_buy, cur_sell)


def how_many_can_buy(order, money):
  sell_list = []
  for bid_ask, name, price, nshare in order:
    if bid_ask == "ASK":
      sell_list = sell_list + nshare * [price]
  sell_list = sorted(sell_list)
  count = 0
  for s in sell_list:
    if money < 0:
      break
    money -= s
    count += 1
  return count


def get_100th_buy_and_sell(order):
  cur_buy = 0
  cur_sell = 1000
  buy_list = []
  sell_list = []
  for bid_ask, name, price, nshare in order:
    if bid_ask == "BID":
      buy_list = buy_list + nshare * [price]
    if bid_ask == "ASK":
      sell_list = sell_list + nshare * [price]
  buy_list = sorted(buy_list)
  sell_list = sorted(sell_list)

  # Get 100th from both sides, if less than 100 then it's bad
  if len(buy_list) < 105 or len(sell_list) < 105:
    return (0,1000)

  return buy_list[-100], sell_list[100]


# assumes that get_orders was just called on everything
def sum_orders(stock):
  s = 0
  for _,_,_,n in orders[stock]:
    s += n
  return s



def buy_stock(stock):

  while True:
    get_cash()
    get_orders(stock)
    this_ord = orders[stock]

    cur_buy, cur_sell = get_buy_and_sell_prices(this_ord)

    # assume we can buy at cur_sell
    buying_price = cur_sell + 0.1
    num_shares = int(my_cash / buying_price)

    if num_shares < 2:
      break

    print "Buying %s: %d shares at %f" % (stock, num_shares, buying_price)
    run("BID %s %f %d" % (stock, buying_price, num_shares))


def sell_stock(stock):

  time_sold[stock] = datetime.datetime.now()
  while True:
    get_my_securities()
    get_orders(stock)
    this_ord = orders[stock]

    cur_buy, cur_sell = get_buy_and_sell_prices(this_ord)

    # assume we can sell at cur_buy
    selling_price = cur_buy - 0.1
    num_shares = int(my_securities[stock][0])

    if num_shares == 0:
      break

    print "Selling %s: %d shares at %f" % (stock, num_shares, selling_price)
    run("ASK %s %f %d"% (stock, selling_price, num_shares))



def smart_sell_1_iter(stock):
  get_my_securities()
  get_orders(stock)
  this_ord = orders[stock]

  _, cur_sell = get_buy_and_sell_prices(this_ord)
  want_price = cur_sell - 0.06

  num_shares = int(my_securities[stock][0])
  run("ASK %s %f %d"% (stock, want_price, num_shares))


def smart_sell(stock):

  while True:
    smart_sell_1_iter(stock)
    time.sleep(3)


def slow_sell_1_iter(stock):
  get_my_securities()
  get_orders(stock)
  this_ord = orders[stock]

  _, cur_sell = get_buy_and_sell_prices(this_ord)
  want_price = cur_sell - 0.01

  num_shares = int(my_securities[stock][0])
  print "Selling %s: %d shares at %f" % (stock, num_shares, want_price)
  run("ASK %s %f %d"% (stock, want_price, num_shares))



def estimate_price(stock):
  cur_buy, cur_sell = get_buy_and_sell_prices(orders[stock])
  return (cur_buy + cur_sell) / 2



def pick_stock():
  get_securities()
  get_cash()
  for ticker,_ in securities.iteritems():
    print "fetching orders", ticker
    get_orders(ticker)

  magic_nums = []
  for ticker,_ in securities.iteritems():
    E = securities[ticker][0]
    N = how_many_can_buy(orders[ticker], my_cash)
    D = securities[ticker][1]
    M = sum_orders(ticker)
    magic_andrei_number = (E*N*D+0.0) / (M+0.0)
    magic_nums.append((magic_andrei_number, ticker ))

  magic_nums = sorted(magic_nums)
  magic_nums.reverse()
  # cannot buy until 4 minutes after selling it
  for v,ticker in magic_nums:
    bad = False
    if ticker in time_sold and datetime.datetime.now() - time_sold[ticker] < datetime.timedelta(minutes=4):
      # if we just sold this less than 4 minutes ago
      bad = True
    if ticker in my_securities and my_securities[ticker][0] > 0:
      # if we already have this stock
      bad = True
    if not bad:
      return ticker


time_bought = {}
time_sold = {}
def autorun():
  while True:
    get_cash()
    get_my_securities()
    get_my_orders()
    print "MY CASH:", my_cash

    num_owned = 0
    for sec, vl in my_securities.iteritems():
      if vl[0] > 0:
        num_owned += 1

    print num_owned
    #If we don't have any stocks, buy some
    if my_cash > 0:
      stock = pick_stock()
      if stock:
        buy_stock(stock)
        time_bought[stock] = datetime.datetime.now()

    # If we hold a stock for more than 1 minutes, start smart selling
    for sec, vl in my_securities.iteritems():
      we_hold = vl[0]
      if we_hold > 0:
        if datetime.datetime.now() - time_bought[sec] > datetime.timedelta(seconds=90):
          smart_sell_1_iter(ticker)

          # If we managed to sell something completely, update it
          time_sold[ticker] = datetime.datetime.now()

    time.sleep(2)



def alternate_plan():
  while True:
    get_cash()
    get_securities()

    cash_each = my_cash / len(securities)

    for sec,vs in securities.iteritems():
      get_orders(sec)
      cur_buy, cur_sell = get_buy_and_sell_prices(orders[sec])
      want_price = cur_sell + 0.1
      num_shares = int(cash_each / want_price)
      run("BID %s %f %d"% (sec, want_price, num_shares))

    while True:
      get_cash()
      get_my_securities()
      if len(sec) == 0:
        break
      for sec, vl in my_securities.iteritems():
        we_hold = vl[0]
        if we_hold > 0:
          slow_sell_1_iter(sec)
      time.sleep(10)

  


autorun()
