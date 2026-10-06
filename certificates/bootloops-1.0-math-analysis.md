# BootLoops 1.0：49-package 数学功能分析与 SCG-HCWS 映射

## 1. 基线

本分析对应 SCG-HCWS 第一代云端计算基线：

- BootLoops 1.0：66b680ce742e654cfe86da4f072a69061fe182b1
- GitHub Actions Run #5：37438820516
- 结果：45 PASS / 3 REFUSED (by design) / 1 FAIL / 共 49 package
- 唯一 FAIL：abacus，300.1 s timeout，停在 Eichler Julia project readying；不显示直接数学 assertion mismatch。
- artifact：11400509437
- artifact SHA-256：51363fd943d18b226df9848bd82c067520ff67d664f823bfb6389d5373656690

因此第一代 baseline 的“科学可运行率”应报告为：
- 全体：45/49 PASS = 91.8%
- 实际执行项（排除 3 个合同性 data-gated refusal）：45/46 = 97.8%
- 1 个待修复 environmental/runtime FAIL。

## 2. 五层数学结构

### Layer A — 精确代数、消元与关系识别

核心 package：

annihilator, ansatzer, dipstick, lockpick, rankscreen, ratfit, seedling, vopclose, winnow。

共同任务是把“候选结构”压缩成有限、可审计、可重复的代数对象：

- annihilator：由精确序列恢复最小 P-finite recurrence / Picard–Fuchs θ-operator；适合把数列型证据提升为有限阶微分方程。
- ansatzer：在结构 cuts 后计算 residual symbol-ansatz dimension；它回答“还剩多少自由度”，不是回答最终函数是什么。
- dipstick：在昂贵计算前先判断 PF/GKZ rank、cycle-type 与 completeness；适合把“不值得算”的问题提前拒绝。
- lockpick：PSLQ / LLL / BKZ / integer relation；负责从高精度候选值恢复精确关系，但不替代独立验证。
- rankscreen：多素数一致的 rank / pivot / inconsistency 屏幕；可快速给出 refutation 与 exact-Q solve 的受控入口。
- ratfit：Thiele/Newton/mod-p/CRT rational reconstruction；适合从有限采样恢复有理函数或识别高度增长异常。
- seedling：在 Kira/IBP 前做 family audit、symmetry audit 与 staging。
- vopclose：对 UT/graded 1-D path-DE 做 function-level closure。
- winnow：有限域消元 + lambda-witness receipt，是最接近“精确线性约束系统 → 证书”的底层执行器之一。

### Layer B — 认证数值与独立 oracle

核心 package：

baller, eras, nestor, longhand, ellipticus, gpl-eval, clinch。

共同原则是：数值结果必须携带误差/包络/独立路线，而不是只给一个浮点数。

- baller：Arb/ball front door、自动精度升级、fail-closed digit printing。
- eras：针对共享参数造成的 interval dependency，给出 remainder-aware enclosure；特别适合“同一个参数大量重复进入乘积”的稳定性证明。
- nestor：认证 tanh-sinh / dispersion quadrature。
- longhand：独立于 DE/AMFlow 等快方法的数值 ground truth；最重要的独立 oracle。
- ellipticus：椭圆多对数与 Gauss–Manin 高精度认证值。
- gpl-eval：任意精度 GPL/HPL evaluator。
- clinch：interval-Newton/局部最优性证书。

### Layer C — 微分方程、几何与奇异结构

核心 package：

coalescer, famhar, landau-alphabet, maxcut, geotriage, wayfinder, cosmoflow, membound。

它们把“函数”提升为其结构载体：

- coalescer：局部 monodromy 的谱投影与 Frobenius 分支系数。
- famhar：多 sheet connection 的统一 evaluator。
- landau-alphabet：奇异面与 symbol alphabet；适合把可计算对象的奇异结构显式化。
- maxcut：最大切几何、UT rotation、maxcut DE。
- geotriage：判断最大切几何是否足以支持稳定 value-fit。
- wayfinder：ε-graded transport、Frobenius landing 与 dlog connection。
- cosmoflow：图上的 FRW/dS integrand 与 Cayley–Menger/Baikov。
- membound：软区域与 boundary constants。

### Layer D — 物理计算后端

amflow-kit, blade, kira-stack, counterweight, formglue, numkin, pmflow, subtropica, surd, terrier。

这一层不应被当成 SCG 公理层，而应被当成“理论对象被映射到具体物理积分/DE 后的执行引擎”。

特别是：
kira-stack / blade / amflow-kit 提供 IBP/积分计算；
counterweight 提供 ε-factorization；
formglue 处理大表达式；
numkin/pmflow 用于多尺度与 auxiliary-mass flow；
subtropica/surd 处理超对数与根式字母；
terrier 负责 CY/string/F-theory 一类特殊数学物理对象。

### Layer E — 证据完整性与反作弊层

dogtag, seedling, gatekeeper, trust, emitall, qinvert。

这一层在 SCG-HCWS 中不是“辅助工具”，而是证明链的一部分：

输入拓扑错了，后面的计算再漂亮也无效；
value-fit 没有 held-out / independent oracle，不能闭合；
receipt 漂移了，旧结果不能继续作为证据；
部分公开数据若不一致，必须返回 exact consistency certificate。

## 3. SCG-HCWS 最重要的工具链

### Gap 3：Boundary Obstruction / Splitting–Factorization

当前第一优先级：

rankscreen → winnow → ratfit → ansatzer → gatekeeper → trust

对应的数学动作是：

1. 用有限维结构常数/矩阵表示对象；
2. 用 rankscreen 做多素数 rank / inconsistency screen；
3. 用 winnow 完成 exact-Q elimination 并留下 witness；
4. 用 ratfit / lockpick 从采样数据识别候选结构常数或参数关系；
5. 用 gatekeeper / trust 对 closure 与 receipt 做独立验证；
6. 对 split / factorization 与 non-split obstruction 做对抗性对照。

这正对应当前“两通道 / splitting–factorization contrapositive”路线。

### Gap 2：Center / sector decomposition

第一优先级：

rankscreen → winnow → vopclose → gatekeeper

目标不是简单计算 dim Z(A)，而是对有限有效结构计算：

Z(A), center decomposition rank, commutant, connected/irreducible blocks。

这与 SCG 当前已经冻结的“sector / central decomposition rank”版本一致；尤其要避免重新使用无限维场景下错误的 dim Z(A)<∞ 命题。

### Gap 1：GSR → categorical indecomposability

第一优先级：

ansatzer → annihilator → vopclose → rankscreen

这些工具不能代替范畴论证明，但可以把候选生成规则、递推关系、残余自由度和闭包条件压成有限计算实例，用于 DComp/DDGSR 的 counterexample / finite-model 攻击。

### Gap 4：Boundary dimension → area law

第一优先级：

dogtag → rankscreen → winnow → geotriage / maxcut

这里需要谨慎：BootLoops 没有现成“area law theorem prover”。它提供的是边界数据、图结构、精确消元与结构验证能力；面积律本身仍需要我们自己的 combinatorial / operator-theoretic theorem layer。

## 4. 第一击：GAP3-TwoChannel 最小计算实验

建立最小 finite-effective benchmark，对照至少三类对象：

- split control：已有 section，obstruction class 应为 0；
- non-split control：section 不存在，候选 obstruction class 应非零；
- tensor-factorizing control：验证 CNI + PCL 并不自动排除 factorization。

对每个对象计算：

Z(E), boundary algebra, bulk ideal, commutants,
split-section existence,
factorization test,
obstruction cocycle/class。

计算协议：

- exact-Q：SymPy / FLINT；
- mod-p：rankscreen / winnow；
- reconstruction：ratfit / lockpick；
- independent numeric cross-check：baller；
- adversarial certificate：gatekeeper / trust；
- reproducibility：emitall。

关键判据不是“某个数看起来不同”，而是：

split ⇒ factorization

以及反向：

global non-factorizable ⇒ no split section ⇒ nonzero obstruction class。

这一步直接攻击当前 Gap 3 的逻辑桥，而不是再增加一个周边定义。

## 5. 第一轮 49-package 分析的总判断

最有价值的不是某一个 package，而是以下组合：

exact elimination
→ structural extraction
→ certified numerics
→ independent oracle
→ evidence receipt

即：

rankscreen / winnow
→ annihilator / ansatzer / vopclose
→ baller / eras / nestor
→ longhand
→ trust / gatekeeper / emitall。

这条链与 SCG-HCWS 当前研究方法完全同构：

理论命题
→ 有限有效对象
→ 精确约束
→ 候选结构
→ 独立反例/复算
→ certificate。

因此，BootLoops 在本项目中的正确角色已经可以正式固定为：

**计算验证层，而不是理论本体层。**

