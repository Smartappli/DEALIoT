const header = document.querySelector("[data-header]");
const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
const revealTargets = Array.from(document.querySelectorAll(".reveal"));
const languageSelects = Array.from(document.querySelectorAll("[data-language-select]"));
const allowedLanguageRoutes = new Map([
  ["/", "https://smartappli.io/"],
  ["/bg/", "https://smartappli.io/bg/"],
  ["/hr/", "https://smartappli.io/hr/"],
  ["/cs/", "https://smartappli.io/cs/"],
  ["/da/", "https://smartappli.io/da/"],
  ["/nl/", "https://smartappli.io/nl/"],
  ["/et/", "https://smartappli.io/et/"],
  ["/fi/", "https://smartappli.io/fi/"],
  ["/fr/", "https://smartappli.io/fr/"],
  ["/de/", "https://smartappli.io/de/"],
  ["/el/", "https://smartappli.io/el/"],
  ["/hu/", "https://smartappli.io/hu/"],
  ["/ga/", "https://smartappli.io/ga/"],
  ["/it/", "https://smartappli.io/it/"],
  ["/lv/", "https://smartappli.io/lv/"],
  ["/lt/", "https://smartappli.io/lt/"],
  ["/mt/", "https://smartappli.io/mt/"],
  ["/pl/", "https://smartappli.io/pl/"],
  ["/pt/", "https://smartappli.io/pt/"],
  ["/ro/", "https://smartappli.io/ro/"],
  ["/sk/", "https://smartappli.io/sk/"],
  ["/sl/", "https://smartappli.io/sl/"],
  ["/es/", "https://smartappli.io/es/"],
  ["/sv/", "https://smartappli.io/sv/"],
]);

function updateHeaderShadow() {
  if (!header) {
    return;
  }

  header.classList.toggle("is-scrolled", window.scrollY > 16);
}

function getSiteBasePath() {
  return "/";
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  const basePath = getSiteBasePath();
  navigator.serviceWorker.register(`${basePath}sw.js`, { scope: basePath }).catch(() => {});
}

function navigateToSelectedLanguage(value) {
  let target;
  try {
    target = new URL(value, "https://smartappli.io/");
  } catch {
    return;
  }

  const allowedHref = allowedLanguageRoutes.get(target.pathname);
  if (target.origin !== "https://smartappli.io" || !allowedHref) {
    return;
  }

  window.location.assign(allowedHref);
}

function setupLanguageSelects() {
  for (const select of languageSelects) {
    select.addEventListener("change", (event) => {
      navigateToSelectedLanguage(event.currentTarget.value);
    });
  }
}

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.18 },
  );

  for (const target of revealTargets) {
    revealObserver.observe(target);
  }

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const visibleEntry = entries.find((entry) => entry.isIntersecting);
      if (!visibleEntry) {
        return;
      }

      const id = visibleEntry.target.getAttribute("id");
      for (const link of navLinks) {
        link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
      }
    },
    { rootMargin: "-35% 0px -55% 0px", threshold: 0.01 },
  );

  for (const section of document.querySelectorAll("main section[id]")) {
    sectionObserver.observe(section);
  }
} else {
  for (const target of revealTargets) {
    target.classList.add("is-visible");
  }
}

window.addEventListener("scroll", updateHeaderShadow, { passive: true });
window.addEventListener("load", registerServiceWorker);
setupLanguageSelects();
updateHeaderShadow();
