# 完整攻略

> **严重剧透警告。** 本文包含三幕的全部谜题解法、计分点和两种结局。建议先自己玩一遍，卡住时再用 `HINT`。

---

## 通用建议

- 游戏文本是英文，但命令非常宽容：冠词可省略，`N/S/E/W/U/D` 可用，`IT` / `THEM` 会指代上一个对象。
- `HINT` 不扣分，只增加“提示次数”统计。连续输入会重复同一阶段的提示。
- 死亡会自动回退一回合，不会造成不可挽回的损失。
- `UNDO` 可以撤销上一回合；`SAVE` / `LOAD` 使用 `saves/` 目录中的 JSON 文件。
- 每一幕满分 100，总计 300。两个结局都值满分，选择只看你想承担哪种后果。
- `GUIDE` 可以阅读已解锁的幽默条目；探索、交谈和推进剧情都会解锁新条目。

---

## 第一幕：The Psychohistorians

**主角：** 盖尔·多尼克  
**地点：** 川陀  
**目标：** 找到哈里·谢顿，在审判中活下来，登上流放船。

### 推荐路线

```text
take suitcase
open suitcase
read letter
use visa on pedestal
north
use credit chip on fare machine
board taxi
show letter to clerk
go elevator
open door
north
use holo projector
open drawer
take library card
take overdue book
south
go down
go west
read statue
ask student about password
say "don't panic"
north
give overdue book to librarian
open archive door
go archive
take data tape
read data tape
west
south
go old wing
north
talk to seldon
open drawer
take prime radiant
take decoy cube
put prime radiant in towel
south
say no
show data tape to chen
give decoy cube to chen
go launch bay
read manifest
board encyclopedia
```

### 关键点

1. **太空港**：手提箱里有签证和告别信。`USE VISA ON PEDESTAL` 才能通过安检。
2. **出租车**：车费机需要信用芯片；没有芯片就付不起车费。
3. **酒店**：给前台看信，乘电梯上楼；全息投影会揭示抽屉的线索。
4. **大学图书馆**：先读雕像，再问学生暗号。暗号是 `DON'T PANIC`。把逾期书还给图书管理员，才能打开档案室。
5. **旧翼**：和谢顿交谈后，拿走真正的 Prime Radiant 和假立方体。把真货藏进毛巾，别让帝国拿到。
6. **审判**：拒绝认罪（`SAY NO`），把数据带作为证据展示给陈专员，再把假立方体交给他。真货一旦暴露，你会被处决。
7. **发射湾**：读舱单，登上 *Encyclopedia Galactica*。登船即完成本幕。

### 计分点（100 分）

| 事件 | 分数 |
|---|---:|
| 签证 / 安检 | 5 |
| 手提箱 | 5 |
| 告别信 | 5 |
| 出租车 | 5 |
| 酒店入住 | 5 |
| 全息投影 | 10 |
| 借书证 | 2 |
| 归还逾期书 | 2 |
| 数据带 | 5 |
| 学生暗号 | 3 |
| 与谢顿交谈 | 15 |
| 把 Prime Radiant 藏进毛巾 | 5 |
| 庭审拒绝认罪 | 5 |
| 数据带作为证据 | 5 |
| 交出假立方体 | 10 |
| 舱单 | 2 |
| 登上正确的船 | 11 |
| **合计** | **100** |

---

## 第二幕：The Mayors

**主角：** 萨尔沃·哈丁  
**地点：** 端点星  
**目标：** 化解安纳克里昂的最后通牒，让“科学宗教”运转起来。

### 推荐路线（信仰结局）

```text
read ultimatum
read logic sheets
take logic sheets
open cabinet
take whiskey
east
show logic sheets to pirenne
west
south
read newspaper
south
talk to rodric
give whiskey to rodric
north
east
talk to verisof
north
open vault door
go vault
west
south
talk to verisof
talk to aporat
west
west
read reactor manual
open supply crate
take power cell
south
take waveguide
north
east
east
use waveguide on relay
use power cell on relay
use frequency card on relay
use cipher on relay
use relay
west
south
talk to wienis
say faith
```

### 另一种结局

把最后一句换成：

```text
say trade
```

两种路线都得到 100 分，区别在于哈丁选择用**宗教**还是**贸易**控制四王国。`say faith` 更接近原著的“科学宗教”路线；`say trade` 更冷酷，也更像一份长期商业合同。

### 关键点

1. **市长办公室**：读最后通牒和逻辑分析，拿走威士忌。逻辑分析是说服皮雷纳的关键。
2. **议会**：把逻辑表给皮雷纳看，让他明白条约没有约束力。
3. **城市广场 / 着陆台**：读报纸，和罗德里克交谈，把威士忌送给他，换取信息。
4. **神庙**：与韦里索夫交谈，进入地下时间穹顶，听谢顿的录音。出来后与韦里索夫和阿波拉特交谈，获得进入动力站的许可。
5. **动力站 / 车间**：读反应堆手册，拿动力电池和波导。
6. **中继器**：依次安装波导、动力电池、频率卡，再用密码激活。广播会让安纳克里昂舰队“看见神迹”，从而瘫痪。
7. **着陆台**：与维尼斯亲王对质，选择 `SAY FAITH` 或 `SAY TRADE`。

### 计分点（100 分）

| 事件 | 分数 |
|---|---:|
| 阅读最后通牒 | 5 |
| 阅读逻辑分析 | 5 |
| 说服皮雷纳 | 10 |
| 读报纸 | 3 |
| 威士忌 | 5 |
| 与韦里索夫交谈 | 5 |
| 时间穹顶 | 10 |
| 反应堆手册 | 2 |
| 动力电池 | 3 |
| 波导 | 3 |
| 安装波导 | 3 |
| 安装动力电池 | 3 |
| 安装频率 | 3 |
| 激活中继广播 | 20 |
| 最终主义（信仰 / 贸易） | 20 |
| **合计** | **100** |

---

## 第三幕：The Mule

**主角：** 贝泰·达瑞尔  
**地点：** 卡尔甘 → 川陀 → 罗森  
**目标：** 逃出骡的宫殿，找到第二基地的线索，并在最后一刻做出选择。

### 推荐路线（安静的一枪）

```text
read newspaper
talk to magnifico
east
up
read itinerary
open wardrobe
take uniform
wear uniform
open minibar
take wine
down
west
north
give wine to major-domo
east
open trophy case
take visi-sonor
west
south
give visi-sonor to magnifico
south
board yacht
open locker
take glowlamp
take blaster
take credentials
set course to trantor
pull lever
search rubble
down
show credentials to caretaker
east
read star atlas
use visi-sonor on mis
west
up
board yacht
set course to rossem
pull lever
north
talk to elder
east
shoot mis
```

### 另一种结局

把最后一句换成：

```text
say nothing
```

- `SHOOT MIS`：阻止埃布林·米斯说出第二基地的位置。这是原著式的结局，秘密保住了，但贝泰必须背负杀友的代价。
- `SAY NOTHING`：让米斯说完。骡得到坐标，第二基地面临正面进攻。这是一个开放的“如果”结局。

两种结局都得到 15 分，第三幕总分仍为 100。

### 关键点

1. **卡尔甘海滨**：读报纸，和小丑马格尼菲科交谈。他需要他的 Visi-Sonor。
2. **酒店套房**：读行程表，打开衣柜拿制服并穿上，打开迷你吧拿酒。制服是进入宫殿的员工通道。
3. **骡的宫殿**：把酒送给大管家。他会给你离境通行证和奖杯陈列柜钥匙。
4. **荣耀大厅**：用钥匙打开玻璃柜，拿走 Visi-Sonor。
5. **返回海滨**：把 Visi-Sonor 交给马格尼菲科。他会跟随你，并成为后续解码的关键。
6. **7 号机库**：通行证让你进入机库。登上 *Bayta*，打开储物柜，拿走提灯、爆能枪和基金会证件。
7. **川陀**：在导航电脑上 `SET COURSE TO TRANTOR`，拉发射杆。在废墟上 `SEARCH RUBBLE` 找到图书馆入口。提灯必须带在身上。
8. **帝国图书馆**：向管理员出示基金会证件，打开受限档案。读星图，获得“星之尽头 = 川陀”的线索。
9. **解码**：`USE VISI-SONOR ON MIS`。马格尼菲科演奏，米斯在音乐中说出第二基地的真相，同时获得塔曾达/罗森的坐标。
10. **罗森**：回到游艇，`SET COURSE TO ROSSEM`，拉发射杆。到村庄和长老交谈，然后东行到农舍。
11. **农舍**：最终场景自动触发。选择 `SHOOT MIS` 或 `SAY NOTHING`。

### 计分点（100 分）

| 事件 | 分数 |
|---|---:|
| 读卡尔甘日报 | 2 |
| 读蜜月行程表 | 2 |
| 贿赂大管家 | 5 |
| 取得 Visi-Sonor | 8 |
| 把 Visi-Sonor 交给马格尼菲科 | 10 |
| 设定川陀航线 | 8 |
| 逃离卡尔甘 | 8 |
| 找到图书馆入口 | 5 |
| 打开受限档案 | 8 |
| 阅读星图 | 4 |
| 用 Visi-Sonor 解码 | 10 |
| 设定罗森航线 | 5 |
| 抵达罗森 | 5 |
| 与罗森长老交谈 | 5 |
| 最终选择 | 15 |
| **合计** | **100** |

---

## 全流程 300 分

把三幕路线依次输入，或在项目目录运行：

```powershell
uv run python -m foundation_guide --script tests\walkthrough_full.txt --no-color
```

自动化测试中的“三幕连续通关”会验证：

- 第一幕 100/100
- 第二幕 100/100（信仰路线）
- 第三幕 100/100（安静的一枪）
- 总分 300/300
- 零死亡

---

## 彩蛋与额外内容

- `GUIDE` 中有 20 条条目，包括 `TOWEL`、`42`、`DON'T PANIC`、`THE MULE`、`VISI-SONOR` 等。部分条目需要和特定人物交谈或完成特定谜题才会解锁。
- 试试 `PANIC`、`FORTY TWO`、`XYZZY`、`TOWEL`。
- 在第二幕选择不同主义，会看到不同的结尾文字；第三幕的两种选择也各有独立的尾声。
- 游戏没有“必死”路线；即使死亡，指南也会把你送回上一回合。
