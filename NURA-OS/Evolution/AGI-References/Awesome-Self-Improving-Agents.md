<h1 align="center">
  Awesome Self-Improving Modern Agentic Systems
</h1>

<p align="center">
  <strong>
    A curated and continuously evolving resource hub for self-improving agentic systems
  </strong>
  <br>
  <sub>
    This repository brings together
    📄 Papers · 📊 Benchmarks · ✍️ Blogs · 🎙️ Podcasts ·
    💬 Interviews · 🎥 Videos · 🧑‍🏫 Workshops & Courses
  </sub>
  <br>
  <sub>
    Contributions are welcome — open a PR to share relevant resources and help grow the community! 🌱
  </sub>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2607.13104">
    <img
      src="https://img.shields.io/badge/READ_THE_PAPER-arXiv%3A2607.13104-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white"
      alt="Read the paper"
    >
  </a>
  <a href="https://huggingface.co/papers/2607.13104">
    <img
      src="https://img.shields.io/badge/HUGGING_FACE-Daily_Papers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=FFD21E"
      alt="Hugging Face Daily Papers"
    >
  </a>
  <a href="https://selfimproving-agent.github.io/">
    <img
      src="https://img.shields.io/badge/PROJECT_PAGE-Explore-1D4ED8?style=for-the-badge&logo=googlechrome&logoColor=white"
      alt="Project page"
    >
  </a>
  <a href="#-key-literature">
    <img
      src="https://img.shields.io/badge/PAPER_LIST-Browse-0F766E?style=for-the-badge&logo=readthedocs&logoColor=white"
      alt="Paper list"
    >
  </a>
  <a href="https://discord.gg/fn5rYJhgaz">
    <img
      src="https://img.shields.io/badge/COMMUNITY-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"
      alt="Discord"
    >
  </a>
</p>

<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome">
  </a>
  <a href="LICENSE">
    <img
      src="https://img.shields.io/badge/License-MIT-F59E0B?labelColor=555555"
      alt="MIT License"
    >
  </a>
</p>

<p align="center">
  This repository accompanies
  <a href="https://arxiv.org/abs/2607.13104">
    <em>Self-Improvements in Modern Agentic Systems: A Survey</em>
  </a>.
</p>

---

## 🌐 Contents
- [Definition & Scope](#-definition--scope)
- [Survey Paper](#-survey-paper)
- [Taxonomy](#-taxonomy)
- [Key Literature](#-key-literature)
  - [🟦 Foundation Model Improvement](#-foundation-model-improvement)
  - [🟩 Scaffolding Improvement](#-scaffolding-improvement)
- [Evaluation & Benchmarking](#evaluation)
- [Related Resources](#-related-resources)
- [Contact & Community](#-contact--community)
- [Contribute](#-contribute)
- [Citation](#-citation)

---

## 🧩 Definition & Scope
This repository focuses on:
- **Foundation-Model-Based Agents**: Autonomous systems that use foundation models as cognitive cores and operate through persistent scaffolds such as prompts, memory, tools, and control logic.
- **Self-Improvement Loops**: Agent-level update loops in which signals or artifacts produced through generation, intrinsic evaluation, or environment interaction are consolidated into persistent components of the agent.
- **Foundation Model Improvement**: Parameter-level updates driven by intrinsic generative demonstrations, intrinsic evaluative feedback, or extrinsic exploratory experience.
- **Scaffolding Improvement**: Persistent updates to prompts, memory, tools, workflows, or full agent scaffolds.

---

## 📄 Survey Paper

|**[Self-Improvements in Modern Agentic Systems: A Survey](https://arxiv.org/abs/2607.13104)** | `arXiv:2607.13104` | [LaTeX source](./Paper/) | [Agent-oriented guide](./README_AGENT.md)|

<p align="center">
  <img src="assets/fig-si-main-001.png" alt="Main figure of the survey" width="95%">
  <br>
  <em>Overview of self-improvement mechanisms in foundation model–based agentic systems.</em>
</p>

---

## 🧭 Taxonomy

If you are not yet familiar with agents, this simple illustration shows how an **FM-based agent** differs from a standalone **foundation model** (e.g., an LLM).

<details open>
  <summary><strong>View the animated comparison</strong></summary>

  <br>

  <p align="center">
    <a href="assets/agentvsfm.gif">
      <img
        src="assets/agentvsfm.gif"
        alt="Animated comparison between a standalone foundation model and an agent"
        width="70%"
      >
    </a>
    <br>
    <em>
      An illustration of the distinction between a standalone foundation model and an FM-Based agent.
    </em>
  </p>
</details>

To ground our taxonomy, we first introduce a formal abstraction of a foundation model–based agent,
which serves as the basic unit for all self-improving agentic systems considered in this survey.

<p align="center">
  <img src="assets/agent_def.png" alt="Formal abstraction of an FM-based agent" width="55%">
  <br>
  <em>Formal abstraction of a foundation model–based agent, consisting of a foundation model and its scaffolding.</em>
</p>

Based on this abstraction, we categorize **self-improving agents** along two orthogonal axes,
depending on **which component is improved** during learning and adaptation.

* **🚀 Self-Improving Agents**
    * **🧠 Foundation Model Improvement**
        * 📄 `1.1` Intrinsic Generative Demonstrations
        * ⚖️ `1.2` Intrinsic Evaluative Feedback
        * 🌍 `1.3` Extrinsic Exploratory Experience
            * 🤖 `1.3.1` Interaction with Grounded Task Environments
            * 🔮 `1.3.2` Interaction with Simulated Proxy Environments
    * **🏗️ Scaffolding Improvement**
        * ✍️ `2.1` Prompt Optimization
        * 💾 `2.2` Memory
        * 🛠️ `2.3` Tool
        * ♾️ `2.4` Full Scaffolding

---

## 📚 Key Literature
### 🛣️ Evolution of Self-Improving Agents

<p align="center">
  <a href="assets/fig-si-rw-001.png">
    <img
      src="assets/fig-si-rw-001.png"
      alt="Timeline of representative self-improving agent systems"
      width="100%"
    >
  </a>
  <br>
  <em>
    Timeline of representative self-improving agent systems, organized by
    foundation model improvement and scaffolding improvement.
  </em>
</p>

### 🔖 Papers List

#### 🟦 Foundation Model Improvement

<details open>
<summary><b>1.1 Intrinsic Generative Demonstrations</b></summary>

  | 📅 Year | 📝 Title | 🏛️ Venue | 📄 Paper | 💻 Code |
  |------:|--------|--------|--------|--------|
  | 2023 | Self-Instruct: Aligning Language Models with Self-Generated Instructions | ACL | [paper](https://arxiv.org/abs/2212.10560) | [code](https://github.com/yizhongw/self-instruct) |
  | 2023 | Large Language Models Can Self-Improve | EMNLP | [paper](https://arxiv.org/abs/2210.11610) | N/A |
  | 2023 | Orca: Progressive Learning from Complex Explanation Traces of GPT-4 | arXiv | [paper](https://arxiv.org/abs/2306.02707) | [code]( https://aka.ms/orca-lm) |
  | 2024 | SELF: Self-Evolution with Language Feedback | arXiv | [paper](https://arxiv.org/abs/2310.00533) | N/A |
  | 2024 | SELF-GUIDE: Better Task-Specific Instruction Following via Self-Synthetic Finetuning | COLM | [paper](https://arxiv.org/abs/2407.12874) | [code](https://github.com/zhaochenyang20/Prompt2Model-Self-Guide) |
  | 2025 | Improving Model Alignment Through Collective Intelligence of Open-Source LLMS | ICML | [paper](https://arxiv.org/abs/2505.03059) | N/A |
  | 2025 | Superficial Self-Improved Reasoners Benefit from Model Merging | EMNLP | [paper](https://arxiv.org/abs/2503.02103) | [code](https://github.com/xiangchi-yuan/merge_syn) |
  | 2025 | Will Pre-Training Ever End? A First Step Toward Next-Generation Foundation MLLMs via Self-Improving Systematic Cognition | arXiv | [paper](https://arxiv.org/abs/2503.12303) | [code](https://github.com/thunlp/SICOG?tab=readme-ov-file) |
  | 2025 | TaskCraft: Automated Generation of Agentic Tasks | arXiv | [paper](https://arxiv.org/abs/2506.10055) | [code](https://github.com/OPPO-PersonalAI/TaskCraft) |
  | 2025 | Iterative Tool Usage Exploration for Multimodal Agents via Step-wise Preference Tuning | NeurIPS | [paper](https://arxiv.org/abs/2504.21561) | [code](https://github.com/SPORT-Agents/SPORT-Agents) |
  | 2025 | Maximizing Confidence Alone Improves Reasoning | arXiv | [paper](https://arxiv.org/abs/2505.22660) | [code](https://github.com/satrams/rent-rl) |
  | 2025 | DIVE: Diversified Iterative Self-Improvement | arXiv | [paper](https://arxiv.org/abs/2501.00747) | [code](https://github.com/qinyiwei/DIVE) |
  | 2025 | Self-Adapting Language Models | NeurIPS | [paper](https://arxiv.org/abs/2506.10943) | [code](https://github.com/Continual-Intelligence/SEAL) |
  | 2025 | First SFT, Second RL, Third UPT: Continual Improving Multi-Modal LLM Reasoning via Unsupervised Post-Training | NeurIPS | [paper](https://arxiv.org/pdf/2505.22453) | [code](https://github.com/waltonfuture/MM-UPT) |
  | 2025 | LADDER: Self-Improving LLMs Through Recursive Problem Decomposition | arXiv | [paper](https://arxiv.org/abs/2503.00735) | N/A |
  | 2025 | Self-Consistency Preference Optimization | ICML | [paper](https://arxiv.org/abs/2411.04109) | N/A |
  | 2025 | Adapting While Learning: Grounding LLMs for Scientific Problems with Tool Usage Adaptation | ICML | [paper](https://arxiv.org/abs/2411.00412) | [code](https://github.com/Rose-STL-Lab/Adapting-While-Learning) |
  | 2026 | Reinforcing General Reasoning Without Verifiers | ICLR | [paper](https://arxiv.org/abs/2505.21493) | [code](https://github.com/sail-sg/VeriFree) |
  | 2026 | SAGE: Multi-Agent Self-Evolution for LLM Reasoning | arXiv | [paper](https://arxiv.org/abs/2603.15255) | N/A |
  | 2026 | ANDES: Agent Native Data Evolving Synthesis Tool for Autonomous Instruction Alignment | arXiv | [paper](https://arxiv.org/abs/2606.01279) | [code](https://github.com/zzy1127/ANDES) |
  | 2026 | EvoGround: Self-Evolving Video Agents for Video Temporal Grounding | arXiv | [paper](https://arxiv.org/abs/2605.13803) | [code](https://github.com/minjoong507/EvoGround) |

</details>

<details open>
<summary><b>1.2 Intrinsic Evaluative Feedback</b></summary>

  | 📅 Year | 📝 Title | 🏛️ Venue | 📄 Paper | 💻 Code |
  |------:|--------|--------|--------|--------|
  | 2022 | Constitutional AI: Harmlessness from AI Feedback | arXiv | [paper](https://arxiv.org/abs/2212.08073) | [code](https://github.com/anthropics/ConstitutionalHarmlessnessPaper?tab=readme-ov-file) |
  | 2023 | ReST meets ReAct: Self-Improvement for Multi-Step Reasoning LLM Agent | arXiv | [paper](https://arxiv.org/abs/2312.10003) | N/A |
  | 2025 | STRIVE: Structured Reasoning for Self-Improvement in Claim Verification | MIR | [paper](https://arxiv.org/abs/2502.11959) | N/A |
  | 2025 | Beyond Accuracy: The Role of Calibration in Self-Improving Large Language Models | arXiv | [paper](https://arxiv.org/abs/2504.02902) | N/A |
  | 2025 | Self-Evolved Reward Learning for LLMs | ICLR | [paper](https://arxiv.org/abs/2411.00418) | [code](https://github.com/microsoft/DKI_LLM/tree/main/SER) |
  | 2025 | Sample, Predict, then Proceed: Self-Verification Sampling for Tool Use of LLMs | arXiv | [paper](https://arxiv.org/abs/2506.02918v1) | N/A |
  | 2025 | RLSR: Reinforcement Learning from Self Reward | arXiv | [paper](https://arxiv.org/abs/2505.08827) | N/A |
  | 2025 | Right Question is Already Half the Answer: Fully Unsupervised LLM Reasoning Incentivization | NeurIPS | [paper](https://arxiv.org/abs/2504.05812) | [code](https://github.com/QingyangZhang/EMPO) |
  | 2025 | TTRL: Test-Time Reinforcement Learning | NeurIPS | [paper](https://arxiv.org/abs/2504.16084) | [code](https://github.com/PRIME-RL/TTRL) |
  | 2025 | Can Large Reasoning Models Self-Train? | arXiv | [paper](https://arxiv.org/abs/2505.21444) | [code](https://github.com/tajwarfahim/srt) |
  | 2025 | Self Rewarding Self Improving | arXiv | [paper](https://arxiv.org/abs/2505.08827v1) | N/A |
  | 2025 | Self-Evolving Curriculum for LLM Reasoning | arXiv | [paper](https://arxiv.org/abs/2505.14970) | [code](https://github.com/ServiceNow/sec) |
  | 2025 | Reflect, Retry, Reward: Self-Improving LLMs via Reinforcement Learning | arXiv | [paper](https://arxiv.org/abs/2505.24726) | N/A |
  | 2025 | Adaptive Self-improvement LLM Agentic System for ML Library Development | ICML | [pa