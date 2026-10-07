# GitHub 上传说明

本包为 v1.1.0 本地候选版，未推送 GitHub，未发布 Zenodo。

1. 解压后，把顶层文件和目录合并到现有 ETAS-network 仓库根目录，
   不要再嵌套一层 ETAS-network-v1.1.0。保留线上无关改动。
2. 核对差异后提交；不要删除旧版本 tag 或 Zenodo 记录。
3. 建议先运行 README 的安装、pytest 和 verify_reference.py。
4. 创建 GitHub release v1.1.0，再在原 Zenodo 记录下创建新版本。
   如已启用 GitHub–Zenodo 自动归档，不要重复手动上传另一条记录。
5. 新版本 DOI 生成后，更新 README、CITATION.cff 和论文中的软件引用；
   旧 DOI 仅标为上一版本，不冒充本次版本 DOI。

主要更新包括 RW40/SR640、200 次零模型、20 次 Louvain 重启、
固定 holdout 样本、排除 source 本身、派生网络和最终统计参考文件。

不包含原始目录、断层数据库、论文 Word、临时日志或账户信息。
这不是从原始目录自动拟合 ETAS 的完整流水线，也未收录全部论文绘图脚本。
本包已与线上 53b70a1 版本核对，保留原作者信息与旧版本链接。
后续上传仍应检查 GitHub diff，避免覆盖线上其他改动。

归档中的事件编号仅在对应目录/节点映射下有效。正式实验固定样本
最初按 seed=12345 的 partition 筛选，后来采用 best-of-20 评价时仍保留该样本。
代码对此保持一致，不能擅自改成重新筛选。
