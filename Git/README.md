# Git 数据工作区

这个文件夹用于 **2027 第四届大学生数据要素素质大赛** 的代码与数据管理，配合 VS Code 使用。

> 仓库根目录是 `C:\Users\LZZ\Desktop\Git`；本文件在仓库的 `Git/` 子目录下。

## 推荐结构

```
Git/
├── .gitignore
├── README.md
├── data/
│   ├── raw/          # 原始数据：默认不提交
│   ├── processed/    # 清洗后数据：可提交
│   └── sample/       # 小样本：可提交
├── notebooks/        # Jupyter 笔记本
├── scripts/          # 清洗、分析、绘图脚本
└── docs/             # 数据字典、字段说明
```

## 提交规则

**不要提交：**

- `data/raw/`、`data/private/` 里的原始/私密数据；
- `.env`、`*.key`、`*.pem`、账号密码；
- 压缩包、模型权重（`*.pt` / `*.pth` / `*.onnx` 等）；
- 超过 50MB 的大文件；
- `.docx` / `.doc`（报告放仓库根目录的 `2027数据要素大赛/`，不放这里）。

**建议提交：**

- 清洗脚本、分析脚本、绘图脚本；
- 小样本数据（`data/sample/`）；
- 数据字典、字段说明、README；
- 图表、可复现的 notebook（清空输出后再提交）。

## 如果确实要提交原始数据

默认被忽略的文件，可以强制添加：

```bash
git add -f data/raw/你的文件.csv
```

但提交前确认：**没有个人隐私、没有密钥、文件不大**。

## 大文件

超过 50MB 的文件不要直接提交。两个办法：

1. 用 Git LFS：
   ```bash
   git lfs install
   git lfs track "*.csv"
   git add .gitattributes
   ```
2. 放网盘，在 `docs/` 里写清楚下载方式。

## VS Code 使用

1. 用 VS Code 打开 `C:\Users\LZZ\Desktop\Git`；
2. 左侧“源代码管理”会识别到仓库；
3. 改动后写 commit message，点提交，再点“同步更改”推送；
4. 提交前看一眼“更改”列表，确认没有 `data/raw/`、`.env`、大文件。

## 目录说明

- `data/raw/`：只读原始数据，不进 Git；
- `data/processed/`：清洗后的分析表，可进 Git；
- `data/sample/`：给评委/队友复现用的小样本，可进 Git；
- `scripts/`：所有清洗、分析、绘图代码；
- `notebooks/`：探索性分析，提交前清空输出；
- `docs/`：数据字典、口径说明、来源与许可。
