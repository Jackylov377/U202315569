#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <queue>
#include <ctime>
#include <cstdlib>
#include <fstream>   
using namespace std;

const int TABLE_LEN = 100000;    // 哈希表长度
const int MAX_KICK = 500;        // 最大踢出次数

string table1[TABLE_LEN];
string table2[TABLE_LEN];

int hash1(const string& s) {
    unsigned long h = 5381;
    for (unsigned char c : s)
        h = ((h << 5) + h) + c;
    return int(h % TABLE_LEN);
}
int hash2(const string& s) {
    unsigned long h = 1315423911;
    for (unsigned char c : s)
        h ^= ((h << 5) + (unsigned long)c + (h >> 2));
    return int(h % TABLE_LEN);
}

vector<string> load_data(const string& filename, int limit = -1) {
    vector<string> data;
    ifstream fin(filename);
    if (!fin.is_open()) {
        cerr << "无法打开文件: " << filename << endl;
        exit(1);
    }

    string s;
    while (fin >> s) {
        data.push_back(s);
        if (limit > 0 && (int)data.size() >= limit)
            break;
    }

    fin.close();
    return data;
}
bool insert_element(const string& x) {
    string cur = x;
    int pos = hash1(cur);

    for (int kick = 0; kick < MAX_KICK; kick++) {
        if (pos < 0 || pos >= TABLE_LEN) return false; // 防越界
        if (table1[pos].empty()) {
            table1[pos] = cur;
            return true;
        }
        swap(cur, table1[pos]);  // 踢出

        pos = hash2(cur);
        if (pos < 0 || pos >= TABLE_LEN) return false; // 防越界
        if (table2[pos].empty()) {
            table2[pos] = cur;
            return true;
        }
        swap(cur, table2[pos]);  // 再踢出

        pos = hash1(cur);
    }
    return false;  // 超过最大踢出次数
}

void test_dataset(const vector<string>& data, const string& label) {
    cout << "\n===== 测试数据类型: " << label << " =====" << endl;

    vector<double> load_factors = { 0.05,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,
                                   0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1.00 };

    for (double lf : load_factors) {
        fill(begin(table1), end(table1), "");
        fill(begin(table2), end(table2), "");

        int insert_count = (int)(TABLE_LEN * lf);
        int success = 0, fail = 0;

        if (insert_count > (int)data.size()) {
            cerr << "数据不足以支撑负载率 " << lf << "，已跳过" << endl;
            continue;
        }

        clock_t start = clock();
        for (int i = 0; i < insert_count; i++) {
            if (insert_element(data[i])) success++;
            else fail++;
        }
        clock_t end = clock();

        double time_ms = double(end - start) / CLOCKS_PER_SEC * 1000; // ms
        double success_rate = 100.0 * success / insert_count;

        cout << "负载率: " << lf
            << " | 成功: " << success
            << " | 失败: " << fail
            << " | 成功率: " << success_rate << "%"
            << " | 时间: " << time_ms << " ms" << endl;
    }
}

int main() {
    srand((unsigned)time(0));

    vector<string> int_data = load_data("C:\\Users\\Vampire\\Desktop\\bigdataStorage\\test_data\\int_data.txt");
    vector<string> str_data = load_data("C:\\Users\\Vampire\\Desktop\\bigdataStorage\\test_data\\string_data.txt");

    test_dataset(int_data, "随机整数数据集");
    test_dataset(str_data, "随机字符串数据集");

    return 0;
}
