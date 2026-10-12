# code-brand-film

用代码做 15 秒品牌宣传片的 Agent Skill：画面是一页 HTML，用暂停状态的 GSAP 时间轴驱动，由 [HyperFrames](https://github.com/heygen-com/hyperframes) 逐帧渲染；配乐是用 Python 合成的原创曲，节拍跟着画面的切点走。

- `SKILL.md`：工作流程和交付标准
- `references/`：创作方法、工程管线、配乐
- `scripts/`：乐器库、配乐模板、构建模板、审帧脚本

依赖：Node 22+、ffmpeg、Python 3 + numpy。
