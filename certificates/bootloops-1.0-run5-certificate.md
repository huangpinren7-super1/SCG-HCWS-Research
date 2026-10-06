# SCG-HCWS 第一代云端计算基线：BootLoops 1.0 Acceptance Certificate

## 基线身份

- BootLoops：`66b680ce742e654cfe86da4f072a69061fe182b1` (BootLoops 1.0)
- SCG-HCWS-Research commit：`4c8c8b4574273438198073c55a66f2429de23d28`
- GitHub Actions：Run #5 / workflow `BootLoops Acceptance Battery`
- Workflow run ID：`37438820516`
- Runner：Ubuntu 24.04 / Python 3.11 / Julia 1.11
- Acceptance artifact：`11400509437` / SHA-256 `51363fd943d18b226df9848bd82c067520ff67d664f823bfb6389d5373656690`

## 总体结果

| 状态 | 数量 | 定义 |
|---|---:|---|
| PASS | 45 | canonical battery 正常返回 0 |
| REFUSED (by design) | 3 | data-gated 合约性拒绝，不计为 failure |
| FAIL | 1 | canonical battery 未通过，保留为真实失败 |
| **Total** | **49** | **全部 49 package 均有结果记录** |

## 失败项

`abacus`：`FAIL`，耗时约 300.1 s。其输出显示在 `[eichler] readying the julia project` 后触发 canonical runner 的 300 s timeout，并非一个明确的数学 assertion mismatch。按 BootLoops 的协议，该结果仍必须保留为 FAIL，直到重新验证通过。

## 合约性拒绝

- `ffcapital`：缺用户提供的 FireFly `ff_save/` reconstruction state。
- `frobenius-boundary`：缺 per-point Kira reduction table。
- `galois`：缺 campaign/reference bank。

## 49-package 状态表

| Package | Verification class | Status | Time (s) | 数学角色 | SCG/HCWS 优先级 |
|---|---|---|---:|---|---|
| `abacus` | selftest | **FAIL** | 300.1 | 算术几何/有限域点计数 | 间接 |
| `amflow-kit` | partial | **PASS** | 21.1 | AMFlow.cpp 结果门控、IBP cache/key 与内存围栏 | 物理计算基础设施 |
| `annihilator` | selftest | **PASS** | 166.4 | 精确级数 → P-finite 递推 / Picard–Fuchs θ-ODE | 核心 |
| `ansatzer` | selftest | **PASS** | 19.9 | 结构约束后剩余符号 Ansatz 维数预测 | 核心 |
| `baller` | partial | **PASS** | 21.4 | Arb/球算术式任意精度与数值卫生 | 核心 |
| `blade` | partial | **PASS** | 0.5 | 块三角 IBP、有限场/每点探针 | 物理计算基础设施 |
| `clinch` | partial | **PASS** | 1.0 | 区间 Newton 最优性/收敛证书 | 验证 |
| `coalescer` | selftest | **PASS** | 136.5 | Fuchsian 局部单值化与有限单值 Frobenius 分支投影 | 核心 |
| `cosmoflow` | selftest | **PASS** | 26.4 | 图上的 FRW/dS 积分核、Cayley–Menger/Baikov 多项式 | 高价值物理 |
| `counterweight` | selftest | **PASS** | 49.9 | Kira connection 的 ε-factorization / canonical form | 核心 |
| `dipstick` | selftest | **PASS** | 36.5 | PF/GKZ rank、count、cycle-type 预计算 triage；regions 完备性 | 核心 |
| `dogtag` | selftest | **PASS** | 275.5 | 积分族同构/拓扑/切签名一致性审计 | 核心 |
| `eichler` | partial | **PASS** | 7.1 | 镜映射、theta、genus-2 识别等精确算术引擎 | 数学基础 |
| `ellipticus` | selftest | **PASS** | 54.0 | 椭圆多对数/椭圆迭代积分的认证评估与 Gauss–Manin | 核心 |
| `emitall` | selftest | **PASS** | 6.5 | 从 receipt 重放主张数字，检测结果漂移 | 验证 |
| `eras` | selftest | **PASS** | 0.5 | 参数共享下的认证包络 + 对抗验证 | 核心 |
| `famhar` | selftest | **PASS** | 13.0 | 二维参数 dlog connection 的多 sheet 精确评估 | 核心 |
| `ffcapital` | data-gated | **REFUSED (by design)** | 1.9 | FireFly 死/截断运行状态的精确 salvage | 外部引擎 |
| `formglue` | partial | **PASS** | 0.9 | FORM 大表达式、迹、色代数、MZV 胶水层 | 物理计算基础设施 |
| `frobenius-boundary` | data-gated | **REFUSED (by design)** | 30.3 | var=∞ 的 Frobenius boundary / 非解析锚点 | 前沿数学 |
| `galois` | data-gated | **REFUSED (by design)** | 1.0 | motivic Galois coaction-cut 与精确 MZV relation ring | 前沿数学 |
| `gatekeeper` | selftest | **PASS** | 3.6 | 数据完整性、held-out CV、closure honesty gate | 核心验证 |
| `geotriage` | selftest | **PASS** | 4.9 | 最大切几何与 value-fittability triage | 核心 |
| `gpl-eval` | partial | **PASS** | 235.2 | 任意精度 GPL/HPL 评估与 basis consistency | 核心 |
| `holonomic` | partial | **PASS** | 0.1 | Arb 球算术认证的 D-finite/holonomic analytic continuation | 核心 |
| `kira-stack` | smoke | **PASS** | 0.4 | IBP 到 master + differential equations | 物理计算基础设施 |
| `landau-alphabet` | selftest | **PASS** | 8.4 | Landau 奇异面、symbol alphabet、dlog bootstrap | 核心 |
| `lockpick` | partial | **PASS** | 4.3 | PSLQ / integer relation / lattice fitting | 核心 |
| `longhand` | selftest | **PASS** | 42.0 | 独立高精度 Feynman-parametric ground truth | 核心 |
| `maxcut` | partial | **PASS** | 137.9 | 最大切几何、canonical UT rotation、maxcut DE | 核心 |
| `membound` | partial | **PASS** | 54.5 | 软区域边界常数与 Bessel-kernel frequency integrals | 高价值物理 |
| `mixalot` | selftest | **PASS** | 91.1 | 精确 Bayesian mixture evidence | 方法学 |
| `nestor` | selftest | **PASS** | 9.1 | 认证 quadrature、tanh-sinh、dispersion integration | 核心 |
| `numkin` | smoke | **PASS** | 2.6 | 多变量 FireFly/Kira 卡死时的 freeze-one-scale rescue | 物理计算基础设施 |
| `pmflow` | smoke | **PASS** | 1.9 | auxiliary-mass-flow 自洽积分族 CLI | 物理计算基础设施 |
| `popcorn` | selftest | **PASS** | 109.0 | certified population-genetics likelihood/SFS 与模拟 | 方法学 |
| `posq` | partial | **PASS** | 9.0 | 认证双侧 Bayesian evidence / Bayes factor quadrature | 方法学 |
| `qinvert` | selftest | **PASS** | 1.3 | 部分公开表上的 exact consistency certificate | 验证 |
| `rankscreen` | selftest | **PASS** | 4.8 | 多素数 rank / inconsistency over exact Q eliminations | 核心 |
| `ratfit` | partial | **PASS** | 2.9 | 精确 rational reconstruction、Thiele/Newton、CRT 高度诊断 | 核心 |
| `seedling` | partial | **PASS** | 32.1 | Kira pre-reduction predictive staging / family audit | 核心 |
| `subtropica` | partial | **PASS** | 8.6 | HyperFLINT/Tropical subtraction hyperlog integration | 高价值物理 |
| `surd` | partial | **PASS** | 5.0 | 含根式字母的 Cheng–Wu / hyperlog exact integration | 前沿数学 |
| `terrier` | partial | **PASS** | 82.1 | CY periods、lattice、string/F-theory census | 数学物理 |
| `tropical-sampler` | selftest | **PASS** | 22.8 | 热带重要性采样与 certified Gauss-Jacobi | 方法学 |
| `trust` | partial | **PASS** | 4.3 | 三条 disjoint lineage 的 reduction verification/receipt certificates | 核心验证 |
| `vopclose` | selftest | **PASS** | 3.2 | UT/graded 1-D path-DE 的 full-A function-level closure | 核心 |
| `wayfinder` | partial | **PASS** | 135.7 | ε-graded DE transport、Frobenius landing、dlog sampling | 核心 |
| `winnow` | partial | **PASS** | 3.5 | 升级 Laporta：有限域消元 + lambda witness receipts | 核心 |

## 第一轮数学分层结论

### I. 精确性与认证层

`baller → lockpick → rankscreen → ratfit → eras → nestor → longhand → trust → emitall → gatekeeper` 构成最重要的“数值候选 → 精确关系 → 证书 → 独立复算 → provenance”链。它对 SCG-HCWS 的价值最高，因为我们的目标不是得到一个 plausible number，而是得到可复核的结构性证据。

### II. 结构提取层

`annihilator → ansatzer → dipstick → coalescer → landau-alphabet → maxcut → vopclose → wayfinder → winnow` 对应从约束后的函数空间、微分方程、奇异结构、最大切到精确消元与闭包。这里最接近“理论命题 → 有限计算对象”的转化。

### III. 物理计算层

`kira-stack / blade / amflow-kit / numkin / pmflow / counterweight / gpl-eval / formglue / subtropica / surd / cosmoflow / membound` 是将抽象结构推到真实积分、DE、极限与高精度物理量的执行层。它们应被视为 SCG/HCWS 的计算后端，而不是理论公理。

### IV. 结构诚信与输入审计层

`dogtag / seedling / gatekeeper / emitall / qinvert / trust` 负责阻止“错误输入、错误拓扑、数据泄漏、receipt 漂移、还原结果伪装成证明”。这一层在正式研究中应与数学计算同等对待。

## 对 SCG-HCWS 的直接计算映射

| SCG-HCWS 研究动作 | 首选工具 |
|---|---|
| 精确固定点/代数对象的结构化编码 | `annihilator`, `ansatzer`, `winnow` |
| 中心/交换子/谱结构的候选闭包与消元 | `rankscreen`, `winnow`, `vopclose` |
| boundary obstruction / splitting–factorization 的反例构造 | `ratfit`, `rankscreen`, `gatekeeper`, `trust` |
| 有限尺寸数据的精确关系识别 | `lockpick`, `ratfit`, `baller` |
| 独立高精度数值复算 | `longhand`, `nestor`, `baller` |
| 奇异面/可观测结构与几何候选 | `landau-alphabet`, `geotriage`, `maxcut` |
| 结果证书、receipt、漂移检测 | `trust`, `emitall`, `gatekeeper` |

## 下一阶段

1. 单独修复 `abacus` 的 Julia/Eichler 300 s timeout，并作为“environmental FAIL”重新验收；在修复前不把它重分类为 PASS。
2. 以第一轮核心工具为计算底座，开始 SCG 当前数学缺口的最小可计算 benchmark：`center/rank/commutant → split/factorization → boundary obstruction → adversarial counterexample`。
3. 所有进入正式结论的数值均要求至少一条独立计算路线，并保留 receipt/artifact。

## Provenance

此证书由 GitHub Actions Run #5 的 canonical `selftest_results.json` 生成；原始 artifact 由 Workflow 上传并以 SHA-256 固定。状态分类沿用 BootLoops 自身的 verification classes 与 canonical runner 语义。
