# Copy sheet — every line that appears on screen, and where it came from

`film_audit.py` fails if any visible text in `film/index.html` is missing here.
Source column: `brief` (quote the brief), `product page` (URL), `UI` (text the
product itself shows), `data` (example values), or `INVENTED — flag to client`.

| On screen | Source |
| --- | --- |
| 把这周的数据整理成报告，做成演示稿，明早发给大家。 | brief: example task the product handles |
| acme work · 一句话派活 | brief: feature name "一句话派活" |
| 一句话派活 · 自动执行 · 交付成果 | brief: three-step value chain |
| 你说一句，它拆成六步。 | brief: "自动拆解任务" |
| 读取数据 / 清洗 · 汇总 / 生成图表 / 撰写报告 / 排版成演示稿 / 定时发送 / 进行中 | UI: task step names and status |
| 电脑合上了，活还在继续。 | brief: "后台运行" |
| 合上电脑也不停 ｜ 手机 · 电脑 · 网页同步 | brief: P0 selling point, multi-device sync |
| 本地电脑 / 云端 · 运行中 / 手机 / % · 云端执行 / % · 生成中 / web | UI: device labels and status |
| 23:40 / 08:52 / 星期四 → 星期五 | data: overnight clock |
| 醒来，已经交付。 | brief: deliverables arrive |
| 周报 / 第42周 周报 / 演示文稿 · 套用公司模板 / Q3 复盘 / 表格 / 渠道数据汇总 / TOTAL | UI: deliverable titles |
| 周报已发送给 团队（12人） / PPT 与数据表已附上 | UI: notification text |
| 重复的活儿交给它，你只负责思考和决定 | brief: mandatory selling line |
| Acme 工作台 | brand name |
| 下载电脑版 · 免费试用 | brief: CTA |
| acme.example | brand URL |
