## LLDB Formatters for C++

This repository contains a collection of LLDB formatters for C++ types. The formatters are written in Python and can be used to improve the debugging experience of C++ code in LLDB. The supported types are the ones I encounter frequently, please feel free to contribute by adding more formatters. 

Inspired from [dprogm/boost-lldb-formatter](https://github.com/dprogm/boost-lldb-formatter) and [tehrengruber/LLDB-Eigen-Data-Formatter](https://github.com/tehrengruber/LLDB-Eigen-Data-Formatter).

#### Supported Types
```c++
// Boost
boost::container::small_vector

// Eigen (under development)
Eigen::Matrix
Eigen::Array
```

#### Example Usage
- Clone the repository to your local machine:
```sh
git clone https://github.com/ajay-mk/LLDB-Formatters.git
```
- Open `~/.lldbinit` in your home directory and add the following line (or any of the formatters you want to use):
```sh
command script import /path/to/LLDB-Formatters/boost_formatter.py
```