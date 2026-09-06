(() => {
  const form = document.getElementById("login-form");
  const usernameInput = document.getElementById("login-username");
  const passwordInput = document.getElementById("login-password");
  const submitBtn = document.getElementById("login-submit-btn");
  const errorEl = document.getElementById("login-error");

  function nextPath() {
    const next = new URLSearchParams(window.location.search).get("next");
    if (next && next.startsWith("/") && !next.startsWith("//")) return next;
    return "/panel";
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorEl.textContent = "";
    submitBtn.disabled = true;
    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: usernameInput.value.trim(),
          password: passwordInput.value,
        }),
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        errorEl.textContent = payload.detail || "로그인에 실패했습니다.";
        return;
      }
      window.location.href = nextPath();
    } catch (_error) {
      errorEl.textContent = "네트워크 오류로 로그인할 수 없습니다.";
    } finally {
      submitBtn.disabled = false;
    }
  });
})();
