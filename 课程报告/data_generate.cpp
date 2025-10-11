#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>
using namespace std;

const int INT_DATA_SIZE = 1000000;   // 随机整数数量
const int STR_DATA_SIZE = 100000;    // 随机字符串数量
const int STR_LEN = 5000;            // 每个字符串长度
const string OUTPUT_DIR = "test_data"; // 输出目录
vector<string> generate_int_data(int n) {
    vector<string> data;
    data.reserve(n);
    for (int i = 0; i < n; i++) {
        int num = rand() % 1000000;
        data.push_back(to_string(num));
    }
    return data;
}

string random_string(int len) {
    static const string chars = "abcdefghijklmnopqrstuvwxyz";
    string s;
    s.reserve(len);
    for (int i = 0; i < len; i++)
        s += chars[rand() % chars.size()];
    return s;
}

vector<string> generate_string_data(int n, int len) {
    vector<string> data;
    data.reserve(n);
    for (int i = 0; i < n; i++)
        data.push_back(random_string(len));
    return data;
}

int main() {
    srand(12345);  // 固定随机种子，确保可复现
    system(("mkdir " + OUTPUT_DIR).c_str());  // 创建文件夹（Windows可用）

    cout << "开始生成数据集..." << endl;

    // 1️⃣ 生成随机整数数据集
    cout << "生成随机整数数据集，共 " << INT_DATA_SIZE << " 条" << endl;
    vector<string> int_data = generate_int_data(INT_DATA_SIZE);
    ofstream fout1(OUTPUT_DIR + "/int_data.txt");
    for (const string& s : int_data)
        fout1 << s << "\n";
    fout1.close();

    // 2️⃣ 生成随机字符串数据集
    cout << "生成随机字符串数据集，共 " << STR_DATA_SIZE << " 条，每条长度 " << STR_LEN << " ..." << endl;
    vector<string> str_data = generate_string_data(STR_DATA_SIZE, STR_LEN);
    ofstream fout2(OUTPUT_DIR + "/string_data.txt");
    for (const string& s : str_data)
        fout2 << s << "\n";
    fout2.close();
    cout << " 字符串数据集已写入 " << OUTPUT_DIR + "/string_data.txt" << endl;
    return 0;
}
