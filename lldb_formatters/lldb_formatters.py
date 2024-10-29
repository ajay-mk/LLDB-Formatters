import lldb
from utils import *
from boost_formatter import *

def __lldb_init_module(debugger, dict):
    debugger.HandleCommand('type synthetic add add -l boost_formatter.BoostSmallVectorSynthProvider -x "^boost::container::small_vector<.+>$"')
    debugger.HandleCommand('type summary add -F utils.SizeSummaryProvider -e -x "boost::container::small_vector<.+>$"')