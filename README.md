# code-brand-film

用代码做 15 秒品牌宣传片的 Agent Skill：画面是一页 HTML，用暂停状态的 GSAP 时间轴驱动，由 [HyperFrames](https://github.com/heygen-com/hyperframes) 逐帧渲染；配乐是用 Python 合成的原创曲，节拍跟着画面的切点走。

- `SKILL.md`：工作流程和交付标准
- `references/`：创作方法、质量门槛、动效配方、分镜表、工程管线、配乐
- `scripts/`：两道质量闸门（`film_audit.py` 查代码，`frame_audit.py` 查渲染出的画面）、乐器库、配乐模板、构建模板、审帧脚本
- `examples/office-agent/`：一条完整可渲染的参考片，附分镜表、文案出处表和联系表

用法要点：先填 `shot-list.md` 和 `copy.md` 再写代码；两道闸门都 `0 failed` 才算能交付。门槛是下限，不是目标。

依赖：Node 22+、ffmpeg、Python 3 + numpy。
