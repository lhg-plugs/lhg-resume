# 灵感来源与致谢（Attribution）

本插件的**方法论灵感**来自以下开源项目，**所有实现代码、检测规则与文案均为原创**，
未复制任何第三方的原文案与代码。核实日期：2026-10-11。

| 项目 | 作者 | 许可（2026-10-11 核实） | 链接 | 借鉴了什么思路 |
|---|---|---|---|---|
| ResumeSkills | Param Choudhary | MIT（2,510 stars） | https://github.com/Paramchoudhary/ResumeSkills | "ATS 优化 / bullet 量化 / JD 匹配 / 面试准备"的流程划分思路；本插件的命令与 skill 切分受其启发，**文案与规则全部原创** |
| cv-creator | Faraz Fookeer | MIT（2 stars） | https://github.com/farazfookeer/cv-creator | "action-verb + quantified-result"的 bullet 改写 rubric 思路；本插件动词库与量化公式为独立撰写 |
| master-resume-skill | vbalashi | 未声明（仓库无 LICENSE 文件，核实时 0 stars） | https://github.com/vbalashi/master-resume-skill | 仅借鉴"先审计经历真实性、再生成简历"的通用流程思想；因其许可未声明，**未参考其任何具体文案、模板与代码** |

## 声明

1. **借鉴思路，实现与文案均为原创**：以上项目的具体文案、规则原文、代码实现均未被复制。
   本插件的 skill 方法论文案、审计规则、命令流程、动词库均为独立撰写。
2. **许可合规**：ResumeSkills 与 cv-creator 均为 MIT 许可，允许在保留声明的前提下进行思路借鉴与二次创作，
   本文件即为保留声明的一部分。master-resume-skill 因许可未声明，仅借鉴不受著作权保护的通用方法论思想，
   未使用其任何表达性内容。
3. **商标与归属**：各项目名称与作者署名归其各自所有者所有。
4. **诚实声明**：本插件不编造"已验证"的数据；README 与 skill 中的数字（如规则条数）均为本仓库实际可数的，
   欢迎用 `smoke_test.py` 验证。

## 本插件自身的许可

本插件原创部分采用 MIT 许可（见 `LICENSE` 文件），版权所有：刘洪光（https://github.com/lhg-skills）。
