## LLDB Formatters for C++

This repository contains a collection of LLDB formatters for C++ types. The formatters are written in Python and can be used to improve the debugging experience of C++ code in LLDB. The supported types are the ones I use frequently, please feel free to contribute by adding more formatters. 

Heavily insiped from [dprogm/boost-lldb-formatter](https://github.com/dprogm/boost-lldb-formatter) and [tehrengruber/LLDB-Eigen-Data-Formatter](https://github.com/tehrengruber/LLDB-Eigen-Data-Formatter).

#### Supported Types
```c++
// Boost
boost::container::small_vector
boost::optional
boost::variant

// Eigen
Eigen::Matrix
Eigen::Array
```

#### Installation
```bash

```

#### Example Usage

##### `Eigen::Matrix`
```c++

```

##### `boost::container::small_vector`
```c++

```