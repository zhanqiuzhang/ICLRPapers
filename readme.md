# ICLR 论文数据爬取
用于从 openreview 获取 ICLR 论文数据，计算 reviews 的得分情况，利用 LLM 生成题目和摘要的中文翻译并总结关键词。

ICLR2025 的相关数据已上传至 https://huggingface.co/datasets/QAQqaq/ICLR2025Openreview



## 使用说明
- 安装依赖 `pip install -r requirements.txt`
- 修改配置文件 `config.yaml`，其中 `gateway` 为 [ AWS  API 网关服务](https://docs.aws.amazon.com/powershell/latest/userguide/creds-idc.html)，可以避免触发请求 openreview API 的 rate limit，从而大幅提升 reviews 的爬取速度，如无可删除 `gateway` 这一配置项
- 运行 `python main.py --config config.yaml` 

## 其他
- openreview API 调用部分的代码参考了 [openreview-visualization](https://github.com/ranpox/openreview-visualization)，感谢 ranpox 大佬的开源贡献。