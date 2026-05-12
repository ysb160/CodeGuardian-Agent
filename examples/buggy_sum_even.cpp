#include <vector>
using namespace std;

int sumEven(vector<int> nums) {
    int sum;
    for (int i = 0; i <= nums.size(); i++) {
        if (nums[i] % 2 = 0) {
            sum += nums[i];
        }
    }
    return sum;
}
