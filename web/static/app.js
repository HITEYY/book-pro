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
const DEFAULT_UPLOAD_PARALLEL = 3;
const MIN_UPLOAD_PARALLEL = 1;
const MAX_UPLOAD_PARALLEL = 8;

const STORAGE_KEY = "book-pro-panel-settings";
const UI_LANGUAGES = ["ko", "en", "ja"];

const I18N_MESSAGES = {
  ko: {
    brand_sub: "다권 요약 허브",
    nav_library: "라이브러리",
    nav_detail: "책 상세",
    nav_settings: "설정",
    library_title: "Books Library",
    detail_title_default: "Book Detail",
    settings_title: "Settings",
    tip_title: "EPUB 다권 업로드",
    tip_body: "여러 권을 한번에 업로드하고 책별 챕터/캐릭터/세계관 요약을 저장합니다.",
    library_subtitle: "여러 권을 등록하고 책별 상세 요약 페이지로 이동하세요.",
    upload_books_btn: "EPUB 여러권 업로드",
    metric_total_books_label: "등록된 책",
    metric_total_books_meta: "라이브러리 전체",
    metric_processing_label: "처리 중",
    metric_processing_meta: "현재 실행중",
    metric_completed_label: "완료",
    metric_completed_meta: "열람 가능",
    books_table_title: "책 목록",
    th_title: "제목",
    th_status: "상태",
    th_updated: "최근 업데이트",
    th_chapters: "챕터",
    th_characters: "캐릭터",
    th_action: "액션",
    pagination_prev: "이전",
    pagination_next: "다음",
    tab_chapter: "챕터",
    tab_character: "캐릭터",
    tab_world: "세계관",
    tab_reader: "리더",
    detail_subtitle_empty: "Library에서 책을 선택하면 상세 요약이 표시됩니다.",
    upload_single_btn: "EPUB 업로드",
    detail_metric_chapters_label: "챕터",
    detail_metric_chapters_meta: "분석된 챕터 수",
    detail_metric_characters_label: "캐릭터",
    detail_metric_characters_meta: "추출된 캐릭터",
    detail_metric_updated_label: "최근 업데이트",
    detail_metric_updated_meta: "저장 기준",
    quick_insights_title: "빠른 인사이트",
    insight_book_select: "책을 선택하세요.",
    generate_new_summary_btn: "새 요약 생성",
    settings_subtitle: "기본 Provider/Model을 설정하고 Provider별 API Key를 관리합니다.",
    settings_save_btn: "설정 저장",
    settings_basic_title: "기본 실행 설정",
    settings_default_provider: "기본 Provider",
    settings_default_model: "기본 Model",
    settings_custom_model: "직접 입력 Model",
    settings_custom_model_placeholder: "예: gpt-4.1-mini",
    settings_ui_language: "UI 언어",
    settings_default_language: "요약 Language",
    settings_upload_parallel: "업로드 병렬 수",
    settings_precise_analysis: "정밀 분석 사용",
    settings_hint:
      "Model은 리스트에서 선택합니다. 목록에 없으면 직접 입력 Model을 사용하세요. 업로드 병렬 수는 1~8 범위입니다. 정밀 분석을 켜면 챕터별 캐릭터 특징과 작가 필체 분석을 추가해 정확도를 높입니다.",
    settings_api_key_title: "Provider별 API Key",
    settings_summary:
      "현재 기본값: {provider} / {model} / API Key {apiKeyState} / 업로드 병렬 {uploadParallel} / 정밀 분석 {precise}",
    bool_on: "ON",
    bool_off: "OFF",
    model_not_set: "모델 미설정",
    api_key_set: "설정됨",
    api_key_unset: "미설정",
    custom_model_option: "직접 입력",
    models_empty: "{provider} 모델 목록이 비어 있습니다.",
    models_fetch_failed: "{provider} 모델 목록 조회 실패",
    upload_waiting: "업로드 대기 중",
    stage_queued: "업로드 대기 중",
    stage_upload: "업로드 파일 수신 중",
    stage_parse: "EPUB 파싱 중",
    stage_start: "요약 시작",
    stage_chapter: "챕터 요약 중",
    stage_character: "캐릭터 요약 중",
    stage_world: "세계관 요약 중",
    stage_style: "작가 필체 분석 중",
    stage_saving: "Markdown 저장 중",
    stage_done: "요약 완료",
    stage_failed: "요약 실패",
    pending_stage_chapter: "챕터 {index}/{total}{titlePart}",
    pending_stage_character: "캐릭터 {index}/{total}{namePart}",
    page_info: "페이지 {page} / {total}",
    status_processing: "요약 중",
    status_queued: "대기 중",
    status_failed: "실패",
    status_completed: "완료",
    table_action_open: "열기",
    table_progressing: "진행 중",
    empty_books_table: "저장된 책이 없습니다. EPUB 업로드 후 시작하세요.",
    reader_loading: "원문 EPUB를 불러오는 중입니다.",
    reader_no_chapters: "{title} 원문 챕터가 없습니다.",
    reader_load_failed: "원문 EPUB를 불러오지 못했습니다.",
    reader_chapter_prefix: "챕터",
    insight_stats: "챕터 {chapters}개 · 캐릭터 {characters}개",
    empty_chapter_summary: "챕터 요약이 없습니다.",
    summary_text_missing: "요약 텍스트가 없습니다.",
    view_original: "원문 보기",
    empty_character_summary: "캐릭터 요약이 없습니다.",
    world_missing: "setting.md가 없습니다.",
    upload_start: "업로드 시작",
    summary_done: "요약 완료",
    summary_failed: "요약 실패",
    config_error: "설정 오류",
    upload_error: "업로드 실패",
    result_with_error: "완료 {success}권 / 실패 {failure}권 - {error}",
    result_summary: "완료 {success}권 / 실패 {failure}권",
    settings_saved: "설정을 저장했습니다.",
    select_book_first: "먼저 Library에서 책을 선택하세요.",
    init_load_failed: "초기 로딩 실패",
  },
  en: {
    brand_sub: "Multi-book Summary Hub",
    nav_library: "Library",
    nav_detail: "Book Detail",
    nav_settings: "Settings",
    library_title: "Books Library",
    detail_title_default: "Book Detail",
    settings_title: "Settings",
    tip_title: "Upload Multiple EPUBs",
    tip_body: "Upload multiple books and save chapter/character/world summaries per book.",
    library_subtitle: "Register books and open each book detail page.",
    upload_books_btn: "Upload EPUBs",
    metric_total_books_label: "Books",
    metric_total_books_meta: "All library items",
    metric_processing_label: "Processing",
    metric_processing_meta: "Currently running",
    metric_completed_label: "Completed",
    metric_completed_meta: "Ready to view",
    books_table_title: "Books",
    th_title: "Title",
    th_status: "Status",
    th_updated: "Updated",
    th_chapters: "Chapters",
    th_characters: "Characters",
    th_action: "Action",
    pagination_prev: "Prev",
    pagination_next: "Next",
    tab_chapter: "Chapter",
    tab_character: "Character",
    tab_world: "World",
    tab_reader: "Reader",
    detail_subtitle_empty: "Select a book in Library to view details.",
    upload_single_btn: "Upload EPUB",
    detail_metric_chapters_label: "Chapters",
    detail_metric_chapters_meta: "Summarized chapters",
    detail_metric_characters_label: "Characters",
    detail_metric_characters_meta: "Extracted profiles",
    detail_metric_updated_label: "Updated",
    detail_metric_updated_meta: "Saved timestamp",
    quick_insights_title: "Quick Insights",
    insight_book_select: "Select a book.",
    generate_new_summary_btn: "Generate New Summary",
    settings_subtitle: "Set default provider/model and manage API keys by provider.",
    settings_save_btn: "Save Settings",
    settings_basic_title: "Default Run Settings",
    settings_default_provider: "Default Provider",
    settings_default_model: "Default Model",
    settings_custom_model: "Custom Model",
    settings_custom_model_placeholder: "e.g. gpt-4.1-mini",
    settings_ui_language: "UI Language",
    settings_default_language: "Summary Language",
    settings_upload_parallel: "Upload Parallelism",
    settings_precise_analysis: "Enable Precise Analysis",
    settings_hint:
      "Pick model from the list. If missing, use custom model. Upload parallelism range is 1~8. Precise analysis adds chapter-level character traits and writing-style analysis.",
    settings_api_key_title: "API Keys by Provider",
    settings_summary:
      "Current defaults: {provider} / {model} / API Key {apiKeyState} / Parallel {uploadParallel} / Precise {precise}",
    bool_on: "ON",
    bool_off: "OFF",
    model_not_set: "Model not set",
    api_key_set: "configured",
    api_key_unset: "not configured",
    custom_model_option: "Custom input",
    models_empty: "{provider} model list is empty.",
    models_fetch_failed: "Failed to load {provider} models",
    upload_waiting: "Waiting for upload",
    stage_queued: "Waiting for upload",
    stage_upload: "Receiving upload file",
    stage_parse: "Parsing EPUB",
    stage_start: "Starting summary",
    stage_chapter: "Summarizing chapters",
    stage_character: "Summarizing characters",
    stage_world: "Summarizing world",
    stage_style: "Analyzing writing style",
    stage_saving: "Saving markdown",
    stage_done: "Summary completed",
    stage_failed: "Summary failed",
    pending_stage_chapter: "Chapter {index}/{total}{titlePart}",
    pending_stage_character: "Character {index}/{total}{namePart}",
    page_info: "Page {page} / {total}",
    status_processing: "Processing",
    status_queued: "Queued",
    status_failed: "Failed",
    status_completed: "Completed",
    table_action_open: "Open",
    table_progressing: "In progress",
    empty_books_table: "No saved books yet. Upload an EPUB to start.",
    reader_loading: "Loading EPUB original text...",
    reader_no_chapters: "No readable chapters in {title}.",
    reader_load_failed: "Failed to load EPUB original text.",
    reader_chapter_prefix: "Chapter",
    insight_stats: "Chapters {chapters} · Characters {characters}",
    empty_chapter_summary: "No chapter summaries.",
    summary_text_missing: "Summary text is missing.",
    view_original: "View source",
    empty_character_summary: "No character summaries.",
    world_missing: "setting.md is missing.",
    upload_start: "Upload started",
    summary_done: "Summary completed",
    summary_failed: "Summary failed",
    config_error: "Configuration error",
    upload_error: "Upload failed",
    result_with_error: "Done {success} / Failed {failure} - {error}",
    result_summary: "Done {success} / Failed {failure}",
    settings_saved: "Settings saved.",
    select_book_first: "Select a book from Library first.",
    init_load_failed: "Initial load failed",
  },
  ja: {
    brand_sub: "マルチブック要約ハブ",
    nav_library: "ライブラリ",
    nav_detail: "本の詳細",
    nav_settings: "設定",
    library_title: "Books Library",
    detail_title_default: "Book Detail",
    settings_title: "Settings",
    tip_title: "EPUB 複数アップロード",
    tip_body: "複数の本を一括アップロードし、本ごとの章/キャラクター/世界観要約を保存します。",
    library_subtitle: "複数の本を登録し、各本の詳細ページを開きます。",
    upload_books_btn: "EPUB をアップロード",
    metric_total_books_label: "本",
    metric_total_books_meta: "ライブラリ全体",
    metric_processing_label: "処理中",
    metric_processing_meta: "現在実行中",
    metric_completed_label: "完了",
    metric_completed_meta: "閲覧可能",
    books_table_title: "本一覧",
    th_title: "タイトル",
    th_status: "状態",
    th_updated: "更新日時",
    th_chapters: "章",
    th_characters: "キャラクター",
    th_action: "操作",
    pagination_prev: "前へ",
    pagination_next: "次へ",
    tab_chapter: "章",
    tab_character: "キャラクター",
    tab_world: "世界観",
    tab_reader: "リーダー",
    detail_subtitle_empty: "ライブラリで本を選択すると詳細が表示されます。",
    upload_single_btn: "EPUB アップロード",
    detail_metric_chapters_label: "章",
    detail_metric_chapters_meta: "要約済み章数",
    detail_metric_characters_label: "キャラクター",
    detail_metric_characters_meta: "抽出されたプロフィール",
    detail_metric_updated_label: "更新日時",
    detail_metric_updated_meta: "保存基準",
    quick_insights_title: "クイックインサイト",
    insight_book_select: "本を選択してください。",
    generate_new_summary_btn: "新しい要約を生成",
    settings_subtitle: "デフォルト Provider/Model を設定し、Provider ごとの API Key を管理します。",
    settings_save_btn: "設定を保存",
    settings_basic_title: "デフォルト実行設定",
    settings_default_provider: "デフォルト Provider",
    settings_default_model: "デフォルト Model",
    settings_custom_model: "カスタム Model",
    settings_custom_model_placeholder: "例: gpt-4.1-mini",
    settings_ui_language: "UI 言語",
    settings_default_language: "要約言語",
    settings_upload_parallel: "アップロード並列数",
    settings_precise_analysis: "精密分析を有効化",
    settings_hint:
      "Model はリストから選択します。なければカスタム Model を使用します。アップロード並列数は 1〜8。精密分析を有効にすると章ごとのキャラクター特徴と文体分析を追加します。",
    settings_api_key_title: "Provider 別 API Key",
    settings_summary:
      "現在の既定値: {provider} / {model} / API Key {apiKeyState} / 並列 {uploadParallel} / 精密分析 {precise}",
    bool_on: "ON",
    bool_off: "OFF",
    model_not_set: "Model 未設定",
    api_key_set: "設定済み",
    api_key_unset: "未設定",
    custom_model_option: "直接入力",
    models_empty: "{provider} のモデル一覧が空です。",
    models_fetch_failed: "{provider} のモデル一覧取得に失敗しました",
    upload_waiting: "アップロード待機中",
    stage_queued: "アップロード待機中",
    stage_upload: "アップロードファイル受信中",
    stage_parse: "EPUB 解析中",
    stage_start: "要約開始",
    stage_chapter: "章要約中",
    stage_character: "キャラクター要約中",
    stage_world: "世界観要約中",
    stage_style: "文体分析中",
    stage_saving: "Markdown 保存中",
    stage_done: "要約完了",
    stage_failed: "要約失敗",
    pending_stage_chapter: "章 {index}/{total}{titlePart}",
    pending_stage_character: "キャラクター {index}/{total}{namePart}",
    page_info: "ページ {page} / {total}",
    status_processing: "要約中",
    status_queued: "待機中",
    status_failed: "失敗",
    status_completed: "完了",
    table_action_open: "開く",
    table_progressing: "進行中",
    empty_books_table: "保存された本がありません。EPUB をアップロードしてください。",
    reader_loading: "EPUB 原文を読み込み中です...",
    reader_no_chapters: "{title} に読める章がありません。",
    reader_load_failed: "EPUB 原文の読み込みに失敗しました。",
    reader_chapter_prefix: "章",
    insight_stats: "章 {chapters} · キャラクター {characters}",
    empty_chapter_summary: "章要約がありません。",
    summary_text_missing: "要約テキストがありません。",
    view_original: "原文を見る",
    empty_character_summary: "キャラクター要約がありません。",
    world_missing: "setting.md がありません。",
    upload_start: "アップロード開始",
    summary_done: "要約完了",
    summary_failed: "要約失敗",
    config_error: "設定エラー",
    upload_error: "アップロード失敗",
    result_with_error: "完了 {success} / 失敗 {failure} - {error}",
    result_summary: "完了 {success} / 失敗 {failure}",
    settings_saved: "設定を保存しました。",
    select_book_first: "先に Library で本を選択してください。",
    init_load_failed: "初期読み込みに失敗しました",
  },
};

function normalizeUiLanguage(value) {
  return UI_LANGUAGES.includes(value) ? value : "ko";
}

function t(key, params = {}) {
  const lang = normalizeUiLanguage(state.settings?.uiLanguage || "ko");
  const table = I18N_MESSAGES[lang] || I18N_MESSAGES.ko;
  const fallback = I18N_MESSAGES.ko[key] || key;
  const template = table[key] || fallback;
  return template.replace(/\{(\w+)\}/g, (_, name) => String(params[name] ?? ""));
}

function applyI18nToDom() {
  const lang = normalizeUiLanguage(state.settings?.uiLanguage || "ko");
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (!key) return;
    node.textContent = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.getAttribute("data-i18n-placeholder");
    if (!key) return;
    node.setAttribute("placeholder", t(key));
  });
}

function clampUploadParallel(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return DEFAULT_UPLOAD_PARALLEL;
  const rounded = Math.trunc(numeric);
  return Math.max(MIN_UPLOAD_PARALLEL, Math.min(MAX_UPLOAD_PARALLEL, rounded));
}

const state = {
  page: 1,
  pageSize: 10,
  total: 0,
  items: [],
  pendingUploads: [],
  nextPendingId: 1,
  currentBook: null,
  readerCache: {},
  readerRequestSeq: 0,
  currentTab: "chapter",
  currentView: "library",
  uploading: false,
  pendingUploadMode: "multi",
  modelOptions: {},
  modelOptionsLoaded: {},
  settings: {
    selectedProvider: "open-ai",
    uiLanguage: "ko",
    language: "ko",
    uploadParallel: DEFAULT_UPLOAD_PARALLEL,
    preciseAnalysis: false,
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
  settingsUiLanguageInput: document.getElementById("settings-ui-language-input"),
  settingsLanguageInput: document.getElementById("settings-language-input"),
  settingsUploadParallelInput: document.getElementById("settings-upload-parallel-input"),
  settingsPreciseAnalysisInput: document.getElementById("settings-precise-analysis-input"),
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
  tabReader: document.getElementById("tab-reader"),

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
  const localeByUi = {
    ko: "ko-KR",
    en: "en-US",
    ja: "ja-JP",
  };
  const locale = localeByUi[normalizeUiLanguage(state.settings?.uiLanguage || "ko")] || "ko-KR";
  return date.toLocaleString(locale, {
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
    uiLanguage: "ko",
    language: "ko",
    uploadParallel: DEFAULT_UPLOAD_PARALLEL,
    preciseAnalysis: false,
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
    const uiLanguage = normalizeUiLanguage(parsed.uiLanguage || parsed.ui_language || "ko");
    const language = typeof parsed.language === "string" && parsed.language.trim() ? parsed.language.trim() : "ko";
    const uploadParallel = clampUploadParallel(parsed.uploadParallel ?? parsed.maxParallel);
    const preciseAnalysis = parsed.preciseAnalysis === true || parsed.preciseAnalysis === "true";

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
      uiLanguage,
      language,
      uploadParallel,
      preciseAnalysis,
      models,
      apiKeys,
    };
  } catch (_error) {
    state.settings = defaults;
  }

  applyI18nToDom();
  renderSettingsForm();
}

function persistSettings() {
  const provider = state.settings.selectedProvider;
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      selectedProvider: provider,
      provider,
      uiLanguage: normalizeUiLanguage(state.settings.uiLanguage),
      language: state.settings.language,
      uploadParallel: clampUploadParallel(state.settings.uploadParallel),
      maxParallel: clampUploadParallel(state.settings.uploadParallel),
      preciseAnalysis: Boolean(state.settings.preciseAnalysis),
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
  const uploadParallel = clampUploadParallel(state.settings.uploadParallel);
  const preciseText = state.settings.preciseAnalysis ? t("bool_on") : t("bool_off");
  const modelText = model || t("model_not_set");

  el.settingsActiveSummary.textContent = t("settings_summary", {
    provider: providerLabel,
    model: modelText,
    apiKeyState: hasKey ? t("api_key_set") : t("api_key_unset"),
    uploadParallel,
    precise: preciseText,
  });
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
  customOption.textContent = t("custom_model_option");
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
      throw new Error(t("models_empty", { provider: PROVIDER_LABEL[normalized] }));
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
      showToast(error.message || t("models_fetch_failed", { provider: PROVIDER_LABEL[normalized] }), true);
    }
  }
}

function renderSettingsForm() {
  const provider = state.settings.selectedProvider;

  applyI18nToDom();
  if (!state.currentBook) {
    el.insightBookTitle.textContent = t("insight_book_select");
  }
  el.settingsProviderSelect.value = provider;
  renderModelSelect(provider);
  el.settingsUiLanguageInput.value = normalizeUiLanguage(state.settings.uiLanguage || "ko");
  el.settingsLanguageInput.value = state.settings.language || "ko";
  el.settingsUploadParallelInput.value = String(clampUploadParallel(state.settings.uploadParallel));
  el.settingsPreciseAnalysisInput.checked = Boolean(state.settings.preciseAnalysis);

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
  state.settings.uiLanguage = normalizeUiLanguage(el.settingsUiLanguageInput.value);
  state.settings.language = el.settingsLanguageInput.value.trim() || "ko";
  state.settings.uploadParallel = clampUploadParallel(el.settingsUploadParallelInput.value);
  state.settings.preciseAnalysis = Boolean(el.settingsPreciseAnalysisInput.checked);
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

function generateUploadId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function findPendingUploadByUploadId(uploadId) {
  return state.pendingUploads.find((item) => item.uploadId === uploadId) || null;
}

function addPendingUpload(fileName, options = {}) {
  const id = options.id || `pending-${state.nextPendingId++}`;
  const row = {
    id,
    uploadId: options.uploadId || generateUploadId(),
    fileName,
    displayName: options.displayName || fileName,
    status: options.status || "queued",
    progress: Number.isFinite(options.progress) ? options.progress : 0,
    message: options.message || t("upload_waiting"),
    bookTitle: options.bookTitle || "",
    stage: options.stage || "queued",
    chapterIndex: options.chapterIndex ?? null,
    chapterTotal: options.chapterTotal ?? null,
    chapterTitle: options.chapterTitle || "",
    characterIndex: options.characterIndex ?? null,
    characterTotal: options.characterTotal ?? null,
    characterName: options.characterName || "",
    error: options.error || "",
    timerId: null,
    completionTimerId: null,
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
  if (row && row.completionTimerId) {
    window.clearTimeout(row.completionTimerId);
  }
  renderLibraryMetrics();
  renderBooksTable(state.items);
}

function renderPendingMessage(item) {
  if (item.error) return item.error;

  if (item.stage === "chapter") {
    const chapterIndex = item.chapterIndex;
    const chapterTotal = item.chapterTotal;
    const chapterTitle = item.chapterTitle || "";
    if (chapterIndex && chapterTotal) {
      return t("pending_stage_chapter", {
        index: chapterIndex,
        total: chapterTotal,
        titlePart: chapterTitle ? ` - ${chapterTitle}` : "",
      });
    }
  }

  if (item.stage === "character") {
    const characterIndex = item.characterIndex;
    const characterTotal = item.characterTotal;
    const characterName = item.characterName || "";
    if (characterIndex && characterTotal) {
      return t("pending_stage_character", {
        index: characterIndex,
        total: characterTotal,
        namePart: characterName ? ` - ${characterName}` : "",
      });
    }
  }

  const stageKey = item.stage ? `stage_${item.stage}` : "";
  const stageText = stageKey ? t(stageKey) : "";
  if (stageText && stageText !== stageKey) {
    return stageText;
  }

  return item.message || "-";
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
  el.libraryPageInfo.textContent = t("page_info", { page: state.page, total: totalPages });
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
          ? t("status_processing")
          : item.status === "queued"
            ? t("status_queued")
            : item.status === "failed"
              ? t("status_failed")
              : t("status_completed");
      const statusClass =
        item.status === "failed"
          ? "status-failed"
          : item.status === "completed"
            ? "status-completed"
            : "status-processing";

      return `
        <tr class="pending-row">
          <td>${escapeHtml(item.bookTitle || item.displayName || item.fileName)}</td>
          <td>
            <span class="status-chip ${statusClass}">${statusLabel}</span>
            <div class="progress-track">
              <div class="progress-fill" style="width:${Math.max(0, Math.min(item.progress || 0, 100))}%"></div>
            </div>
            <div class="progress-text">${Math.round(item.progress || 0)}%</div>
            <div class="progress-text">${escapeHtml(renderPendingMessage(item))}</div>
            ${item.error ? `<div class="error-text">${escapeHtml(item.error)}</div>` : ""}
          </td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>${item.status === "processing" || item.status === "queued" ? t("table_progressing") : "-"}</td>
        </tr>
      `;
    })
    .join("");

  const processingTitles = new Set(
    state.pendingUploads
      .filter((item) => item.status === "queued" || item.status === "processing")
      .map((item) => (item.bookTitle || "").trim())
      .filter((title) => title.length > 0),
  );

  const savedRows = items
    .filter((item) => !processingTitles.has((item.book_title || "").trim()))
    .map(
      (item) => `
      <tr>
        <td>${escapeHtml(item.book_title)}</td>
        <td>
          <span class="status-chip ${item.status === "processing" ? "status-processing" : "status-completed"}">
            ${escapeHtml(t(`status_${item.status}`) || item.status)}
          </span>
        </td>
        <td>${escapeHtml(formatDate(item.updated_at))}</td>
        <td>${item.chapter_count}</td>
        <td>${item.character_count}</td>
        <td>
          <button class="inline-action" data-open-book="${escapeHtml(item.slug)}" type="button">${t("table_action_open")}</button>
        </td>
      </tr>
    `,
    )
    .join("");

  if (!pendingRows && !savedRows) {
    el.booksTableBody.innerHTML = `
      <tr>
        <td class="empty-row" colspan="6">${escapeHtml(t("empty_books_table"))}</td>
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

function renderReaderPanel(reader, fallbackTitle = "") {
  if (!reader) {
    el.tabReader.innerHTML = `<div class="reader-card"><p class="reader-empty">${escapeHtml(t("reader_loading"))}</p></div>`;
    return;
  }

  if (reader.error) {
    el.tabReader.innerHTML = `<div class="reader-card"><p class="reader-empty">${escapeHtml(reader.error)}</p></div>`;
    return;
  }

  const chapters = Array.isArray(reader.chapters) ? reader.chapters : [];
  if (!chapters.length) {
    const title = reader.book_title || fallbackTitle || "This book";
    el.tabReader.innerHTML = `<div class="reader-card"><p class="reader-empty">${escapeHtml(
      t("reader_no_chapters", { title }),
    )}</p></div>`;
    return;
  }

  el.tabReader.innerHTML = chapters
    .map((chapter) => {
      const idx = Number.isFinite(chapter.index) ? chapter.index : "-";
      const title = chapter.title || "Untitled";
      const text = chapter.text || "";
      return `
        <article class="reader-card">
          <h3 class="reader-title">${escapeHtml(t("reader_chapter_prefix"))} ${idx}: ${escapeHtml(title)}</h3>
          <pre class="reader-text">${escapeHtml(text)}</pre>
        </article>
      `;
    })
    .join("");
}

async function loadReaderForBook(slug, fallbackTitle = "", { force = false } = {}) {
  if (!slug) return;

  const cached = state.readerCache[slug];
  if (cached && !force) {
    renderReaderPanel(cached, fallbackTitle);
    return;
  }

  const reqId = ++state.readerRequestSeq;
  renderReaderPanel(null, fallbackTitle);

  try {
    const payload = await fetchJson(`/books/${encodeURIComponent(slug)}/reader`);
    state.readerCache[slug] = payload;
    if (reqId !== state.readerRequestSeq) return;
    if (!state.currentBook || state.currentBook.slug !== slug) return;
    renderReaderPanel(payload, fallbackTitle);
  } catch (error) {
    const fallback = {
      slug,
      book_title: fallbackTitle || "",
      chapter_count: 0,
      chapters: [],
      error: error.message || t("reader_load_failed"),
    };
    state.readerCache[slug] = fallback;
    if (reqId !== state.readerRequestSeq) return;
    if (!state.currentBook || state.currentBook.slug !== slug) return;
    renderReaderPanel(fallback, fallbackTitle);
  }
}

function renderDetail(detail) {
  el.detailTitle.textContent = detail.book_title;
  el.detailSubtitle.textContent = `slug: ${detail.slug}`;
  el.detailChapterCount.textContent = String(detail.chapter_count);
  el.detailCharacterCount.textContent = String(detail.character_count);
  el.detailUpdatedAt.textContent = formatDate(detail.updated_at);

  el.insightBookTitle.textContent = detail.book_title;
  el.insightBookStats.textContent = t("insight_stats", {
    chapters: detail.chapter_count,
    characters: detail.character_count,
  });

  if (!detail.chapters.length) {
    el.tabChapter.innerHTML = `<div class="chapter-card"><p class="chapter-snippet">${escapeHtml(
      t("empty_chapter_summary"),
    )}</p></div>`;
  } else {
    el.tabChapter.innerHTML = detail.chapters
      .map((chapter) => {
        const summary = extractSection(chapter.markdown, "요약") || t("summary_text_missing");
        return `
          <article class="chapter-card">
            <h3 class="chapter-title">${escapeHtml(t("reader_chapter_prefix"))} ${chapter.index}: ${escapeHtml(chapter.title)}</h3>
            <p class="chapter-snippet">${escapeHtml(summary)}</p>
            <details>
              <summary>${escapeHtml(t("view_original"))} (${escapeHtml(chapter.file_name)})</summary>
              <pre>${escapeHtml(chapter.markdown)}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  if (!detail.characters.length) {
    el.tabCharacter.innerHTML = `<div class="character-card"><p class="character-snippet">${escapeHtml(
      t("empty_character_summary"),
    )}</p></div>`;
  } else {
    el.tabCharacter.innerHTML = detail.characters
      .map((character) => {
        const preview = character.markdown.split("\n").slice(0, 6).join("\n");
        return `
          <article class="character-card">
            <h3 class="character-title">${escapeHtml(character.name)}</h3>
            <p class="character-snippet">${escapeHtml(preview).replaceAll("\n", "<br>")}</p>
            <details>
              <summary>${escapeHtml(t("view_original"))} (${escapeHtml(character.file_name)})</summary>
              <pre>${escapeHtml(character.markdown)}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  el.tabWorld.innerHTML = `<div class="markdown-view">${markdownToHtml(detail.setting_markdown || t("world_missing"))}</div>`;
  renderReaderPanel(state.readerCache[detail.slug] || null, detail.book_title);

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
  el.tabReader.classList.toggle("active", tabName === "reader");
}

async function openBook(slug, { switchToDetail = false } = {}) {
  const detail = await fetchJson(`/books/${encodeURIComponent(slug)}`);
  state.currentBook = detail;
  renderDetail(detail);
  void loadReaderForBook(detail.slug, detail.book_title, { force: true });

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
  const uploadParallel = clampUploadParallel(state.settings.uploadParallel);
  const preciseAnalysis = Boolean(state.settings.preciseAnalysis);
  return { provider, model, apiKey, language, uploadParallel, preciseAnalysis };
}

function buildSingleUploadFormData(file, config) {
  const formData = new FormData();
  formData.append("file", file);
  if (config.uploadId) formData.append("upload_id", config.uploadId);
  formData.append("provider", config.provider);
  formData.append("language", config.language);
  formData.append("precise_analysis", String(Boolean(config.preciseAnalysis)));
  if (config.model) formData.append("model", config.model);
  if (config.apiKey) formData.append("api_key", config.apiKey);
  return formData;
}

function scheduleCompletedCleanup(pendingRow) {
  if (pendingRow.completionTimerId) return;
  const completionTimerId = window.setTimeout(async () => {
    removePendingUpload(pendingRow.id);
    try {
      await loadLibrary({ autoOpenFirst: false });
    } catch (_error) {
      // 라이브러리 갱신 실패는 다음 갱신에서 복구된다.
    }
  }, 1200);
  updatePendingUpload(pendingRow.id, { completionTimerId });
}

function startProgressPolling(pendingRow) {
  if (pendingRow.timerId) {
    return () => {};
  }

  let stopped = false;
  let timerId = null;

  const stop = () => {
    stopped = true;
    if (timerId) {
      window.clearInterval(timerId);
      timerId = null;
    }
    updatePendingUpload(pendingRow.id, { timerId: null });
  };

  const poll = async () => {
    if (stopped) return;
    try {
      const payload = await fetchJson(`/uploads/${encodeURIComponent(pendingRow.uploadId)}/progress`);
      const patch = {
        status: payload.status || "processing",
        progress: Number.isFinite(payload.progress) ? payload.progress : 0,
        message: payload.message || "",
        stage: payload.stage || "processing",
        error: payload.error || "",
        chapterIndex: payload.chapter_index ?? null,
        chapterTotal: payload.chapter_total ?? null,
        chapterTitle: payload.chapter_title || "",
        characterIndex: payload.character_index ?? null,
        characterTotal: payload.character_total ?? null,
        characterName: payload.character_name || "",
      };

      if (typeof payload.book_title === "string" && payload.book_title.trim()) {
        patch.bookTitle = payload.book_title.trim();
        patch.displayName = payload.book_title.trim();
      }

      updatePendingUpload(pendingRow.id, patch);

      if (payload.status === "completed") {
        stop();
        scheduleCompletedCleanup(pendingRow);
        return;
      }
      if (payload.status === "failed") {
        stop();
      }
    } catch (_error) {
      // Upload 시작 직후에는 progress 레코드가 아직 없을 수 있어 다음 폴링에서 재시도한다.
    }
  };

  timerId = window.setInterval(() => {
    void poll();
  }, 800);
  updatePendingUpload(pendingRow.id, { timerId });
  void poll();

  return stop;
}

async function uploadSingleFile(file, config, pendingRow) {
  updatePendingUpload(pendingRow.id, {
    status: "processing",
    progress: 1,
    message: t("upload_start"),
    error: "",
  });
  const stopPolling = startProgressPolling(pendingRow);

  try {
    const formData = buildSingleUploadFormData(file, { ...config, uploadId: pendingRow.uploadId });
    const payload = await fetchJson("/summaries/from-epub", {
      method: "POST",
      body: formData,
    });

    stopPolling();
    updatePendingUpload(pendingRow.id, {
      status: "completed",
      progress: 100,
      stage: "done",
      message: t("summary_done"),
      timerId: null,
    });
    scheduleCompletedCleanup(pendingRow);
    return { ok: true, payload };
  } catch (error) {
    stopPolling();
    updatePendingUpload(pendingRow.id, {
      status: "failed",
      progress: 100,
      stage: "failed",
      message: t("summary_failed"),
      error: error.message || t("summary_failed"),
      timerId: null,
    });
    return { ok: false, error };
  }
}

async function runWithConcurrency(items, limit, worker) {
  const size = Math.max(1, Math.min(limit, items.length || 1));
  const results = new Array(items.length);
  let cursor = 0;

  async function runner() {
    while (true) {
      const index = cursor;
      cursor += 1;
      if (index >= items.length) {
        return;
      }
      results[index] = await worker(items[index], index);
    }
  }

  const workers = Array.from({ length: size }, () => runner());
  await Promise.all(workers);
  return results;
}

async function uploadFiles(files) {
  if (!files.length) return;

  let config;
  try {
    config = getRunConfig();
  } catch (error) {
    showToast(error.message || t("config_error"), true);
    return;
  }

  const pendingRows = files.map((file) => addPendingUpload(file.name));

  let successCount = 0;
  let failureCount = 0;
  let firstErrorMessage = "";

  try {
    setUploading(true);

    const results = await runWithConcurrency(
      files,
      Math.min(clampUploadParallel(config.uploadParallel), files.length),
      async (file, index) => uploadSingleFile(file, config, pendingRows[index]),
    );

    for (const result of results) {
      if (result.ok) {
        successCount += 1;
      } else {
        failureCount += 1;
        if (!firstErrorMessage) {
          firstErrorMessage = result.error?.message || t("summary_failed");
        }
      }
    }

    if (successCount > 0) {
      await loadLibrary({ autoOpenFirst: false });
    }

    const summaryMessage =
      failureCount > 0 && firstErrorMessage
        ? t("result_with_error", { success: successCount, failure: failureCount, error: firstErrorMessage })
        : t("result_summary", { success: successCount, failure: failureCount });
    showToast(summaryMessage, failureCount > 0);
    if (successCount > 0) switchView("library");
  } catch (error) {
    showToast(error.message || t("upload_error"), true);
  } finally {
    setUploading(false);
  }
}

async function restoreActiveUploads() {
  let payload;
  try {
    payload = await fetchJson("/uploads/active");
  } catch (_error) {
    return;
  }

  if (!Array.isArray(payload) || payload.length === 0) {
    return;
  }

  for (const row of payload) {
    if (!row || typeof row !== "object") continue;
    const uploadId = typeof row.upload_id === "string" ? row.upload_id.trim() : "";
    if (!uploadId) continue;

    const status = typeof row.status === "string" ? row.status : "queued";
    if (status !== "queued" && status !== "processing") continue;

    const fileName =
      typeof row.file_name === "string" && row.file_name.trim() ? row.file_name.trim() : "unknown.epub";
    const bookTitle =
      typeof row.book_title === "string" && row.book_title.trim() ? row.book_title.trim() : "";
    const options = {
      uploadId,
      status,
      progress: Number.isFinite(row.progress) ? row.progress : 0,
      message: row.message || "",
      stage: row.stage || "queued",
      error: row.error || "",
      bookTitle,
      displayName: bookTitle || fileName,
      chapterIndex: row.chapter_index ?? null,
      chapterTotal: row.chapter_total ?? null,
      chapterTitle: row.chapter_title || "",
      characterIndex: row.character_index ?? null,
      characterTotal: row.character_total ?? null,
      characterName: row.character_name || "",
    };

    const existing = findPendingUploadByUploadId(uploadId);
    if (existing) {
      updatePendingUpload(existing.id, options);
      startProgressPolling(existing);
      continue;
    }

    const pendingRow = addPendingUpload(fileName, options);
    startProgressPolling(pendingRow);
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

  el.settingsUiLanguageInput.addEventListener("change", () => {
    syncSettingsFromForm();
    renderBooksTable(state.items);
    if (state.currentBook) {
      renderDetail(state.currentBook);
    }
    loadLibrary({ autoOpenFirst: false }).catch(() => {});
  });

  el.settingsLanguageInput.addEventListener("change", () => {
    syncSettingsFromForm();
  });

  el.settingsUploadParallelInput.addEventListener("change", () => {
    syncSettingsFromForm();
  });

  el.settingsPreciseAnalysisInput.addEventListener("change", () => {
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
    showToast(t("settings_saved"));
  });
}

function bindEvents() {
  el.navLibrary.addEventListener("click", () => switchView("library"));

  el.navDetail.addEventListener("click", () => {
    if (!state.currentBook) {
      showToast(t("select_book_first"), true);
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
  await restoreActiveUploads();

  try {
    await loadLibrary();
    if (state.items.length > 0) {
      await openBook(state.items[0].slug);
    }
  } catch (error) {
    showToast(error.message || t("init_load_failed"), true);
  }
}

void init();
