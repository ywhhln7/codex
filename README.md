# Cartoon Pet Workshop · 照片变卡通桌面宠物

把一张照片转成统一的 Q 版角色，制作 **9 组动作 + 16 个视线方向**，再导出独立视频或打包成 Codex 兼容的桌面宠物。

这是一次真实制作过程的整理：既包含成功的步骤，也记录了跳跃被自动对齐、左右视线画反、安装后没有自动选中等问题。原始人物照片、账号凭据及本机配置均未收录。

> 这是独立的流程示例。图像由图像生成工具制作，Python 负责提取、拼图、导出和本地安装；运行代码不会自动生成新的人物或动作。不同应用版本的宠物入口与格式可能变化。

## 效果预览

| 挥手 | 跳跃 | 失落 |
| --- | --- | --- |
| ![挥手](examples/panda-girl/previews/waving.gif) | ![跳跃](examples/panda-girl/previews/jumping.gif) | ![失落](examples/panda-girl/previews/failed.gif) |

示例角色叫 **熊猫酱**：深棕长发、小熊猫发箍、浅粉衣服，以及手中的小熊猫挂件。

## 五步制作流程

1. **照片转角色**：提取发型、服装与配饰特征，生成完整的卡通人物；本项目只公开卡通结果。
2. **固定标准形象**：生成后续动作共用的参考图，统一头身比例、眼睛、轮廓、服装、持物手和配色。
3. **分别生成动作条**：待机、向右跑、向左跑、挥手、跳跃、失落、等待、工作、查看结果分别生成；每条使用同一角色参考。
4. **制作视线方向**：先确认上、右、下、左四个锚点，再生成两条连续的八方向图。方向以屏幕为准。
5. **脚本处理与安装**：去除背景、保留动作位移、拼成精灵图，查看动画预览，导出 MP4 或放入本地宠物目录，最后在应用里选择。

详细步骤和命令见 [制作流程](docs/workflow.md)，实际遇到的问题见 [制作复盘](docs/lessons.md)。代码导出与临时安装的本地运行结果见 [检查记录](docs/local-checks.json)。

## 快速使用现有示例

需要 Python 3.10+。在仓库根目录运行：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

导出九个独立 MP4（默认 720×720、浅粉背景、无声、每个循环六次）：

```bash
python scripts/export_videos.py --atlas examples/panda-girl/spritesheet.webp
```

只导出某个动作：

```bash
python scripts/export_videos.py --atlas examples/panda-girl/spritesheet.webp --state waving --loops 8
```

导出透明 GIF：

```bash
python scripts/export_gifs.py --atlas examples/panda-girl/spritesheet.webp
```

输出都在默认忽略的 `artifacts/` 下。MP4 使用 H.264，不保留透明通道；GIF 保留透明背景。低分辨率精灵放大后不会增加原始细节。

## 安装为本地宠物

```bash
python scripts/install_pet.py --package examples/panda-girl
```

这会复制 `pet.json` 与 `spritesheet.webp` 到 `$CODEX_HOME/pets/panda-girl/`；未设置 `CODEX_HOME` 时使用 `~/.codex/pets/`。已有同名目录时会停止，不覆盖已有宠物。

随后在应用的 **设置 → Pets / 宠物 → 刷新** 中选择 **熊猫酱**。文件已安装不等于应用已选中。此安装脚本不修改账号或应用内部配置，不自动切换活动宠物。

如果你的应用没有这个入口，先确认其版本和自定义宠物支持情况。

## 动作与文件格式

| 状态 | 含义 | 帧数 |
| --- | --- | ---: |
| `idle` | 待机、呼吸、眨眼 | 6 |
| `running-right` | 向右拖动时的奔跑 | 8 |
| `running-left` | 向左拖动时的奔跑 | 8 |
| `waving` | 挥手 | 4 |
| `jumping` | 起跳、腾空、落地 | 5 |
| `failed` | 失落、失败反应 | 8 |
| `waiting` | 等待回应 | 6 |
| `running` | 思考或工作，区别于脚步奔跑 | 6 |
| `review` | 查看结果 | 6 |

v2 精灵图为 **1536×2288**，8 列×11 行，每格 **192×208**。前九行为动作，后两行为十六个顺时针视线方向。`000` 表示向上，`090` 向右，`180` 向下，`270` 向左。具体槽位和额外中性帧以兼容应用及上游验证脚本为准。

## 仓库内容

```text
scripts/                     可移植的导出、组装与安装入口
docs/                        制作流程、问题复盘、验证说明
examples/panda-girl/          卡通图、精灵图、GIF 预览、生成提示词
third_party/hatch_pet/        保留许可的上游处理脚本与格式文档
```

## 示例状态与复用边界

- 示例的九组动作做过帧数、透明背景和播放检查，跳跃位移问题已经修正。
- 视线制作过程做过方向修复；实际交付版本按使用者要求跳过了修正版的最终完整验收。因此不能把此仓库当作全套动画均已通过最终验收的证明，斜向视线仍建议人工检查。
- 公开代码不包含图像生成模型、API 密钥，也不保证同一提示词每次得到一致的角色。
- 更换自己的参考图时，请确认有权使用和公开相关形象。示例人物素材不随代码许可自动授予肖像或商业使用权。

## 许可与来源

代码与文档使用 [Apache-2.0](LICENSE)。`third_party/hatch_pet/` 来自安装环境中 OpenAI 随应用提供的 hatch-pet 工具，原始许可一并保留，未把这些脚本当作本项目独立原创。新增入口负责便携参数、视频导出与本地安装。详见 [NOTICE](NOTICE)。示例人物素材的复用边界见上一节。
