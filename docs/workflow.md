# 从参考图到宠物：完整流程

所有命令均从仓库根目录执行。使用 ASCII 文件夹名，例如 `runs/my-pet`；显示名称可以是中文。生成目录已经被 `.gitignore` 忽略，原始人物照片应保存在 `private/` 或仓库外。

## 1. 生成主形象

用有权使用的照片作为参考，先生成一张完整的卡通角色。建议保留容易辨认的少量特征，并缩小到实际显示尺寸检查脸和轮廓。原始提示词示例：

```text
以参考照片为基础，生成一个完整的 Q 版卡通人物。
保留深棕长发、轻薄刘海、小熊猫毛绒发箍、浅粉服装和小熊猫挂件。
大头小身体，完整露出鞋子和发箍，轮廓清晰，适合小尺寸桌面显示。
不添加文字、标志、背景、阴影或无关角色，使用真正透明的背景。
```

这一步需要支持参考图的图像生成工具。仓库不包含照片上传、API 调用或模型凭据。不要把原始照片当作公共代码仓库中的默认素材。

## 2. 准备提示词与布局参考

```bash
python third_party/hatch_pet/scripts/prepare_pet_run.py --pet-name "我的卡通伙伴" --pet-id my-pet --reference private/cartoon.png --output-dir runs/my-pet --style-preset sticker
```

脚本会生成 `pet_request.json`、`imagegen-jobs.json`、提示词和布局参考图。自动选择的纯色背景记录在 `pet_request.json`，下文以示例所用的 `#00FFFF` 为例；自己的任务应使用自己的背景色。

先按 `prompts/base-pet.md` 生成标准角色图，保存为 `decoded/base.png`，再将同一张图复制为 `references/canonical-base.png`。之后每组动作都应附上标准角色、与身份有关的参考图和对应布局图。

布局图只规定帧数、间隔和留白，不应被画进结果。纯色背景应与人物的衣服、头发、饰品颜色明显不同。生成整条动作时保留充分间隔，避免相邻头发连在一起。

## 3. 分别生成九组动作

使用 `imagegen-jobs.json` 列出的输入图和提示词，按作业分别生成，保存到 `decoded/<state>.png`。不要让模型一次直接生成最终 8×11 精灵图，也不要用复制同一张图片代替完整动画。

先检查 `idle` 和 `running-right` 的身份、比例与步态。只有服装、标记、光照和持物手都允许时，才能用上游脚本逐帧镜像右跑动作；本示例有单手持物，因此单独生成了左跑。

其余动作也各自生成。特别注意：

- `idle` 只做安静的微动作。
- `jumping` 必须在原图里实际改变垂直位置。
- `running` 是工作/思考，不是脚步奔跑，不额外添加平板等道具。
- `waiting` 是等你回应，不要添加悬浮问号或爱心。
- 角色头饰里原本的爱心图案属于身份特征，不属于悬浮装饰。

## 4. 提取标准动作与生成预览

```bash
python scripts/build_standard.py --run runs/my-pet --stable-states jumping
```

如果源动作完整、比例稳定，但连通域提取失败，可以明确选择共享视口提取；本示例使用：

```bash
python scripts/build_standard.py --run runs/my-pet --stable-states jumping,failed,waiting,review
```

`stable-slots` 是提取方法，不是豁免检查。应检查生成的 `qa/standard-contact.png` 和所有 `qa/previews/*.gif`，确认没有切到头发、遗漏肢体、尺寸跳动或动作反向。此时 `final/standard.webp` 只是九行动作的中间文件，不能作为新的 v2 宠物安装。

## 5. 制作四个视线锚点

先写自己的视线运动计划：脚与下半身锚定在哪里，眼睛如何带动头部，头发和饰物如何跟随，挂件是否随手轻微摆动。人形角色通常用眼睛、眼睑、头颈转向共同表达注意方向，不应旋转整个人物。

生成四帧动作条，固定顺序：**上、屏幕右、下、屏幕左**。保存为 `decoded/look-cardinals.png`。

```bash
python third_party/hatch_pet/scripts/extract_cardinal_anchors.py --strip runs/my-pet/decoded/look-cardinals.png --output-dir runs/my-pet/decoded/look-anchors --chroma-key "#00FFFF" --json-out runs/my-pet/qa/cardinal-anchors.json
python third_party/hatch_pet/scripts/compose_cardinal_anchor_strip.py --anchors-dir runs/my-pet/decoded/look-anchors --output runs/my-pet/decoded/look-anchors-approved.png
```

提取报错时先修复来源。确认四个方向在实际大小下能辨认后，再将它们作为后续的方向依据。

## 6. 按顺序生成两条八方向图

第九行：`000, 022.5, 045, 067.5, 090, 112.5, 135, 157.5`。

第十行：`180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5`。

每一整行使用同一套参考，一次连续生成八帧。不要把八个独立生成的人物拼成一行。第十行还要附上已完成的第九行，保证两行边界连续。

先生成、登记并检查第九行：

```bash
python third_party/hatch_pet/scripts/assemble_extended_atlas.py --base-atlas runs/my-pet/final/standard.webp --look-row-9 runs/my-pet/decoded/look-row-9.png --neutral-cell runs/my-pet/frames/idle/00.png --chroma-key "#00FFFF" --registered-row-output runs/my-pet/qa/look-row-9-registered.png --registration-manifest-output runs/my-pet/qa/look-row-9-registration.json
```

通过后生成第十行，然后组装完整图：

```bash
python third_party/hatch_pet/scripts/assemble_extended_atlas.py --base-atlas runs/my-pet/final/standard.webp --registered-row-9 runs/my-pet/qa/look-row-9-registered.png --row-9-registration runs/my-pet/qa/look-row-9-registration.json --look-row-10 runs/my-pet/decoded/look-row-10.png --neutral-cell runs/my-pet/frames/idle/00.png --chroma-key "#00FFFF" --output runs/my-pet/final/spritesheet.png --webp-output runs/my-pet/final/spritesheet.webp --manifest-output runs/my-pet/final/atlas.json
```

脚本使用同一个登记尺度。若第十行无法在该尺度下完整放入单元格，应修复整行生成图，而不是放宽裁切门槛。

## 7. 透明边缘、结构与视觉检查

对新组装的这一版图执行一次边缘去色溢处理：

```bash
python third_party/hatch_pet/scripts/despill_chroma_edges.py runs/my-pet/final/spritesheet.png --output runs/my-pet/final/spritesheet.png --webp-output runs/my-pet/final/spritesheet.webp --chroma-key "#00FFFF" --json-out runs/my-pet/qa/chroma.json
python third_party/hatch_pet/scripts/validate_atlas.py runs/my-pet/final/spritesheet.webp --require-v2 --chroma-key "#00FFFF" --json-out runs/my-pet/qa/atlas-validation.json
python third_party/hatch_pet/scripts/make_contact_sheet.py runs/my-pet/final/spritesheet.webp --output runs/my-pet/qa/final-contact.png
python third_party/hatch_pet/scripts/make_direction_qa_sheet.py runs/my-pet/final/spritesheet.webp --output runs/my-pet/qa/look-directions.png
python third_party/hatch_pet/scripts/measure_direction_continuity.py runs/my-pet/final/spritesheet.webp --json-out runs/my-pet/qa/continuity.json
```

结构检查不能判断人物是否看反方向。四个正方向必须明确；斜向提示稍弱可以人工复核，但明显错误象限、循环反转、破损和裁切需要修复。上游还提供独立盲审工具，见 [验证说明](validation.md)。不要反复对同一版成品运行去色溢处理。

## 8. 打包、导出、安装

最终包只需 `pet.json` 与 `spritesheet.webp`。示例 `pet.json`：

```json
{
  "id": "my-pet",
  "displayName": "我的卡通伙伴",
  "description": "来自自己参考图的卡通桌面伙伴",
  "spriteVersionNumber": 2,
  "spritesheetPath": "spritesheet.webp"
}
```

将文件放到独立包目录后，使用 README 中的导出与安装命令。发布自己的仓库前，检查提示词、配置和报告中的绝对路径、照片、凭据与账号标识。
