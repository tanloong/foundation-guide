# 银河系漫游指南：基地

**THE HITCHHIKER'S GUIDE TO THE FOUNDATION**

一个运行在终端里的英文文字冒险游戏。三名主角，三幕故事，三十四个场景，一百四十六件物品，二十三个角色，以及一条毛巾。

故事发生在艾萨克·阿西莫夫《基地》三部曲的宇宙里，叙述方式则借用了道格拉斯·亚当斯《银河系漫游指南》的刻薄幽默。你将依次扮演盖尔·多尼克、萨尔沃·哈丁和贝泰·达瑞尔，在心理史学的裂缝里生存、谈判、解谜，并决定银河系的未来要不要被一个穿小丑服的人拿走。

> 本项目是粉丝作品，与阿西莫夫遗产、出版商以及并不存在的第二基地均无关系。

---

## 快速开始

### 环境要求

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/)

项目只使用 Python 标准库，没有第三方依赖。

### 启动

在 Windows 上，直接双击：

```text
play.bat
```

或者在项目目录中打开终端：

```powershell
cd foundation-guide
uv run python -m foundation_guide
```

其他平台：

```bash
uv run python -m foundation_guide
```

### 命令行选项

```text
--no-color        关闭 ANSI 颜色
--ascii           使用 ASCII 边框和符号
--width N         指定文本宽度
--load [名字]     读取存档（默认读取 autosave）
--script 文件     从脚本文件播放命令（测试 / 演示用）
--debug           出错时显示完整 traceback
--version         显示版本
```

例如：

```powershell
uv run python -m foundation_guide --no-color --width 88
uv run python -m foundation_guide --script tests\walkthrough_full.txt --no-color
```

---

## 三幕故事

| 幕 | 标题 | 主角 | 舞台 |
|---|---|---|---|
| I | The Psychohistorians | 盖尔·多尼克（Gaal Dornick） | 川陀 |
| II | The Mayors | 萨尔沃·哈丁（Salvor Hardin） | 端点星 |
| III | The Mule | 贝泰·达瑞尔（Bayta Darell） | 卡尔甘、川陀、罗森 |

每一幕都有独立的场景、人物、谜题、计分和结局。完成一幕会自动进入下一幕，并在幕间写入自动存档。

---

## 操作方式

游戏接受自然的英文命令。冠词、大小写和标点基本可以忽略，`IT` / `THEM` 会指代上一个提到的对象。

### 移动

```text
NORTH / SOUTH / EAST / WEST / UP / DOWN
N / S / E / W / U / D
GO <出口>        ENTER <地点>        EXIT
BOARD <飞船>
```

### 探索与物品

```text
LOOK             EXAMINE <对象>       READ <对象>
SEARCH <对象>    TAKE <对象>          TAKE ALL
DROP <对象>      INVENTORY / I
OPEN / CLOSE <对象>
UNLOCK <对象> WITH <钥匙>
WEAR / REMOVE <衣物>
PUT <对象> IN / ON <容器>
```

### 人物与谜题

```text
TALK TO <人物>
ASK <人物> ABOUT <话题>
GIVE <对象> TO <人物>
SHOW <对象> TO <人物>
USE <对象> [ON <对象>]
PUSH / PULL / PRESS / TURN / SWITCH <对象>
SET <对象> TO <值>
TYPE <文字>
SAY <话>
```

### 元命令

```text
GUIDE              列出已解锁的指南条目
GUIDE <话题>       阅读条目
HINT               当前进度的提示（不扣分）
MAP                显示已访问场景的地图
SCORE              查看分数、等级和统计
SAVE [名字]        保存（默认 quicksave）
LOAD [名字]        读取（默认 quicksave）
UNDO               撤销一回合
RESTART            重新开始（需要确认）
ACHIEVEMENTS       查看成就
QUIT               离开游戏
```

---

## 系统特色

- **三幕完整流程**：每一幕都有独立的地图、谜题链、角色对话和结局。
- **宽容的解析器**：支持 `PICK UP`、`LOOK AT`、`PUT X IN Y`、`USE X ON Y`、`ASK X ABOUT Y`、代词、`TAKE ALL` 和方向缩写。
- **可解锁的《指南》**：20 条幽默条目，通过探索、交谈和推进剧情解锁。`GUIDE` 随时可读。
- **不会卡死的死亡**：死亡会自动回退一回合，并恢复死亡前的状态；游戏没有不可挽回的死局。
- **提示不扣分**：`HINT` 只影响指南对你的评价，不影响分数。
- **计分与评价**：每幕 100 分，总计 300 分；根据总分获得不同等级，并解锁成就。
- **多种结局**：第二幕有两种执政路线，第三幕有两种最终选择。每种选择都值满分，也都需要承担后果。
- **存档**：JSON 格式，位于 `saves/`；幕间自动存档，也可以随时手动保存。
- **纯标准库**：没有第三方依赖，克隆即可运行。

---

## 攻略与测试

完整攻略在 **[walkthrough.md](walkthrough.md)**，包含三幕的推荐路线、两种结局和计分明细。攻略含大量剧透，建议先自己玩一遍。

运行自动化测试：

```powershell
uv run python -m unittest discover -s tests -v
```

当前测试覆盖：

- 解析器的方向、复合动词、冠词、代词、`USE ... ON ...`、`SET ... TO ...` 等行为
- 三幕世界的完整性（出口、物品位置、NPC 位置、指南条目）
- 第一幕 100 分路线
- 第二幕“信仰”与“贸易”两种结局，各 100 分
- 第三幕“安静的一枪”与“沉默”两种结局，各 100 分
- 三幕连续通关 300 分
- 提示不扣分、死亡回退、存读档、指南查找

也可以直接播放脚本，观察完整流程：

```powershell
uv run python -m foundation_guide --script tests\walkthrough_full.txt --no-color
```

---

## 项目结构

```text
foundation-guide/
├─ foundation_guide/
│  ├─ __main__.py        命令行入口与菜单
│  ├─ engine.py          游戏循环、命令分派、计分、存读档
│  ├─ model.py           Room / Object / NPC / Exit / World 数据模型
│  ├─ state.py           ActState 与 Meta 的可序列化状态
│  ├─ parser.py          宽容的英文命令解析器
│  ├─ ui.py              终端输出、换行、颜色、脚本模式
│  ├─ guide.py           20 条《指南》条目
│  └─ episodes/
│     ├─ act1.py         第一幕：心理史学家
│     ├─ act2.py         第二幕：市长
│     └─ act3.py         第三幕：骡
├─ tests/
│  ├─ test_game.py       自动化测试
│  ├─ walkthrough_*.txt  各幕与全流程脚本
│  └─ run_act.py         单幕调试运行器
├─ saves/                存档目录
├─ pyproject.toml
├─ play.bat
├─ walkthrough.md
└─ README.md
```

---

## 设计说明

游戏采用数据驱动的结构：每一幕都是一个 `World`，其中包含房间、物品、NPC 和出口。所有可变状态集中在 `ActState` 中，因此存档、读档和撤销都只是状态的序列化或快照。NPC 对话、谜题条件和计分事件以回调函数的形式挂在数据对象上，使剧情逻辑与引擎分离。

文本风格尽量贴近两位原作者的混合物：阿西莫夫式的历史尺度与政治逻辑，加上亚当斯式的脚注、官僚主义的荒诞，以及一条永远不该被低估的毛巾。

---

## 致谢

- 故事与角色来自艾萨克·阿西莫夫的《基地》三部曲。
- 幽默风格致敬道格拉斯·亚当斯的《银河系漫游指南》。
- 本作是非商业性的粉丝作品，仅供学习与娱乐。

所以，别慌。带上毛巾。历史正在看着你。
