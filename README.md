## LLDB Formatters for C++

This repository contains a collection of LLDB formatters for C++ types. The formatters are written in Python and can be used to improve the debugging experience of C++ code in LLDB. The supported types are the ones I encounter frequently, please feel free to contribute by adding more formatters. 

Inspired from [dprogm/boost-lldb-formatter](https://github.com/dprogm/boost-lldb-formatter) and [tehrengruber/LLDB-Eigen-Data-Formatter](https://github.com/tehrengruber/LLDB-Eigen-Data-Formatter).

#### Supported Types
```c++
// Boost
boost::container::small_vector

// Eigen
Eigen::Matrix
Eigen::Array
Eigen::MatrixXd, Eigen::MatrixXf, Eigen::MatrixXi
Eigen::VectorXd, Eigen::VectorXf, Eigen::VectorXi
Eigen::ArrayXd, Eigen::ArrayXf, Eigen::ArrayXi
```

#### Example Usage
- Clone the repository to your local machine:
```sh
git clone https://github.com/ajay-mk/LLDB-Formatters.git
```
- Open `~/.lldbinit` in your home directory and add the following line (or any of the formatters you want to use):
```sh
command script import /path/to/LLDB-Formatters/boost_formatter.py
command script import /path/to/LLDB-Formatters/eigen_formatter.py
```

#### Example with Boost Objects
When debugging C++ code with Boost container objects, the formatter will display elements with proper indexing:

```cpp
#include <boost/container/small_vector.hpp>

int main() {
    boost::container::small_vector<int, 4> vec;
    vec.push_back(10);
    vec.push_back(20);
    vec.push_back(30);
    
    // Set breakpoint here
    return 0;
}
```

In LLDB, you'll see:
```
(lldb) p vec
(boost::container::small_vector<int, 4>) vec = {
  [0] = 10
  [1] = 20
  [2] = 30
}
```

#### Example with Eigen Objects
When debugging C++ code with Eigen objects, the formatter will display matrix and array elements with `[row,col]` indexing:

```cpp
#include <Eigen/Dense>

int main() {
    Eigen::MatrixXd matrix(2, 3);
    matrix << 1.0, 2.0, 3.0,
              4.0, 5.0, 6.0;
              
    Eigen::VectorXd vector(3);
    vector << 10.0, 20.0, 30.0;
    
    // Set breakpoint here
    return 0;
}
```

In LLDB, you'll see:
```
(lldb) p matrix
(Eigen::MatrixXd) matrix = {
  [0,0] = 1
  [1,0] = 4
  [0,1] = 2
  [1,1] = 5
  [0,2] = 3
  [1,2] = 6
}

(lldb) p vector
(Eigen::VectorXd) vector = {
  [0,0] = 10
  [1,0] = 20
  [2,0] = 30
}
```