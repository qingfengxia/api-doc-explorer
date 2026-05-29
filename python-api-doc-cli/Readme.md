# Python Api Explorer

> **CLI usage examples**: See [SKILL.md](SKILL.md) for full CLI reference and query examples.



## Python module has API doc builtin



Unlike other languages, in-code documentation has been strip from runtime binary, Python keeps the API doc inside the module and can be easily retrieved 

If a api-docs.json is required, using the `gen_docs.py` script to generate



## `python-api-explore.py` CLI usage

查询层级	示例	结果
模块级	torch.distributed	✅ 列出 115 个 API
模块.类	torch.distributed.Backend	✅ 类详情 + 方法列表
模块.函数	torch.distributed.init_process_group	✅ 函数签名 + 参数 + 返回值
模块.类.方法	torch.distributed.Backend.register_backend	✅ 方法详情 + 参数 + 返回值
