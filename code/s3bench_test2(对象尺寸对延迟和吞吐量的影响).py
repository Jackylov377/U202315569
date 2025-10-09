import os
import re
import matplotlib.pyplot as plt
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

result_dir = "C:/Users/Vampire/s3bench_result2"

object_sizes = []
avg_latencies = []
throughputs = []

# 遍历结果文件
for file in os.listdir(result_dir):
    if file.startswith("result_size_") and file.endswith(".txt"):
        size = int(re.search(r"result_size_(\d+).txt", file).group(1))
        object_sizes.append(size)

        with open(os.path.join(result_dir, file), "r", encoding="utf-8") as f:
            text = f.read()

        # 匹配 Write 的平均延迟
        latency_match = re.search(r"Total Duration:\s*([\d\.]+) s", text)
        errors_match = re.search(r"Number of Errors:\s*(\d+)", text)
        transferred_match = re.search(r"Total Transferred:\s*([\d\.]+) MB", text)

        if latency_match and errors_match and transferred_match:
            total_duration = float(latency_match.group(1))
            errors = int(errors_match.group(1))
            transferred = float(transferred_match.group(1))

            # 平均延迟 = 总时间 / 成功请求数
            num_samples_match = re.search(r"numSamples\s*=\s*(\d+)", text)
            num_samples = 500 if not num_samples_match else int(num_samples_match.group(1))
            success_count = num_samples - errors
            avg_latency = total_duration / success_count * 1000 if success_count > 0 else np.nan  # ms
            avg_latencies.append(avg_latency)

            # 吞吐量 = Total Transferred / 总时间
            throughput = transferred / total_duration if total_duration > 0 else np.nan
            throughputs.append(throughput)
        else:
            avg_latencies.append(np.nan)
            throughputs.append(np.nan)

# 按对象大小排序
sorted_data = sorted(zip(object_sizes, avg_latencies, throughputs))
sizes, avg_latencies, throughputs = zip(*sorted_data)

# 绘制延迟曲线
plt.figure(figsize=(8, 5))
plt.plot(sizes, avg_latencies, marker='o', label="平均延迟 (ms)")
plt.xscale('log')
plt.xlabel("对象大小 (Bytes)")
plt.ylabel("平均延迟 (ms)")
plt.title("对象大小 vs 平均延迟")
plt.grid(True)
plt.legend()
plt.savefig("latency_vs_object_size.png")
plt.show()

# 绘制吞吐量曲线
plt.figure(figsize=(8, 5))
plt.plot(sizes, throughputs, marker='o', color='orange', label="吞吐量 (MB/s)")
plt.xscale('log')
plt.xlabel("对象大小 (Bytes)")
plt.ylabel("吞吐量 (MB/s)")
plt.title("对象大小 vs 吞吐量")
plt.grid(True)
plt.legend()
plt.savefig("throughput_vs_object_size.png")
plt.show()
