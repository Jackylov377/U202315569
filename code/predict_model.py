import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import lognorm, genpareto

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置：s3bench 输出目录
result_dir = "C:/Users/Vampire/s3bench_results_highdata"
data_list = []

# 遍历输出文件
for file in os.listdir(result_dir):
    if not file.endswith(".txt"):
        continue

    filepath = os.path.join(result_dir, file)

    match = re.match(r"result_size_(\d+)_clients_(\d+)_run\d+\.txt", file)
    if match:
        obj_size = int(match.group(1))
        clients = int(match.group(2))
    else:
        obj_size = -1
        clients = -1

    # 读取文本（尝试多种编码）
    encodings = ["utf-8", "utf-16", "latin1"]
    text = None
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        with open(filepath, "rb") as f:
            text = f.read().decode(errors="ignore")

    # 提取延迟与吞吐量
    latencies = [float(x)*1000 for x in re.findall(r"completed in ([\d\.]+)s", text)]
    throughputs = [float(x) for x in re.findall(r"- ([\d\.]+)MB/s", text)]

    latencies = [l for l in latencies if l > 0]
    for lat, tp in zip(latencies, throughputs):
        data_list.append({
            "object_size": obj_size,
            "clients": clients,
            "latency_ms": lat,
            "throughput_MBps": tp
        })

# 转为 DataFrame
df = pd.DataFrame(data_list)
if df.empty:
    print("没有捕获到延迟数据，请检查 s3bench 是否使用 verbose 模式。")
    exit()

# 平均延迟 / 吞吐量趋势
summary_avg = df.groupby(["object_size", "clients"]).agg({
    "latency_ms": "mean",
    "throughput_MBps": "mean"
}).reset_index()

plt.figure(figsize=(8,5))
for obj in sorted(summary_avg["object_size"].unique()):
    sub = summary_avg[summary_avg["object_size"]==obj]
    plt.plot(sub["clients"], sub["latency_ms"], marker='o', label=f"{obj}B")
plt.xlabel("并发数")
plt.ylabel("平均延迟 (ms)")
plt.title("平均延迟 vs 并发数")
plt.legend()
plt.grid(True)
plt.savefig("avg_latency_vs_clients.png")
plt.show()

plt.figure(figsize=(8,5))
for obj in sorted(summary_avg["object_size"].unique()):
    sub = summary_avg[summary_avg["object_size"]==obj]
    plt.plot(sub["clients"], sub["throughput_MBps"], marker='o', label=f"{obj}B")
plt.xlabel("并发数")
plt.ylabel("平均吞吐量 (MB/s)")
plt.title("平均吞吐量 vs 并发数")
plt.legend()
plt.grid(True)
plt.savefig("avg_throughput_vs_clients.png")
plt.show()

# 混合分布尾延迟建模 (LogNormal + GPD)
results = []

for (obj_size, clients), group in df.groupby(["object_size", "clients"]):
    lat = np.array(group["latency_ms"])
    if len(lat) < 20:
        continue

    # 主体部分与尾部部分分离（例如前90% vs 后10%）
    q_cut = np.percentile(lat, 90)
    body = lat[lat <= q_cut]
    tail = lat[lat > q_cut]

    # 拟合主体分布 (Log-normal)
    try:
        shape, loc, scale = lognorm.fit(body, floc=0)
    except Exception:
        continue

    # 拟合尾部分布 (GPD)
    excess = tail - q_cut
    try:
        c, loc_g, scale_g = genpareto.fit(excess, floc=0)
    except Exception:
        continue

    # 构建混合分布预测CDF
    def hybrid_cdf(x):
        if x <= q_cut:
            return 0.9 * lognorm.cdf(x, shape, loc=loc, scale=scale) / lognorm.cdf(q_cut, shape, loc=loc, scale=scale)
        else:
            return 0.9 + 0.1 * genpareto.cdf(x - q_cut, c, loc=loc_g, scale=scale_g)

    # 预测 P95 / P99 / P99.9
    x_vals = np.linspace(min(lat), max(lat)*1.2, 2000)
    cdf_vals = np.array([hybrid_cdf(x) for x in x_vals])
    p95 = x_vals[np.searchsorted(cdf_vals, 0.95)]
    p99 = x_vals[np.searchsorted(cdf_vals, 0.99)]
    p999 = x_vals[np.searchsorted(cdf_vals, 0.999)]

    results.append({
        "object_size": obj_size,
        "clients": clients,
        "P95(ms)": p95,
        "P99(ms)": p99,
        "P99.9(ms)": p999
    })

    # 可视化：实测CDF vs 拟合混合CDF
    plt.figure(figsize=(6,4))
    sorted_lat = np.sort(lat)
    empirical_cdf = np.arange(1, len(sorted_lat)+1)/len(sorted_lat)
    plt.plot(sorted_lat, empirical_cdf, label="实测CDF", lw=2)
    plt.plot(x_vals, cdf_vals, 'r--', lw=2, label="预测CDF (LogN+GPD)")
    plt.xlabel("延迟 (ms)")
    plt.ylabel("CDF")
    plt.title(f"对象 {obj_size}B 并发 {clients}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"cdf_对象大小{obj_size}_并发数{clients}.png")
    plt.close()

# 输出预测表
df_tail = pd.DataFrame(results)
df_tail = df_tail.sort_values(["object_size","clients"])
df_tail.to_csv("尾延迟预测表.csv", index=False)
print("混合模型尾延迟预测表已生成: 尾延迟预测表.csv")
