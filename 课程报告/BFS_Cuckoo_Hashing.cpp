#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <queue>
#include <ctime>
#include <cstdlib>
#include <fstream>
using namespace std;

const int TABLE_LEN = 100000;
const int MAX_DEPTH = 500;

string table1[TABLE_LEN];
string table2[TABLE_LEN];


int hash1(const string& s) {
    unsigned long h = 5381;
    for (char c : s) h = ((h << 5) + h) + c;
    return h % TABLE_LEN;
}
int hash2(const string& s) {
    unsigned long h = 1315423911;
    for (char c : s) h ^= ((h << 5) + c + (h >> 2));
    return h % TABLE_LEN;
}

vector<string> read_data_from_file(const string& filename) {
    vector<string> data;
    ifstream infile(filename);
    if (!infile.is_open()) {
        cerr << "无法打开文件: " << filename << endl;
        return data;
    }
    string line;
    while (getline(infile, line)) {
        if (!line.empty()) data.push_back(line);
    }
    infile.close();
    return data;
}

struct Node {
    int table_id; // 1 or 2
    int index;
    vector<Node> path;
};

bool BFS_find_path(const string& x, vector<Node>& final_path) {
    queue<Node> q;
    vector<vector<bool>> visited(2, vector<bool>(TABLE_LEN, false));
    int start1 = hash1(x), start2 = hash2(x);
    q.push({ 1, start1, {} });
    q.push({ 2, start2, {} });
    visited[0][start1] = true;
    visited[1][start2] = true;

    while (!q.empty()) {
        Node cur = q.front(); q.pop();
        if ((cur.table_id == 1 && table1[cur.index].empty()) ||
            (cur.table_id == 2 && table2[cur.index].empty())) {
            final_path = cur.path;
            final_path.push_back(cur);
            return true;
        }

        string occupant = (cur.table_id == 1 ? table1[cur.index] : table2[cur.index]);
        int next_table = (cur.table_id == 1 ? 2 : 1);
        int next_index = (next_table == 1 ? hash1(occupant) : hash2(occupant));

        if (!visited[next_table - 1][next_index] && cur.path.size() < MAX_DEPTH) {
            Node next = { next_table, next_index, cur.path };
            next.path.push_back(cur);
            q.push(next);
            visited[next_table - 1][next_index] = true;
        }
    }
    return false;
}


void relocate_along_path(const vector<Node>& path) {
    for (int i = path.size() - 1; i > 0; i--) {
        Node from = path[i - 1];
        Node to = path[i];
        string& src = (from.table_id == 1 ? table1[from.index] : table2[from.index]);
        string& dst = (to.table_id == 1 ? table1[to.index] : table2[to.index]);
        dst = src;
        src.clear();
    }
}


bool insert_element(const string& x) {
    int i1 = hash1(x), i2 = hash2(x);
    if (table1[i1].empty()) { table1[i1] = x; return true; }
    if (table2[i2].empty()) { table2[i2] = x; return true; }

    vector<Node> path;
    if (BFS_find_path(x, path)) {
        relocate_along_path(path);
        table1[i1] = x;
        return true;
    }
    return false;
}

void test_dataset(const vector<string>& data, string label) {
    cout << "\n===== 测试数据类型: " << label << " =====" << endl;
    vector<double> load_factors = { 0.05,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7 ,0.75, 0.8,0.85 ,0.9,0.95,1.00 };

    for (double lf : load_factors) {
        fill(begin(table1), end(table1), "");
        fill(begin(table2), end(table2), "");
        int insert_count = min(int(data.size()), int(TABLE_LEN * lf));
        int success = 0, fail = 0;

        clock_t start = clock();
        for (int i = 0; i < insert_count; i++) {
            if (insert_element(data[i])) success++;
            else fail++;
        }
        clock_t end = clock();
        double time = double(end - start) / CLOCKS_PER_SEC * 1000; // ms

        cout << "负载率: " << lf
            << " | 成功: " << success
            << " | 失败: " << fail
            << " | 成功率: " << (double)success / insert_count * 100 << "%"
            << " | 时间: " << time << " ms" << endl;
    }
}


int main() {
    srand(time(0));

    vector<string> int_data = read_data_from_file("C:\\Users\\Vampire\\Desktop\\bigdataStorage\\test_data\\int_data.txt");
    vector<string> str_data = read_data_from_file("C:\\Users\\Vampire\\Desktop\\bigdataStorage\\test_data\\string_data.txt");

    if (!int_data.empty()) test_dataset(int_data, "整数数据集");
    if (!str_data.empty()) test_dataset(str_data, "字符串数据集");

    return 0;
}
