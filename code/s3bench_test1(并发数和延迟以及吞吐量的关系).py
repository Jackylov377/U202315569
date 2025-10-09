import os
import re
import chardet
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False     # 正常显示负号


RESULT_DIR = "C:/Users/Vampire/s3bench_results1"

concurrency = []
avg_latencies = []
throughputs = []

for fname in os.listdir(RESULT_DIR):
    if not fname.endswith(".txt"):
        continue

    file_path = os.path.join(RESULT_DIR, fname)
    with open(file_path, "rb") as f:
        raw_data = f.read()
        detect = chardet.detect(raw_data)
        encoding = detect["encoding"]

    text = raw_data.decode(encoding, errors="ignore")

    # 从文件内容里找并发数
    match = re.search(r"numClients:\s+(\d+)", text)
    if not match:
        continue
    c = int(match.group(1))

    # 吞吐量 (MB/s)
    thr_match = re.search(r"Total Throughput:\s+([\d\.]+)", text)
    throughput = float(thr_match.group(1)) if thr_match else 0.0

    # 总时长
    dur_match = re.search(r"Total Duration:\s+([\d\.]+)", text)
    duration = float(dur_match.group(1)) if dur_match else 0.0

    # 总请求数
    ns_match = re.search(r"numSamples:\s+(\d+)", text)
    num_samples = int(ns_match.group(1)) if ns_match else 1

    # 平均延迟 (ms)
    avg_latency = (duration / num_samples) * 1000 if num_samples > 0 else 0.0

    concurrency.append(c)
    avg_latencies.append(avg_latency)
    throughputs.append(throughput)

# 排序
if not concurrency:
    raise ValueError("没有成功解析任何数据，请检查 txt 文件格式")

sorted_data = sorted(zip(concurrency, avg_latencies, throughputs))
concurrency, avg_latencies, throughputs = zip(*sorted_data)

# 画延迟曲线
plt.figure()
plt.plot(concurrency, avg_latencies, marker="o")
plt.xlabel("并发数")
plt.ylabel("平均延迟 (ms)")
plt.title("并发数 vs 平均延迟")
plt.grid(True)
plt.savefig("latency_vs_concurrency.png")

# 画吞吐量曲线
plt.figure()
plt.plot(concurrency, throughputs, marker="s", color="red")
plt.xlabel("并发数")
plt.ylabel("吞吐量 (MB/s)")
plt.title("并发数 vs 吞吐量")
plt.grid(True)
plt.savefig("throughput_vs_concurrency.png")

plt.show()
