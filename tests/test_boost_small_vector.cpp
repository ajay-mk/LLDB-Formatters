#include <boost/container/small_vector.hpp>
#include <iostream>

int main() {
    boost::container::small_vector<int, 4> vec;
    vec.push_back(10);
    vec.push_back(20);
    vec.push_back(30);
    std::cout << "pause" << std::endl; // For breakpoint
    return 0;
}