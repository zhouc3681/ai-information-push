const dailyMeta = {
  dateLabel: "2026-05-30",
  generatedAt: "09:10",
  windowLabel: "近 72 小时",
  nextRun: "18:00",
  dashboardUrl: window.location.href.split("?")[0]
};

let sources = [
  {
    id: "openai-release-0528",
    org: "OpenAI",
    product: "ChatGPT Workspace Agents、Codex、App Templates",
    date: "2026-05-28",
    freshness: "近 48 小时",
    title: "ChatGPT Enterprise & Edu 发布说明：Workspace Agents、应用模板和 Codex 管理能力更新",
    type: "官方发布说明",
    url: "https://help.openai.com/en/articles/10128477-chatgpt-enterprise-i-edu-informacje-o-wersjach",
    summary: "OpenAI 更新企业/Edu 工作区能力：Workspace Agents 支持 GPT-5.5、角色化发布权限、引导式创建、语音输出；GitHub Enterprise、Snowflake、Databricks 应用模板进入企业配置流；Codex 增加目标模式、远程使用、管理员分析和插件分享状态。"
  },
  {
    id: "openai-workspace-agents",
    org: "OpenAI",
    product: "Workspace Agents",
    date: "2026-04-22",
    freshness: "本月延续",
    title: "OpenAI 发布 Workspace Agents：团队级 Agent 可在 ChatGPT 和 Slack 中共享使用",
    type: "官方文章",
    url: "https://openai.com/index/introducing-workspace-agents-in-chatgpt/",
    summary: "Workspace Agents 由 Codex 驱动，可运行在云端、连接工具、按团队流程执行任务，并支持企业级监控、权限和 Compliance API。"
  },
  {
    id: "openai-enterprise-phase",
    org: "OpenAI",
    product: "Frontier、企业 Agent 基础层",
    date: "2026-04-30",
    freshness: "本月延续",
    title: "OpenAI：企业 AI 进入下一阶段，Agent 需要跨系统运行并被统一治理",
    type: "官方文章",
    url: "https://openai.com/index/next-phase-of-enterprise-ai/",
    summary: "OpenAI 将企业策略描述为统一 AI superapp 与 Frontier agent 基础层，强调 Agent 需要接入企业系统、数据和权限控制。"
  },
  {
    id: "servicenow-knowledge-2026",
    org: "ServiceNow",
    product: "AI Control Tower、AI Specialists、Action Fabric",
    date: "2026-05-05",
    freshness: "本月关键更新",
    title: "ServiceNow Knowledge 2026：把企业 AI 混乱纳入治理和自动化控制",
    type: "官方新闻稿",
    url: "https://newsroom.servicenow.com/press-releases/details/2026/ServiceNow-turns-enterprise-AI-chaos-into-control-with-the-platform-for-governed-autonomous-work/default.aspx",
    summary: "ServiceNow 强调 AI Control Tower、AI Specialists、Action Fabric 和 Microsoft Agent 365 生态治理，定位为企业 AI 和 Agent 的控制塔。"
  },
  {
    id: "servicenow-microsoft-2026",
    org: "ServiceNow / Microsoft",
    product: "AI Control Tower、Microsoft Agent 365",
    date: "2026-05-05",
    freshness: "本月关键更新",
    title: "ServiceNow 扩展与 Microsoft 的 Agent 治理集成",
    type: "官方新闻稿",
    url: "https://investor.servicenow.com/news/news-details/2026/ServiceNow-expands-AI-agent-governance-through-deeper-integration-with-Microsoft/default.aspx",
    summary: "ServiceNow 宣布把 AI Control Tower 能力扩展到 Microsoft Agent 365 生态，用于发现、观测、治理和度量企业内 AI Agent。"
  },
  {
    id: "workspace-bench",
    org: "arXiv / 清华大学等研究团队",
    product: "Workspace-Bench 1.0",
    date: "2026-05-14",
    freshness: "近两周研究",
    title: "Workspace-Bench 1.0：评测 Agent 在复杂办公空间中的真实任务能力",
    type: "研究论文",
    url: "https://arxiv.org/abs/2605.03596",
    summary: "研究构建 5 类用户、74 种文件类型、20,476 个文件和 388 个任务；当前 Agent 在 workspace learning 上仍明显低于人类表现。"
  },
  {
    id: "m365-copilot-chat",
    org: "Microsoft Research / arXiv",
    product: "M365 Copilot Chat",
    date: "2026-05-11",
    freshness: "近两周研究",
    title: "AI in the Enterprise：基于 550 万次会话分析企业如何使用 M365 Copilot Chat",
    type: "研究论文",
    url: "https://arxiv.org/abs/2605.23958",
    summary: "论文显示企业 Copilot 使用正在从“搜索式问答”转向写作、沟通、分析、决策和系统诊断等工作活动。"
  },
  {
    id: "mcp-tools",
    org: "arXiv / Merlin Stein",
    product: "MCP Tool Usage Study",
    date: "2026-03-25",
    freshness: "风险背景",
    title: "How are AI agents used? 基于 177,436 个 MCP 工具观察 Agent 工具层风险",
    type: "研究论文",
    url: "https://arxiv.org/abs/2603.23802",
    summary: "研究发现 action tools 占比快速上升，Agent 正在从读取信息走向修改文件、发送邮件、交易等更高影响动作。"
  }
];

let briefItems = [
  {
    title: "OpenAI 5 月 28 日更新把 Workspace Agents 推向“可管理的团队代理”",
    summary:
      "OpenAI 企业/Edu 发布说明显示，Workspace Agents 新增 GPT-5.5、推理强度控制、角色化发布权限、引导式设置和语音输出；同时 GitHub Enterprise、Snowflake、Databricks 应用模板进入管理员配置流程，Codex 也增加目标模式、远程使用和管理员分析。",
    whyNow:
      "这是最近 48 小时内最值得企业关注的信号：Agent 不再只是个人 GPT，而是进入团队目录、权限、应用模板、审计和使用分析。",
    action:
      "建议产品和 IT 团队把“谁能创建、谁能发布、Agent 能访问哪些应用、哪些动作必须人工确认”写成试点规则，再决定是否开放给业务团队。",
    sourceIds: ["openai-release-0528", "openai-workspace-agents"],
    importanceScore: 99
  },
  {
    title: "ServiceNow 正在把 AI Control Tower 做成跨平台 Agent 治理层",
    summary:
      "ServiceNow 在 Knowledge 2026 期间强调 AI Control Tower、AI Specialists、Action Fabric，并宣布把治理扩展到 Microsoft Agent 365 生态。它的叙事不是“再造一个 Agent”，而是发现、观测、治理和度量企业里不断扩散的 Agent。",
    whyNow:
      "这对大中型企业很现实：一旦业务团队开始自己建 Agent，IT 面临的不是模型选择问题，而是影子 Agent、权限外溢、执行留痕和跨系统责任边界。",
    action:
      "建议把 Agent PoC 从第一天就纳入治理清单：Agent 身份、数据范围、触发条件、人工接管、执行日志和停用机制必须同步设计。",
    sourceIds: ["servicenow-knowledge-2026", "servicenow-microsoft-2026"],
    importanceScore: 96
  },
  {
    title: "5 月中旬研究开始给企业 Agent 降温：办公空间任务仍远未可靠",
    summary:
      "Workspace-Bench 1.0 构造真实办公空间中的大量文件依赖任务，结果显示当前 Agent 在 workspace learning 上仍明显低于人类。同期 M365 Copilot Chat 研究显示企业用户正在从“把 AI 当搜索”转向写作、分析、沟通和决策支持。",
    whyNow:
      "这两类研究放在一起看，结论很清楚：企业确实在把 AI 用到日常工作里，但复杂办公任务还不能只靠演示效果判断成熟度。",
    action:
      "建议 PoC 不只看能否完成单次任务，还要测跨文件依赖、历史上下文、错误恢复、人工复核和最终可交付质量。",
    sourceIds: ["workspace-bench", "m365-copilot-chat"],
    importanceScore: 91
  },
  {
    title: "MCP 工具层风险值得纳入 Agent 上线门槛",
    summary:
      "基于 177,436 个 MCP 工具的研究显示，Agent 工具正在从读数据转向执行动作，包括文件修改、邮件发送、甚至更高影响的外部操作。",
    whyNow:
      "企业接入 MCP 或类似工具协议时，真正的风险不只在模型输出，而在工具能否改变外部环境。",
    action:
      "建议所有工具调用分级：只读工具默认开放，写入/发送/交易类工具必须加审批、回滚、日志和异常熔断。",
    sourceIds: ["mcp-tools"],
    importanceScore: 86
  }
];

let pushSkillSteps = [
  {
    name: "简报生成 Skill",
    status: "已完成",
    description: "将入选信息压缩为企业微信、飞书和邮件均可阅读的正文。"
  },
  {
    name: "渠道适配 Skill",
    status: "已完成",
    description: "自动生成纯文字、群机器人卡片和 Dashboard 链接三种格式。"
  },
  {
    name: "邮箱推送 Skill",
    status: "待接入",
    description: "正式版连接企业 SMTP、SendGrid 或飞书邮箱服务。"
  },
  {
    name: "企微/飞书推送 Skill",
    status: "待接入",
    description: "正式版调用群机器人 Webhook，推送摘要和 Dashboard 链接。"
  }
];

const defaultSkills = [
  {
    name: "资讯采集 Skill",
    status: "运行中",
    description: "按时间窗口采集官方发布、研究论文、产品更新和行业新闻",
    input: "来源列表、关键词、时间窗口",
    output: "候选信息",
    owner: "情报组",
    calls: 1480
  },
  {
    name: "信息去重 Skill",
    status: "运行中",
    description: "识别不同来源对同一事件的重复报道",
    input: "候选信息",
    output: "事件簇",
    owner: "算法组",
    calls: 920
  },
  {
    name: "信息筛选 Skill",
    status: "运行中",
    description: "过滤泛新闻、营销稿和低企业相关内容",
    input: "事件簇",
    output: "入选候选",
    owner: "算法组",
    calls: 880
  },
  {
    name: "重要性评分 Skill",
    status: "运行中",
    description: "只作为后台排序和入选依据，不在正文显示",
    input: "入选候选",
    output: "内部排序信号",
    owner: "算法组",
    calls: 860
  },
  {
    name: "简报生成 Skill",
    status: "运行中",
    description: "生成今日摘要、企业含义、建议动作和原文链接",
    input: "排序结果、来源链接",
    output: "中文简报",
    owner: "产品组",
    calls: 520
  },
  {
    name: "渠道适配 Skill",
    status: "运行中",
    description: "将同一份简报转成邮件、企业微信和飞书格式",
    input: "中文简报、渠道规则",
    output: "推送正文、卡片文案、链接摘要",
    owner: "产品组",
    calls: 340
  },
  {
    name: "邮箱推送 Skill",
    status: "待接入",
    description: "通过企业邮箱或 SMTP 发送文字简报和 Dashboard 链接",
    input: "收件人、主题、正文、链接",
    output: "邮件发送结果",
    owner: "运维组",
    calls: 0
  },
  {
    name: "企业微信 / 飞书推送 Skill",
    status: "待接入",
    description: "调用群机器人 Webhook 推送摘要卡片",
    input: "Webhook、卡片文案、Dashboard 链接",
    output: "群消息发送结果",
    owner: "运维组",
    calls: 0
  }
];

let trends = [
  {
    name: "团队级 Workspace Agent",
    description: "OpenAI 5 月 28 日发布说明和 Workspace Agents 产品页显示，企业 Agent 正在进入团队共享、角色权限、应用模板和管理员可见性阶段。",
    sourceIds: ["openai-release-0528", "openai-workspace-agents"]
  },
  {
    name: "Agent 治理与控制塔",
    description: "ServiceNow 在 Knowledge 2026 后持续强化 AI Control Tower，并把治理扩展到 Microsoft Agent 365 生态。",
    sourceIds: ["servicenow-knowledge-2026", "servicenow-microsoft-2026"]
  },
  {
    name: "办公任务评测",
    description: "Workspace-Bench 和 M365 Copilot Chat 研究都说明，企业应从真实工作流、文件依赖和用户行为出发评估 Agent。",
    sourceIds: ["workspace-bench", "m365-copilot-chat"]
  },
  {
    name: "工具调用风险",
    description: "MCP 工具使用研究显示 action tools 占比上升，企业需要把工具权限、审批和日志当成 Agent 上线门槛。",
    sourceIds: ["mcp-tools"]
  }
];

let pocItems = [
  {
    title: "Workspace Agent 发布流程",
    reason: "OpenAI 最新更新把发布权限、应用模板和管理员可见性放到企业核心位置。",
    next: "先制定 Agent 创建、测试、发布、停用和审计规则，再让业务团队试点。"
  },
  {
    title: "AI Control Tower / Agent 台账",
    reason: "ServiceNow 与 Microsoft Agent 365 的方向说明，企业需要知道内部到底有哪些 Agent 在运行。",
    next: "建立 Agent 台账字段：负责人、数据权限、可执行动作、运行频率、日志位置、停用入口。"
  },
  {
    title: "办公空间任务评测",
    reason: "Workspace-Bench 暴露复杂文件依赖任务仍然不稳定，适合转化为内部评测集。",
    next: "从真实项目文件中抽取 20 个可脱敏任务，测试跨文件检索、推理和产出质量。"
  }
];

let agentItems = [
  {
    name: "OpenAI Workspace Agents / Codex",
    type: "团队工作流 Agent",
    description: "关注共享 Agent、应用模板、管理员分析、目标模式和远程执行。",
    sourceIds: ["openai-release-0528", "openai-workspace-agents"]
  },
  {
    name: "ServiceNow AI Control Tower",
    type: "Agent 治理层",
    description: "关注跨平台 Agent 发现、观测、治理、度量和 Microsoft Agent 365 集成。",
    sourceIds: ["servicenow-knowledge-2026", "servicenow-microsoft-2026"]
  },
  {
    name: "Workspace-Bench / M365 Copilot Chat",
    type: "研究评测线索",
    description: "关注企业办公任务评测、真实用户行为和 AI 从搜索到工作执行的迁移。",
    sourceIds: ["workspace-bench", "m365-copilot-chat"]
  }
];

let workflowSteps = [
  {
    name: "定时采集",
    count: "09:00 / 18:00",
    rate: "运行中",
    description: "按近 24/72 小时窗口抓取官方发布、研究论文和产品更新。"
  },
  {
    name: "来源核验",
    count: `${sources.length} 个来源`,
    rate: "运行中",
    description: "校验链接、发布时间、机构和产品名称。"
  },
  {
    name: "筛选排序",
    count: `${briefItems.length} 条入选`,
    rate: "运行中",
    description: "后台排序信号只决定先后，不在简报正文显示。"
  },
  {
    name: "渠道适配",
    count: "3 种格式",
    rate: "运行中",
    description: "生成邮件正文、企业微信/飞书卡片和 Dashboard 页面。"
  },
  {
    name: "推送交付",
    count: "待接入",
    rate: "待配置",
    description: "正式环境连接 SMTP 和飞书/企业微信 Webhook。"
  }
];

const state = {
  activeView: "brief",
  skillQuery: "",
  skills: []
};

const viewTitleMap = {
  brief: "今日简报",
  trends: "趋势与 PoC",
  skills: "Skill 中心",
  workflow: "Agent 工作流"
};

let sourceMap = new Map(sources.map((source) => [source.id, source]));
const isInternalMode = new URLSearchParams(window.location.search).get("internal") === "1";

const els = {
  viewTitle: document.querySelector("#viewTitle"),
  navItems: document.querySelectorAll(".nav-item"),
  internalOnly: document.querySelectorAll(".internal-only"),
  views: {
    brief: document.querySelector("#briefView"),
    trends: document.querySelector("#trendsView"),
    skills: document.querySelector("#skillsView"),
    workflow: document.querySelector("#workflowView")
  },
  briefContent: document.querySelector("#briefContent"),
  sourceGrid: document.querySelector("#sourceGrid"),
  todayNewMetric: document.querySelector("#todayNewMetric"),
  sourceCountMetric: document.querySelector("#sourceCountMetric"),
  copyBriefButton: document.querySelector("#copyBriefButton"),
  copyBriefTopButton: document.querySelector("#copyBriefTopButton"),
  copyStatus: document.querySelector("#copyStatus"),
  sourceButton: document.querySelector("#sourceButton"),
  emailBriefTopButton: document.querySelector("#emailBriefTopButton"),
  emailInput: document.querySelector("#emailInput"),
  deliveryFormat: document.querySelector("#deliveryFormat"),
  emailButton: document.querySelector("#emailButton"),
  emailPreview: document.querySelector("#emailPreview"),
  pushStatusList: document.querySelector("#pushStatusList"),
  copyPushCardButton: document.querySelector("#copyPushCardButton"),
  trendList: document.querySelector("#trendList"),
  pocList: document.querySelector("#pocList"),
  agentGrid: document.querySelector("#agentGrid"),
  skillTableBody: document.querySelector("#skillTableBody"),
  skillSearchInput: document.querySelector("#skillSearchInput"),
  skillForm: document.querySelector("#skillForm"),
  resetSkillsButton: document.querySelector("#resetSkillsButton"),
  workflowList: document.querySelector("#workflowList")
};

function loadState() {
  const savedSkills = JSON.parse(localStorage.getItem("aiRadarSkills") || "null");
  state.skills = Array.isArray(savedSkills) ? savedSkills : [...defaultSkills];
}

async function loadLiveDashboardData() {
  try {
    let data = window.AI_NEWS_PUSH_DATA;
    if (!data) {
      const response = await fetch("./data/dashboard-news.json", { cache: "no-store" });
      if (!response.ok) return;
      data = await response.json();
    }

    if (data.meta) {
      Object.assign(dailyMeta, {
        dateLabel: data.meta.dateLabel || dailyMeta.dateLabel,
        generatedAt: data.meta.generatedAt || dailyMeta.generatedAt,
        windowLabel: data.meta.windowLabel || dailyMeta.windowLabel,
        nextRun: data.meta.nextRun || dailyMeta.nextRun
      });
    }
    if (Array.isArray(data.sources)) sources = data.sources;
    if (Array.isArray(data.briefItems)) briefItems = data.briefItems;
    if (Array.isArray(data.trends)) trends = data.trends;
    if (Array.isArray(data.pocItems)) pocItems = data.pocItems;
    if (Array.isArray(data.agentItems)) agentItems = data.agentItems;
    if (Array.isArray(data.pushSkillSteps)) pushSkillSteps = data.pushSkillSteps;
    if (Array.isArray(data.workflowSteps)) workflowSteps = data.workflowSteps;

    sourceMap = new Map(sources.map((source) => [source.id, source]));
    document.querySelector(".eyebrow").textContent =
      `${dailyMeta.dateLabel} ${dailyMeta.generatedAt} 真实采集 · ${dailyMeta.windowLabel}`;
  } catch (error) {
    // 直接打开 HTML 文件时可能无法 fetch 本地 JSON；保留内置示例数据。
  }
}

function persistSkills() {
  localStorage.setItem("aiRadarSkills", JSON.stringify(state.skills));
}

function getSortedBriefItems() {
  return [...briefItems].sort((a, b) => b.importanceScore - a.importanceScore);
}

function getSourceDetails(ids) {
  return ids
    .map((id) => sourceMap.get(id))
    .filter(Boolean)
    .map((source) => {
      const originalUrl = source.originalUrl || source.url || "";
      const officialUrl = source.officialUrl || source.homepageUrl || originalUrl;
      return { ...source, originalUrl, officialUrl };
    });
}

function renderPlainUrl(label, value) {
  return `<div class="plain-url-row"><span>${label}</span><code>${value || "未提供"}</code></div>`;
}

function getSourceLinks(ids) {
  return getSourceDetails(ids)
    .map(
      (source) => `
        <div class="permanent-link-block">
          <div><strong>${source.org}：${source.product}</strong></div>
          ${renderPlainUrl("原文链接", source.originalUrl)}
          ${renderPlainUrl("官网链接", source.officialUrl)}
          ${source.originalUrl ? `<a href="${source.originalUrl}" target="_blank" rel="noopener noreferrer">打开原文</a>` : ""}
        </div>
      `
    )
    .join("");
}

function getSourceText(ids) {
  return getSourceDetails(ids)
    .map((source) =>
      [
        `来源：${source.org}`,
        `项目/产品：${source.product}`,
        `日期：${source.date}`,
        `原文链接：${source.originalUrl || "未提供"}`,
        `官网链接：${source.officialUrl || "未提供"}`
      ].join("\n")
    )
    .join("\n");
}

function renderBrief() {
  const sortedItems = getSortedBriefItems();
  const intro = `本期简报由 ${dailyMeta.generatedAt} 自动生成，数据窗口为${dailyMeta.windowLabel}。今天的核心变化不是“又发布了一个 Agent”，而是企业 Agent 正在进入团队共享、角色权限、应用模板、控制塔治理和真实办公任务评测阶段。`;

  els.briefContent.innerHTML = `
    <article class="brief-card lead-card">
      <span class="section-kicker">今日摘要</span>
      <h3>近 72 小时最值得企业关注的 AI / Agent 变化</h3>
      <p>${intro}</p>
    </article>
    ${sortedItems
      .map(
        (item, index) => `
          <article class="brief-card">
            <div class="brief-card-index">${index + 1}</div>
            <h3>${item.title}</h3>
            <div class="brief-point first-point">
              <span>项目名称</span>
              <p>${item.projectName || item.title}</p>
            </div>
            <div class="brief-point">
              <span>一句话介绍</span>
              <p>${item.summary}</p>
            </div>
            <div class="brief-point">
              <span>推荐理由</span>
              <p>${item.whyNow}</p>
            </div>
            <div class="brief-point">
              <span>建议动作</span>
              <p>${item.action}</p>
            </div>
            <div class="brief-links">
              <span>永久可复制链接</span>
              <div>${getSourceLinks(item.sourceIds)}</div>
            </div>
          </article>
        `
      )
      .join("")}
  `;

  els.todayNewMetric.textContent = briefItems.length;
  els.sourceCountMetric.textContent = sources.length;
}

function renderSources() {
  els.sourceGrid.innerHTML = sources
    .map(
      (source) => `
        <article class="source-card">
          <div class="source-card-top">
            <span class="tag">${source.type}</span>
            <span>${source.date}</span>
          </div>
          <h4>${source.title}</h4>
          <div class="source-field">
            <span>项目名称</span>
            <p>${source.product || source.title}</p>
          </div>
          <div class="source-field">
            <span>一句话介绍</span>
            <p>${source.summary || "暂无摘要，请打开原文查看。"}</p>
          </div>
          <div class="source-field">
            <span>来源</span>
            <p>${source.org}</p>
          </div>
          <div class="source-field">
            <span>推荐理由</span>
            <p>${source.reason || "该资讯进入本次实时采集窗口，并与企业 AI / Agent 方向相关。"}</p>
          </div>
          <div class="source-product">${source.org} · ${source.product}</div>
          <div class="source-url-list">
            ${renderPlainUrl("原文链接", source.originalUrl || source.url)}
            ${renderPlainUrl("官网链接", source.officialUrl || source.url)}
          </div>
          ${source.url ? `<a class="source-link" href="${source.url}" target="_blank" rel="noopener noreferrer">打开原文</a>` : ""}
        </article>
      `
    )
    .join("");
}

function renderPushStatus() {
  els.pushStatusList.innerHTML = pushSkillSteps
    .map(
      (step) => `
        <article class="push-step">
          <div>
            <strong>${step.name}</strong>
            <p>${step.description}</p>
          </div>
          <span class="status-pill ${getStatusClass(step.status === "已完成" ? "运行中" : "待配置")}">${step.status}</span>
        </article>
      `
    )
    .join("");
}

function renderTrends() {
  els.trendList.innerHTML = trends
    .map(
      (trend, index) => `
        <article class="trend-item">
          <div class="trend-item-top">
            <div class="trend-title">
              <span class="trend-rank">${index + 1}</span>
              <span>${trend.name}</span>
            </div>
          </div>
          <p>${trend.description}</p>
          <div class="brief-links compact-links">
            <span>参考来源</span>
            <div>${getSourceLinks(trend.sourceIds)}</div>
          </div>
        </article>
      `
    )
    .join("");

  els.pocList.innerHTML = pocItems
    .map(
      (item) => `
        <article class="poc-item">
          <div class="poc-item-top">
            <strong>${item.title}</strong>
          </div>
          <p>${item.reason}</p>
          <p><strong>下一步：</strong>${item.next}</p>
        </article>
      `
    )
    .join("");

  els.agentGrid.innerHTML = agentItems
    .map(
      (item) => `
        <article class="agent-card">
          <span class="tag">${item.type}</span>
          <h4>${item.name}</h4>
          <p>${item.description}</p>
          <div class="brief-links compact-links">
            <span>来源</span>
            <div>${getSourceLinks(item.sourceIds)}</div>
          </div>
        </article>
      `
    )
    .join("");
}

function getStatusClass(status) {
  if (status === "运行中") return "status-ok";
  if (status === "待配置" || status === "停用") return "status-wait";
  return "status-error";
}

function renderSkills() {
  const query = state.skillQuery.trim().toLowerCase();
  const skills = state.skills.filter((skill) =>
    [skill.name, skill.status, skill.description, skill.input, skill.output, skill.owner].join(" ").toLowerCase().includes(query)
  );

  els.skillTableBody.innerHTML = skills
    .map(
      (skill) => `
        <tr>
          <td class="skill-name">${skill.name}</td>
          <td><span class="status-pill ${getStatusClass(skill.status)}">${skill.status}</span></td>
          <td>${skill.description}</td>
          <td>${skill.input}</td>
          <td>${skill.output}</td>
          <td>${skill.owner}</td>
          <td>${skill.calls}</td>
        </tr>
      `
    )
    .join("");
}

function renderWorkflow() {
  els.workflowList.innerHTML = workflowSteps
    .map(
      (step) => `
        <article class="workflow-step">
          <div class="workflow-meta">
            <span>${step.count}</span>
            <span>${step.rate}</span>
          </div>
          <h4>${step.name}</h4>
          <p>${step.description}</p>
        </article>
      `
    )
    .join("");
}

function buildBriefText(includeDashboard = false) {
  const lines = [
    "【今日AI简报】",
    `生成时间：${dailyMeta.dateLabel} ${dailyMeta.generatedAt}`,
    `数据窗口：${dailyMeta.windowLabel}`,
    "",
    "今日摘要：企业 Agent 正在进入团队共享、角色权限、应用模板、控制塔治理和真实办公任务评测阶段。",
    ""
  ];

  getSortedBriefItems().forEach((item, index) => {
    lines.push(`${index + 1}. ${item.projectName || item.title}`);
    lines.push(`一句话介绍：${item.summary}`);
    lines.push(`推荐理由：${item.whyNow}`);
    lines.push(`建议动作：${item.action}`);
    lines.push("永久可复制链接：");
    lines.push(getSourceText(item.sourceIds));
    lines.push("");
  });

  lines.push("【建议今天安排】");
  pocItems.forEach((item, index) => {
    lines.push(`${index + 1}. ${item.title}：${item.next}`);
  });

  if (includeDashboard) {
    lines.push("");
    lines.push(`Dashboard 页面：${dailyMeta.dashboardUrl}`);
  }

  return lines.join("\n");
}

function buildPushCardText() {
  const first = getSortedBriefItems()[0];
  const sourceText = getSourceText(first.sourceIds);
  return [
    "【今日AI简报】",
    `生成时间：${dailyMeta.generatedAt}｜数据窗口：${dailyMeta.windowLabel}`,
    `项目名称：${first.projectName || first.title}`,
    `一句话介绍：${first.summary}`,
    `建议动作：${first.action}`,
    "永久可复制链接：",
    sourceText,
    `查看 Dashboard：${dailyMeta.dashboardUrl}`
  ].join("\n");
}

function buildEmailText() {
  const format = els.deliveryFormat.value;
  if (format === "dashboard") {
    return [
      "主题：【今日AI简报】Dashboard 页面",
      "",
      "你好，今日 AI / Agent 情报页面已生成。",
      `生成时间：${dailyMeta.dateLabel} ${dailyMeta.generatedAt}`,
      `打开页面：${dailyMeta.dashboardUrl}`,
      "",
      "页面包含今日摘要、建议动作、关联原文和可验证来源。"
    ].join("\n");
  }

  return buildBriefText(format === "both");
}

async function copyText(text, message) {
  try {
    await navigator.clipboard.writeText(text);
    showCopyStatus(message);
  } catch (error) {
    showCopyStatus("复制失败，请手动选中内容复制。");
  }
}

async function copyBrief() {
  copyText(buildBriefText(true), "简报已复制，可以直接粘贴到飞书、企业微信或邮件。");
}

function generateEmail() {
  const recipient = els.emailInput.value.trim();
  const body = buildEmailText();
  els.emailPreview.textContent = body;

  if (recipient) {
    const subject = encodeURIComponent("【今日AI简报】企业 AI / Agent 每日情报");
    const encodedBody = encodeURIComponent(body);
    window.location.href = `mailto:${encodeURIComponent(recipient)}?subject=${subject}&body=${encodedBody}`;
  }

  showCopyStatus(recipient ? "已打开邮件客户端，可发送给收件人。" : "已生成邮件正文，请填写收件邮箱或复制正文。");
}

function switchView(viewName) {
  if ((viewName === "skills" || viewName === "workflow") && !isInternalMode) return;

  state.activeView = viewName;
  els.viewTitle.textContent = viewTitleMap[viewName];
  els.navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === viewName));
  Object.entries(els.views).forEach(([key, view]) => view.classList.toggle("active", key === viewName));
}

function showCopyStatus(message) {
  els.copyStatus.textContent = message;
  window.clearTimeout(showCopyStatus.timer);
  showCopyStatus.timer = window.setTimeout(() => {
    els.copyStatus.textContent = "";
  }, 2600);
}

function revealInternalMode() {
  els.internalOnly.forEach((node) => {
    node.classList.toggle("internal-only-visible", isInternalMode);
  });
}

function bindEvents() {
  els.navItems.forEach((item) => {
    item.addEventListener("click", () => switchView(item.dataset.view));
  });

  els.copyBriefButton.addEventListener("click", copyBrief);
  els.copyBriefTopButton.addEventListener("click", copyBrief);
  els.copyPushCardButton.addEventListener("click", () => copyText(buildPushCardText(), "企业微信 / 飞书卡片文案已复制。"));
  els.emailButton.addEventListener("click", generateEmail);
  els.emailBriefTopButton.addEventListener("click", () => {
    document.querySelector("#deliverySection").scrollIntoView({ behavior: "smooth", block: "start" });
    els.emailInput.focus();
  });
  els.sourceButton.addEventListener("click", () => {
    document.querySelector("#sourceSection").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  els.deliveryFormat.addEventListener("change", () => {
    els.emailPreview.textContent = buildEmailText();
  });

  els.skillSearchInput.addEventListener("input", (event) => {
    state.skillQuery = event.target.value;
    renderSkills();
  });

  els.skillForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    state.skills.push({
      name: formData.get("name").toString().trim(),
      description: formData.get("description").toString().trim(),
      input: formData.get("input").toString().trim(),
      output: formData.get("output").toString().trim(),
      owner: formData.get("owner").toString().trim(),
      status: formData.get("status").toString(),
      calls: 0
    });
    persistSkills();
    event.currentTarget.reset();
    renderSkills();
  });

  els.resetSkillsButton.addEventListener("click", () => {
    state.skills = [...defaultSkills];
    persistSkills();
    renderSkills();
  });
}

async function init() {
  loadState();
  await loadLiveDashboardData();
  revealInternalMode();
  bindEvents();
  renderBrief();
  renderSources();
  renderPushStatus();
  renderTrends();
  renderSkills();
  renderWorkflow();
  els.emailPreview.textContent = buildEmailText();
}

init();
