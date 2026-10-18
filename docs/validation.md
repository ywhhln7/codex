# 如何验证自己制作的宠物

本页描述建议检查步骤，并不表示示例资产已经通过这里的全部验收。

## 三层检查

1. **格式**：图片尺寸、行列、使用槽位、透明度和非空帧。由 `validate_atlas.py` 检查。
2. **动画**：帧数、角色一致性、持物手、比例、完整肢体、循环与跳跃位移。由动作 GIF、接触表和人工播放检查共同判断。
3. **视线语义**：上、右、下、左要明确，斜向要在正确象限，完整循环不得突然反转。像素差异和中心位移只是辅助证据。

## 独立盲审

```bash
python third_party/hatch_pet/scripts/make_direction_blind_qa_sheet.py runs/my-pet/final/spritesheet.webp --output runs/my-pet/qa/blind.png --answer-key runs/my-pet/qa/blind-answer.json
```

让三个彼此独立的评审者只看 `blind.png`，不要给方向标注图、答案或另一位评审者的结果。每行只判断指定轴，无法辨认时写 `ambiguous`，不应为了成对出现而强行判断为相反方向。

每位输出一个 JSON：

```json
{"pairs":[{"pair":"horizontal-1","A":"screen-left","B":"screen-right","reason":"鼻尖与眼睛的可见方向"}]}
```

需要覆盖图上所有 horizontal/vertical pair。组合并核验：

```bash
python third_party/hatch_pet/scripts/combine_direction_blind_verdicts.py --verdicts runs/my-pet/qa/blind-1.json --verdicts runs/my-pet/qa/blind-2.json --verdicts runs/my-pet/qa/blind-3.json --json-out runs/my-pet/qa/blind-consensus.json
python third_party/hatch_pet/scripts/validate_direction_blind_verdicts.py --answer-key runs/my-pet/qa/blind-answer.json --verdicts runs/my-pet/qa/blind-consensus.json --json-out runs/my-pet/qa/blind-validation.json
```

正方向错误或无法判断应修复。斜向盲审分歧需要结合标注方向、实际尺寸和有序循环复核，不应伪造“通过”报告。修复一格的语义问题时应重新生成包含它的连续整行，并重新组装与复核。

## 本项目代码的本地验证

可以导出示例的九个视频，用 FFmpeg 解码检查视频流；安装脚本可用 `--pet-root artifacts/test-pets` 验证到独立临时目录，而不修改实际应用配置。重复安装同一 ID 应拒绝覆盖。

示例精灵图自带完整人物素材，不包含原始照片。发布时还应检查没有 `.env`、凭据、个人路径、账号信息或应用状态文件进入 Git 提交。
