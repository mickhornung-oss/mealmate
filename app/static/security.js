function getCookie(name) {
  const parts = document.cookie ? document.cookie.split("; ") : [];
  for (const part of parts) {
    const splitIndex = part.indexOf("=");
    if (splitIndex === -1) {
      continue;
    }
    const key = decodeURIComponent(part.slice(0, splitIndex));
    if (key === name) {
      return decodeURIComponent(part.slice(splitIndex + 1));
    }
  }
  return "";
}

function addCsrfInput(form, token) {
  if (!token) {
    return;
  }
  const method = (form.getAttribute("method") || "get").toUpperCase();
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    return;
  }
  let csrfInput = form.querySelector('input[name="csrf_token"]');
  if (!csrfInput) {
    csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrf_token";
    form.appendChild(csrfInput);
  }
  csrfInput.value = token;
}

function injectCsrfIntoForms() {
  const token = getCookie("csrf_token");
  document.querySelectorAll("form").forEach((form) => addCsrfInput(form, token));
}

function initCategorySelector() {
  const select = document.getElementById("category_select");
  const wrapper = document.getElementById("new-category-wrapper");
  const input = document.getElementById("category_new");
  if (!select || !wrapper || !input || select.dataset.categoryInit === "1") {
    return;
  }
  const syncCategoryMode = () => {
    const useNewCategory = select.value === "__new__";
    wrapper.classList.toggle("hidden", !useNewCategory);
    input.required = useNewCategory;
    if (!useNewCategory) {
      input.value = "";
    }
  };
  select.addEventListener("change", syncCategoryMode);
  select.dataset.categoryInit = "1";
  syncCategoryMode();
}

document.addEventListener("DOMContentLoaded", () => {
  injectCsrfIntoForms();
  initCategorySelector();
});

document.addEventListener(
  "submit",
  (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    addCsrfInput(form, getCookie("csrf_token"));
  },
  true
);

document.body.addEventListener("htmx:configRequest", (event) => {
  const token = getCookie("csrf_token");
  if (!token) {
    return;
  }
  event.detail.headers["X-CSRF-Token"] = token;
});

document.body.addEventListener("htmx:afterSwap", () => {
  injectCsrfIntoForms();
  initCategorySelector();
});
