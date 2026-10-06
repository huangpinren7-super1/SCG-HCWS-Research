# BootLoops 1.0：49-package 功能分析与 SCG-HCWS 映射（受限版）

> **科学状态：HYPOTHESIS / 尚未证明。**
>
> 本文描述的是“计算工具如何可能承载 SCG-HCWS 的有限计算对象”，不是 SCG-HCWS 定理，也不是工具能力已经得到数学验证的结论。正式研究前，必须先通过 `experiments/toolchain_truth/` 的真值植入门。

## 1. 计算层边界

BootLoops 在本项目中的正式角色固定为：

**计算验证层，而不是理论本体层。**

它可以提供精确消元、模素数 rank screen、关系重构、认证数值、微分方程/几何工具和 receipt/provenance，但这些工具的上游 GUIDE 语义不能被我们自行扩大。

尤其：

- `rankscreen` 是多素数 rank / inconsistency **screen**；closure 仍必须由 exact-Q solve 决定。
- `winnow` 是有限域 Laporta/IBP elimination library；可作为一般线性消元底层，但不是“中心/交换子定理证明器”。
- `vopclose` 是 **1-D path-DE closure** 工具；对有限维代数的 center/commutant 任务，正式映射应记录为 **NOT-APPLICABLE**，不能为了叙事而调用。

## 2. 真值植入门（正式研究前置条件）

`experiments/toolchain_truth/test_toolchain_truth.py` 构造两个已知答案的有限维对象：

| 对象 | 精确真值 |
|---|---|
| (M_2(mathbb Q)oplus M_3(mathbb Q)) 的定义表示 | (dim Z(A)=2)，(dim operatorname{Comm}_{operatorname{End}(mathbb Q^5)}(A)=2) |
| (mathbb Q[S_3]) 左正则表示 | (dim Z(mathbb Q[S_3])=3)，(dim operatorname{Comm}_{operatorname{End}(mathbb Q^6)}(mathbb Q[S_3])=6) |

测试同时：

1. 用独立 exact-Q Gaussian elimination 固定真值 rank；
2. 要求 `rankscreen` 在两个素数下复现相同 rank；
3. 要求 `winnow` 的有限域消元复现相同 rank/nullity；
4. 检查 `vopclose` 的 1-D path-DE scope guard 仍在。

任何一项失败，都意味着“工具链映射已被验证”的说法必须撤回。

## 3. 早期映射应如何表述

以下表格现在只表示**候选用途**，不能写成“已经同构”：

| SCG-HCWS 研究动作 | 候选计算组件 | 证据等级 |
|---|---|---|
| 有限代数对象的线性约束消元 | `rankscreen`, `winnow` | 待真值门确认 |
| 精确关系识别 | `lockpick`, `ratfit` | BootLoops 自带 gate；与 SCG 对象仍需独立验证 |
| 认证数值复算 | `baller`, `nestor`, `longhand` | 工具自身已有 gates；研究对象需独立复核 |
| DE / singularity / geometry 结构 | `annihilator`, `coalescer`, `landau-alphabet`, `maxcut`, `wayfinder` | 只能作候选结构提取 |
| receipt / reproducibility / adversarial checking | `trust`, `emitall`, `gatekeeper` | 作为证据层，不等于数学证明 |

## 4. 当前 Gap 方向的计算候选

### Gap 3：Boundary Obstruction / Splitting–Factorization

候选顺序仍可保留：

`rankscreen → winnow → ratfit → gatekeeper → trust`

但必须先在有限维已知对象上证明这些组件对所编码的线性问题给出预期答案，再进入真实的 split / non-split 对照。

### Gap 2：Center / sector decomposition

目标不是恢复被否掉的“(dim Z(A)<infty)”命题，而是计算有限有效对象的：

[
Z(A),quad 	ext{central-decomposition rank},quad
operatorname{Comm}(A),
]

并用明确的 exact-Q / modular cross-check 固定结果。

`vopclose` 不属于这一计算环节。

### Gap 1：GSR → categorical indecomposability

`ansatzer / annihilator / rankscreen` 可以把具体候选约束压成有限实例，但不能替代范畴论证明。其作用只能是 counterexample search、finite-model attack 和 consistency screening。

### Gap 4：Boundary dimension → area law

`dogtag / rankscreen / winnow / geotriage / maxcut` 只能提供边界数据、图结构和精确消元基础。面积律仍需要独立的 combinatorial / operator-theoretic theorem layer。

## 5. 正式研究的证据规则

进入 SCG-HCWS 正式结论的计算结果必须：

**有限对象定义 → planted truth / independent oracle → exact or certified computation → independent re-check → receipt/provenance**

其中“BootLoops package PASS”只证明该 package 的自身 acceptance contract，没有自动推出“它正确实现了 SCG-HCWS 所需数学语义”。

因此，在 `toolchain_truth` 首次绿色之前，本文不得继续使用“完全同构”“已验证中心/交换子求解器”等表述。
