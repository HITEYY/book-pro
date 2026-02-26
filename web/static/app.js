const PROVIDERS = ["open-ai", "anthropic", "openrouter", "venice", "kilo-code"];

const PROVIDER_LABEL = {
  "open-ai": "OPEN-AI",
  anthropic: "ANTHROPIC",
  openrouter: "OpenRouter",
  venice: "Venice",
  "kilo-code": "Kilo Code",
};

const DEFAULT_MODEL_BY_PROVIDER = {
  "open-ai": "gpt-4.1-mini",
  anthropic: "claude-sonnet-4-20250514",
  openrouter: "openai/gpt-4.1-mini",
  venice: "venice-uncensored",
  "kilo-code": "anthropic/claude-sonnet-4.5",
};

const MODEL_OPTIONS_BY_PROVIDER = {
  "open-ai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"],
  anthropic: ["claude-sonnet-4-20250514", "claude-3-7-sonnet-latest", "claude-3-5-sonnet-latest"],
  openrouter: ["openai/gpt-4.1-mini", "openai/gpt-4.1", "anthropic/claude-sonnet-4", "google/gemini-2.5-pro"],
  venice: ["venice-uncensored", "llama-3.3-70b", "qwen2.5-72b-instruct"],
  "kilo-code": ["anthropic/claude-sonnet-4.5", "openai/gpt-4.1-mini", "google/gemini-2.5-pro"],
};

const CUSTOM_MODEL_VALUE = "__custom__";

const STORAGE_KEY = "book-pro-panel-settings";

const state = {
  page: 1,
  pageSize: 10,
  total: 0,
  items: [],
  pendingUploads: [],
  nextPendingId: 1,
  currentBook: null,
  currentTab: "chapter",
  currentView: "library",
  uploading: false,
  pendingUploadMode: "multi",
  modelOptions: {},
  modelOptionsLoaded: {},
  settings: {
    selectedProvider: "open-ai",
    language: "ko",
    models: { ...DEFAULT_MODEL_BY_PROVIDER },
    apiKeys: {
      "open-ai": "",
      anthropic: "",
      openrouter: "",
      venice: "",
      "kilo-code": "",
    },
  },
};

const el = {
  navLibrary: document.getElementById("nav-library"),
  navDetail: document.getElementById("nav-detail"),
  navSettings: document.getElementById("nav-settings"),

  viewLibrary: document.getElementById("view-library"),
  viewDetail: document.getElementById("view-detail"),
  viewSettings: document.getElementById("view-settings"),

  settingsProviderSelect: document.getElementById("settings-provider-select"),
  settingsModelSelect: document.getElementById("settings-model-select"),
  settingsCustomModelField: document.getElementById("settings-custom-model-field"),
  settingsCustomModelInput: document.getElementById("settings-custom-model-input"),
  settingsLanguageInput: document.getElementById("settings-language-input"),
  apiKeyOpenAi: document.getElementById("api-key-open-ai"),
  apiKeyAnthropic: document.getElementById("api-key-anthropic"),
  apiKeyOpenrouter: document.getElementById("api-key-openrouter"),
  apiKeyVenice: document.getElementById("api-key-venice"),
  apiKeyKiloCode: document.getElementById("api-key-kilo-code"),
  settingsSaveBtn: document.getElementById("settings-save-btn"),
  settingsActiveSummary: document.getElementById("settings-active-summary"),

  uploadBooksBtn: document.getElementById("upload-books-btn"),
  uploadSingleBtn: document.getElementById("upload-single-btn"),
  generateFromDetailBtn: document.getElementById("generate-from-detail-btn"),
  fileInput: document.getElementById("epub-file-input"),

  metricTotalBooks: document.getElementById("metric-total-books"),
  metricProcessingBooks: document.getElementById("metric-processing-books"),
  metricCompletedBooks: document.getElementById("metric-completed-books"),

  booksTableBody: document.getElementById("books-table-body"),
  libraryPageInfo: document.getElementById("library-page-info"),
  prevPageBtn: document.getElementById("prev-page-btn"),
  nextPageBtn: document.getElementById("next-page-btn"),

  detailTitle: document.getElementById("detail-title"),
  detailSubtitle: document.getElementById("detail-subtitle"),
  detailChapterCount: document.getElementById("detail-chapter-count"),
  detailCharacterCount: document.getElementById("detail-character-count"),
  detailUpdatedAt: document.getElementById("detail-updated-at"),

  tabButtons: Array.from(document.querySelectorAll(".tab")),
  tabChapter: document.getElementById("tab-chapter"),
  tabCharacter: document.getElementById("tab-character"),
  tabWorld: document.getElementById("tab-world"),

  insightBookTitle: document.getElementById("insight-book-title"),
  insightBookStats: document.getElementById("insight-book-stats"),

  toast: document.getElementById("toast"),
};

function escapeHtml(text) {
  return (text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function showToast(message, isError = false) {
  el.toast.textContent = message;
  el.toast.style.background = isError ? "#6b1010" : "#000000";
  el.toast.classList.add("show");
  window.clearTimeout(showToast._timer);
  showToast._timer = window.setTimeout(() => {
    el.toast.classList.remove("show");
  }, 2200);
}

function formatDate(iso) {
  if (!iso) return "-";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function createDefaultSettings() {
  return {
    selectedProvider: "open-ai",
    language: "ko",
    models: { ...DEFAULT_MODEL_BY_PROVIDER },
    apiKeys: {
      "open-ai": "",
      anthropic: "",
      openrouter: "",
      venice: "",
      "kilo-code": "",
    },
  };
}

function normalizeProvider(value) {
  return PROVIDERS.includes(value) ? value : "open-ai";
}

function sortModelsAlphabetically(models) {
  return [...models].sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base", numeric: true }));
}

function initializeModelOptionState() {
  PROVIDERS.forEach((provider) => {
    const defaults = MODEL_OPTIONS_BY_PROVIDER[provider] || [];
    state.modelOptions[provider] = sortModelsAlphabetically(defaults);
    state.modelOptionsLoaded[provider] = false;
  });
}

function loadSettingsFromStorage() {
  const defaults = createDefaultSettings();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      state.settings = defaults;
      renderSettingsForm();
      return;
    }

    const parsed = JSON.parse(raw);
    const selectedProvider = normalizeProvider(parsed.selectedProvider || parsed.provider || "open-ai");
    const language = typeof parsed.language === "string" && parsed.language.trim() ? parsed.language.trim() : "ko";

    const models = { ...DEFAULT_MODEL_BY_PROVIDER };
    if (parsed.models && typeof parsed.models === "object") {
      PROVIDERS.forEach((provider) => {
        const candidate = parsed.models[provider];
        if (typeof candidate === "string" && candidate.trim()) {
          models[provider] = candidate.trim();
        }
      });
    }
    if (typeof parsed.model === "string" && parsed.model.trim()) {
      models[selectedProvider] = parsed.model.trim();
    }

    const apiKeys = { ...defaults.apiKeys };
    if (parsed.apiKeys && typeof parsed.apiKeys === "object") {
      PROVIDERS.forEach((provider) => {
        const key = parsed.apiKeys[provider];
        if (typeof key === "string") {
          apiKeys[provider] = key;
        }
      });
    }
    if (typeof parsed.apiKey === "string" && parsed.apiKey.trim()) {
      apiKeys[selectedProvider] = parsed.apiKey.trim();
    }

    state.settings = {
      selectedProvider,
      language,
      models,
      apiKeys,
    };
  } catch (_error) {
    state.settings = defaults;
  }

  renderSettingsForm();
}

function persistSettings() {
  const provider = state.settings.selectedProvider;
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      selectedProvider: provider,
      provider,
      language: state.settings.language,
      models: state.settings.models,
      model: state.settings.models[provider] || "",
      apiKeys: state.settings.apiKeys,
      apiKey: state.settings.apiKeys[provider] || "",
    }),
  );
}

function renderSettingsSummary() {
  const provider = state.settings.selectedProvider;
  const providerLabel = PROVIDER_LABEL[provider] || provider;
  const model = state.settings.models[provider] || "";
  const hasKey = Boolean(state.settings.apiKeys[provider]);

  el.settingsActiveSummary.textContent = `현재 기본값: ${providerLabel} / ${model || "모델 미설정"} / API Key ${hasKey ? "설정됨" : "미설정"}`;
}

function ensureModelForProvider(provider) {
  if (!state.settings.models[provider]) {
    state.settings.models[provider] = DEFAULT_MODEL_BY_PROVIDER[provider] || "";
  }
}

function getProviderModelOptions(provider) {
  const loaded = state.modelOptions[provider];
  if (Array.isArray(loaded) && loaded.length) {
    return sortModelsAlphabetically(loaded);
  }
  return sortModelsAlphabetically(
    MODEL_OPTIONS_BY_PROVIDER[provider] || [DEFAULT_MODEL_BY_PROVIDER[provider] || ""],
  );
}

function setCustomModelVisible(visible) {
  el.settingsCustomModelField.classList.toggle("hidden", !visible);
}

function renderModelSelect(provider) {
  ensureModelForProvider(provider);

  const activeModel = state.settings.models[provider] || "";
  const options = getProviderModelOptions(provider);
  const inList = options.includes(activeModel);

  el.settingsModelSelect.innerHTML = "";
  for (const model of options) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    el.settingsModelSelect.append(option);
  }

  const customOption = document.createElement("option");
  customOption.value = CUSTOM_MODEL_VALUE;
  customOption.textContent = "직접 입력";
  el.settingsModelSelect.append(customOption);

  if (inList) {
    el.settingsModelSelect.value = activeModel;
    el.settingsCustomModelInput.value = "";
    setCustomModelVisible(false);
    return;
  }

  el.settingsModelSelect.value = CUSTOM_MODEL_VALUE;
  el.settingsCustomModelInput.value = activeModel;
  setCustomModelVisible(true);
}

function readModelFromControls(provider) {
  const selectedValue = (el.settingsModelSelect.value || "").trim();
  if (selectedValue === CUSTOM_MODEL_VALUE) {
    const customValue = el.settingsCustomModelInput.value.trim();
    if (customValue) {
      return customValue;
    }
    return state.settings.models[provider] || DEFAULT_MODEL_BY_PROVIDER[provider] || "";
  }
  return selectedValue || DEFAULT_MODEL_BY_PROVIDER[provider] || "";
}

async function fetchProviderModels(provider, { force = false, silent = false } = {}) {
  const normalized = normalizeProvider(provider);
  if (!force && state.modelOptionsLoaded[normalized]) {
    return;
  }

  const formData = new FormData();
  formData.append("provider", normalized);
  const apiKey = (state.settings.apiKeys[normalized] || "").trim();
  if (apiKey) {
    formData.append("api_key", apiKey);
  }

  try {
    const payload = await fetchJson("/providers/models", {
      method: "POST",
      body: formData,
    });
    const models = Array.isArray(payload.models)
      ? payload.models.map((item) => String(item)).filter((item) => item.trim().length > 0)
      : [];

    if (!models.length) {
      throw new Error(`${PROVIDER_LABEL[normalized]} 모델 목록이 비어 있습니다.`);
    }

    state.modelOptions[normalized] = sortModelsAlphabetically(models);
    state.modelOptionsLoaded[normalized] = true;

    if (!state.settings.models[normalized]) {
      state.settings.models[normalized] = models[0];
      persistSettings();
    }

    if (state.settings.selectedProvider === normalized) {
      renderSettingsForm();
    }
  } catch (error) {
    state.modelOptionsLoaded[normalized] = false;
    if (!silent) {
      showToast(error.message || `${PROVIDER_LABEL[normalized]} 모델 목록 조회 실패`, true);
    }
  }
}

function renderSettingsForm() {
  const provider = state.settings.selectedProvider;

  el.settingsProviderSelect.value = provider;
  renderModelSelect(provider);
  el.settingsLanguageInput.value = state.settings.language || "ko";

  el.apiKeyOpenAi.value = state.settings.apiKeys["open-ai"] || "";
  el.apiKeyAnthropic.value = state.settings.apiKeys.anthropic || "";
  el.apiKeyOpenrouter.value = state.settings.apiKeys.openrouter || "";
  el.apiKeyVenice.value = state.settings.apiKeys.venice || "";
  el.apiKeyKiloCode.value = state.settings.apiKeys["kilo-code"] || "";

  renderSettingsSummary();
}

function syncSettingsFromForm() {
  const prevProvider = state.settings.selectedProvider;
  const nextProvider = normalizeProvider(el.settingsProviderSelect.value);

  state.settings.models[prevProvider] = readModelFromControls(prevProvider);

  state.settings.selectedProvider = nextProvider;
  state.settings.language = el.settingsLanguageInput.value.trim() || "ko";
  state.settings.apiKeys["open-ai"] = el.apiKeyOpenAi.value.trim();
  state.settings.apiKeys.anthropic = el.apiKeyAnthropic.value.trim();
  state.settings.apiKeys.openrouter = el.apiKeyOpenrouter.value.trim();
  state.settings.apiKeys.venice = el.apiKeyVenice.value.trim();
  state.settings.apiKeys["kilo-code"] = el.apiKeyKiloCode.value.trim();

  ensureModelForProvider(nextProvider);

  persistSettings();
  renderSettingsForm();
}

function switchView(view) {
  state.currentView = view;
  el.viewLibrary.classList.toggle("active", view === "library");
  el.viewDetail.classList.toggle("active", view === "detail");
  el.viewSettings.classList.toggle("active", view === "settings");

  el.navLibrary.classList.toggle("active", view === "library");
  el.navDetail.classList.toggle("active", view === "detail");
  el.navSettings.classList.toggle("active", view === "settings");
}

function currentPageCount() {
  return Math.max(1, Math.ceil(state.total / state.pageSize));
}

function pendingProcessingCount() {
  return state.pendingUploads.filter((item) => item.status === "queued" || item.status === "processing").length;
}

function renderLibraryMetrics() {
  const processing = pendingProcessingCount();
  el.metricTotalBooks.textContent = String(state.total + processing);
  el.metricProcessingBooks.textContent = String(processing);
  el.metricCompletedBooks.textContent = String(state.total);
}

function addPendingUpload(fileName) {
  const id = `pending-${state.nextPendingId++}`;
  const row = {
    id,
    fileName,
    status: "queued",
    progress: 0,
    error: "",
    timerId: null,
  };
  state.pendingUploads.unshift(row);
  renderLibraryMetrics();
  renderBooksTable(state.items);
  return row;
}

function updatePendingUpload(id, patch) {
  const row = state.pendingUploads.find((item) => item.id === id);
  if (!row) return;
  Object.assign(row, patch);
  renderLibraryMetrics();
  renderBooksTable(state.items);
}

function removePendingUpload(id) {
  const index = state.pendingUploads.findIndex((item) => item.id === id);
  if (index < 0) return;
  const [row] = state.pendingUploads.splice(index, 1);
  if (row && row.timerId) {
    window.clearInterval(row.timerId);
  }
  renderLibraryMetrics();
  renderBooksTable(state.items);
}

function setUploading(isUploading) {
  state.uploading = isUploading;
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `HTTP ${response.status}`);
  }
  return payload;
}

async function loadLibrary({ autoOpenFirst = false } = {}) {
  const payload = await fetchJson(`/books?page=${state.page}&page_size=${state.pageSize}`);
  state.total = payload.total;
  state.items = payload.items;

  renderLibraryMetrics();
  renderBooksTable(state.items);

  const totalPages = currentPageCount();
  el.libraryPageInfo.textContent = `페이지 ${state.page} / ${totalPages}`;
  el.prevPageBtn.disabled = state.page <= 1;
  el.nextPageBtn.disabled = state.page >= totalPages;

  if (autoOpenFirst && payload.items.length > 0) {
    await openBook(payload.items[0].slug, { switchToDetail: true });
  }
}

function renderBooksTable(items) {
  const pendingRows = state.pendingUploads
    .map((item) => {
      const statusLabel =
        item.status === "processing"
          ? "요약 중"
          : item.status === "queued"
            ? "대기 중"
            : item.status === "failed"
              ? "실패"
              : "완료";
      const statusClass =
        item.status === "failed"
          ? "status-failed"
          : item.status === "completed"
            ? "status-completed"
            : "status-processing";

      return `
        <tr class="pending-row">
          <td>${escapeHtml(item.fileName)}</td>
          <td>
            <span class="status-chip ${statusClass}">${statusLabel}</span>
            <div class="progress-track">
              <div class="progress-fill" style="width:${Math.max(0, Math.min(item.progress || 0, 100))}%"></div>
            </div>
            <div class="progress-text">${Math.round(item.progress || 0)}%</div>
            ${item.error ? `<div class="error-text">${escapeHtml(item.error)}</div>` : ""}
          </td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>${item.status === "processing" || item.status === "queued" ? "진행 중" : "-"}</td>
        </tr>
      `;
    })
    .join("");

  const savedRows = items
    .map(
      (item) => `
      <tr>
        <td>${escapeHtml(item.book_title)}</td>
        <td><span class="status-chip status-completed">${escapeHtml(item.status)}</span></td>
        <td>${escapeHtml(formatDate(item.updated_at))}</td>
        <td>${item.chapter_count}</td>
        <td>${item.character_count}</td>
        <td>
          <button class="inline-action" data-open-book="${escapeHtml(item.slug)}" type="button">열기</button>
        </td>
      </tr>
    `,
    )
    .join("");

  if (!pendingRows && !savedRows) {
    el.booksTableBody.innerHTML = `
      <tr>
        <td class="empty-row" colspan="6">저장된 책이 없습니다. EPUB 업로드 후 시작하세요.</td>
      </tr>
    `;
    return;
  }

  el.booksTableBody.innerHTML = `${pendingRows}${savedRows}`;

  el.booksTableBody.querySelectorAll("[data-open-book]").forEach((button) => {
    button.addEventListener("click", async () => {
      const slug = button.getAttribute("data-open-book");
      if (!slug) return;
      await openBook(slug, { switchToDetail: true });
    });
  });
}

function extractSection(markdown, sectionName) {
  const pattern = new RegExp(`##\\s+${sectionName}\\n([\\s\\S]*?)(\\n##\\s+|$)`, "m");
  const match = markdown.match(pattern);
  return match ? match[1].trim() : "";
}

function markdownToHtml(markdown) {
  const lines = (markdown || "").split("\n");
  let html = "";
  let inList = false;

  const closeList = () => {
    if (inList) {
      html += "</ul>";
      inList = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }

    if (line.startsWith("# ")) {
      closeList();
      html += `<h3>${escapeHtml(line.slice(2))}</h3>`;
      continue;
    }

    if (line.startsWith("## ")) {
      closeList();
      html += `<h4>${escapeHtml(line.slice(3))}</h4>`;
      continue;
    }

    if (line.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${escapeHtml(line.slice(2))}</li>`;
      continue;
    }

    closeList();
    html += `<p>${escapeHtml(line)}</p>`;
  }

  closeList();
  return html;
}

function renderDetail(detail) {
  el.detailTitle.textContent = detail.book_title;
  el.detailSubtitle.textContent = `slug: ${detail.slug}`;
  el.detailChapterCount.textContent = String(detail.chapter_count);
  el.detailCharacterCount.textContent = String(detail.character_count);
  el.detailUpdatedAt.textContent = formatDate(detail.updated_at);

  el.insightBookTitle.textContent = detail.book_title;
  el.insightBookStats.textContent = `챕터 ${detail.chapter_count}개 · 캐릭터 ${detail.character_count}개`;

  if (!detail.chapters.length) {
    el.tabChapter.innerHTML = `<div class="chapter-card"><p class="chapter-snippet">챕터 요약이 없습니다.</p></div>`;
  } else {
    el.tabChapter.innerHTML = detail.chapters
      .map((chapter) => {
        const summary = extractSection(chapter.markdown, "요약") || "요약 텍스트가 없습니다.";
        return `
          <article class="chapter-card">
            <h3 class="chapter-title">Chapter ${chapter.index}: ${escapeHtml(chapter.title)}</h3>
            <p class="chapter-snippet">${escapeHtml(summary)}</p>
            <details>
              <summary>원문 보기 (${escapeHtml(chapter.file_name)})</summary>
              <pre>${escapeHtml(chapter.markdown)}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  if (!detail.characters.length) {
    el.tabCharacter.innerHTML = `<div class="character-card"><p class="character-snippet">캐릭터 요약이 없습니다.</p></div>`;
  } else {
    el.tabCharacter.innerHTML = detail.characters
      .map((character) => {
        const preview = character.markdown.split("\n").slice(0, 6).join("\n");
        return `
          <article class="character-card">
            <h3 class="character-title">${escapeHtml(character.name)}</h3>
            <p class="character-snippet">${escapeHtml(preview).replaceAll("\n", "<br>")}</p>
            <details>
              <summary>원문 보기 (${escapeHtml(character.file_name)})</summary>
              <pre>${escapeHtml(character.markdown)}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  el.tabWorld.innerHTML = `<div class="markdown-view">${markdownToHtml(detail.setting_markdown || "setting.md가 없습니다.")}</div>`;

  setTab(state.currentTab);
}

function setTab(tabName) {
  state.currentTab = tabName;
  el.tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  el.tabChapter.classList.toggle("active", tabName === "chapter");
  el.tabCharacter.classList.toggle("active", tabName === "character");
  el.tabWorld.classList.toggle("active", tabName === "world");
}

async function openBook(slug, { switchToDetail = false } = {}) {
  const detail = await fetchJson(`/books/${encodeURIComponent(slug)}`);
  state.currentBook = detail;
  renderDetail(detail);

  if (switchToDetail) {
    switchView("detail");
  }
}

function openFilePicker(mode) {
  state.pendingUploadMode = mode;
  el.fileInput.multiple = mode === "multi";
  el.fileInput.value = "";
  el.fileInput.click();
}

function getRunConfig() {
  syncSettingsFromForm();

  const provider = state.settings.selectedProvider;
  const model = state.settings.models[provider] || DEFAULT_MODEL_BY_PROVIDER[provider] || "";
  const apiKey = state.settings.apiKeys[provider] || "";
  const language = state.settings.language || "ko";

  if (!apiKey) {
    throw new Error(`${PROVIDER_LABEL[provider]} API Key를 Settings 페이지에서 입력하세요.`);
  }

  return { provider, model, apiKey, language };
}

function buildSingleUploadFormData(file, config) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("provider", config.provider);
  formData.append("language", config.language);
  if (config.model) formData.append("model", config.model);
  if (config.apiKey) formData.append("api_key", config.apiKey);
  return formData;
}

async function uploadSingleFile(file, config, pendingRow) {
  updatePendingUpload(pendingRow.id, { status: "processing", progress: 6, error: "" });

  const timerId = window.setInterval(() => {
    const target = (pendingRow.progress || 0) + Math.floor(Math.random() * 7) + 2;
    updatePendingUpload(pendingRow.id, { progress: Math.min(target, 92) });
  }, 700);

  updatePendingUpload(pendingRow.id, { timerId });

  try {
    const formData = buildSingleUploadFormData(file, config);
    const payload = await fetchJson("/summaries/from-epub", {
      method: "POST",
      body: formData,
    });

    window.clearInterval(timerId);
    updatePendingUpload(pendingRow.id, { status: "completed", progress: 100, timerId: null });
    window.setTimeout(() => removePendingUpload(pendingRow.id), 1200);
    return { ok: true, payload };
  } catch (error) {
    window.clearInterval(timerId);
    updatePendingUpload(pendingRow.id, {
      status: "failed",
      progress: 100,
      error: error.message || "요약 실패",
      timerId: null,
    });
    return { ok: false, error };
  }
}

async function uploadFiles(files) {
  if (!files.length) return;

  let config;
  try {
    config = getRunConfig();
  } catch (error) {
    showToast(error.message || "설정 오류", true);
    return;
  }

  const pendingRows = files.map((file) => addPendingUpload(file.name));

  let successCount = 0;
  let failureCount = 0;

  try {
    setUploading(true);

    for (let i = 0; i < files.length; i += 1) {
      const result = await uploadSingleFile(files[i], config, pendingRows[i]);
      if (result.ok) {
        successCount += 1;
        await loadLibrary({ autoOpenFirst: false });
      } else {
        failureCount += 1;
      }
    }

    showToast(`완료 ${successCount}권 / 실패 ${failureCount}권`, failureCount > 0);
    if (successCount > 0) switchView("library");
  } catch (error) {
    showToast(error.message || "업로드 실패", true);
  } finally {
    setUploading(false);
  }
}

function bindSettingsEvents() {
  el.settingsProviderSelect.addEventListener("change", () => {
    syncSettingsFromForm();
    void fetchProviderModels(state.settings.selectedProvider, { force: true, silent: false });
  });

  el.settingsModelSelect.addEventListener("change", () => {
    if (el.settingsModelSelect.value === CUSTOM_MODEL_VALUE) {
      setCustomModelVisible(true);
      el.settingsCustomModelInput.focus();
      return;
    }
    setCustomModelVisible(false);
    syncSettingsFromForm();
  });

  el.settingsCustomModelInput.addEventListener("change", () => {
    syncSettingsFromForm();
  });

  el.settingsLanguageInput.addEventListener("change", () => {
    syncSettingsFromForm();
  });

  [
    { element: el.apiKeyOpenAi, provider: "open-ai" },
    { element: el.apiKeyAnthropic, provider: "anthropic" },
    { element: el.apiKeyOpenrouter, provider: "openrouter" },
    { element: el.apiKeyVenice, provider: "venice" },
    { element: el.apiKeyKiloCode, provider: "kilo-code" },
  ].forEach(({ element, provider }) => {
    element.addEventListener("change", () => {
      syncSettingsFromForm();
      if (state.currentView === "settings") {
        void fetchProviderModels(provider, { force: true, silent: true });
      }
    });
  });

  el.settingsSaveBtn.addEventListener("click", async () => {
    syncSettingsFromForm();
    await fetchProviderModels(state.settings.selectedProvider, { force: true, silent: true });
    showToast("설정을 저장했습니다.");
  });
}

function bindEvents() {
  el.navLibrary.addEventListener("click", () => switchView("library"));

  el.navDetail.addEventListener("click", () => {
    if (!state.currentBook) {
      showToast("먼저 Library에서 책을 선택하세요.", true);
      return;
    }
    switchView("detail");
  });

  el.navSettings.addEventListener("click", () => {
    switchView("settings");
  });

  el.uploadBooksBtn.addEventListener("click", () => openFilePicker("multi"));
  el.uploadSingleBtn.addEventListener("click", () => openFilePicker("single"));
  el.generateFromDetailBtn.addEventListener("click", () => openFilePicker("single"));

  el.fileInput.addEventListener("change", async () => {
    const files = Array.from(el.fileInput.files || []);
    if (!files.length) return;
    const picked = state.pendingUploadMode === "single" ? files.slice(0, 1) : files;
    await uploadFiles(picked);
  });

  el.prevPageBtn.addEventListener("click", async () => {
    if (state.page <= 1) return;
    state.page -= 1;
    await loadLibrary();
  });

  el.nextPageBtn.addEventListener("click", async () => {
    if (state.page >= currentPageCount()) return;
    state.page += 1;
    await loadLibrary();
  });

  el.tabButtons.forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.tab));
  });

  bindSettingsEvents();
}

async function init() {
  initializeModelOptionState();
  loadSettingsFromStorage();
  bindEvents();
  setTab("chapter");
  await fetchProviderModels(state.settings.selectedProvider, { force: true, silent: true });

  try {
    await loadLibrary();
    if (state.items.length > 0) {
      await openBook(state.items[0].slug);
    }
  } catch (error) {
    showToast(error.message || "초기 로딩 실패", true);
  }
}

void init();
