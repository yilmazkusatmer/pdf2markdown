<div align="center">

<h1>MarkPDFDown</h1>
<p align="center"><a href="./README.md">English</a> | 中文 </p>

[![Size]][hub_url]
[![Pulls]][hub_url]
[![Tag]][tag_url]
[![License]][license_url]
<p>基于多模态大语言模型的PDF转Markdown工具，高质量实现文档结构化转换</p>

![markpdfdown](https://raw.githubusercontent.com/jorben/markpdfdown/refs/heads/master/tests/markpdfdown.png)

</div>

## 项目概述

MarkPDFDown 是一款智能PDF转换Markdown工具，通过先进的多模态AI模型，能够将PDF文档准确转换为结构清晰的Markdown格式，保留原始文档的排版、表格、公式等复杂元素。

## 功能特性

- **PDF转Markdown**：支持任意PDF文档的格式转换
- **多模态理解**：利用AI理解文档结构和内容
- **格式保留**：完整保留标题、列表、表格等排版元素
- **模型定制**：支持自定义AI模型参数配置

## 示例演示
![](https://raw.githubusercontent.com/jorben/markpdfdown/refs/heads/master/tests/demo.png)

## 安装指南

```bash
conda create -n markpdfdown python=3.9
conda activate markpdfdown

# 克隆仓库
git clone https://github.com/jorben/markpdfdown.git
cd markpdfdown

# 安装依赖
pip install -r requirements.txt
```

## 使用指南
```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY=<你的API密钥>
# 可选设置API端点
export OPENAI_API_BASE=<你的API端点>
# 可选设置默认模型
export OPENAI_DEFAULT_MODEL=<你的模型>

# 运行转换程序
python main.py < tests/input.pdf > output.md
```

## 高级用法
```bash
# 转换指定页码范围
python main.py 起始页码 结束页码 < tests/input.pdf > output.md
```

## 在Docker中使用
```bash
docker run -i -e OPENAI_API_KEY=<你的API密钥> -e OPENAI_API_BASE=<你的API端点> -e OPENAI_DEFAULT_MODEL=<你的模型> jorben/markpdfdown < tests/input.pdf > output.md
```

## 依赖环境
- Python 3.9+
- 依赖库详见 `requirements.txt`
- 可访问的多模态AI模型服务

## 贡献指南
欢迎贡献代码！请按以下流程提交PR：

1. Fork 本仓库
2. 新建功能分支（ `git checkout -b feature/somefeat` ）
3. 提交修改（ `git commit -m 'feat: 添加XX新功能'` ）
4. 推送分支（ `git push origin feature/somefeat` ）
5. 提交Pull Request

## 开源协议
本项目采用 Apache License 2.0 开源协议，详见 LICENSE 文件。

## 致谢
- 感谢多模态AI模型的技术支持
- 受PDF转Markdown工具需求启发而开发

[hub_url]: https://hub.docker.com/r/jorbenzhu/markpdfdown/
[tag_url]: https://github.com/jorben/markpdfdown/releases
[license_url]: https://github.com/jorben/markpdfdown/blob/main/LICENSE

[Size]: https://img.shields.io/docker/image-size/jorbenzhu/markpdfdown/latest?color=066da5&label=size
[Pulls]: https://img.shields.io/docker/pulls/jorbenzhu/markpdfdown.svg?style=flat&label=pulls&logo=docker
[Tag]: https://img.shields.io/github/release/jorben/markpdfdown.svg
[License]: https://img.shields.io/github/license/jorben/markpdfdown