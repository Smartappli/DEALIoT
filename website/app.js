const header = document.querySelector("[data-header]");
const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
const revealTargets = Array.from(document.querySelectorAll(".reveal"));

function updateHeaderShadow() {
  if (!header) {
    return;
  }

  header.classList.toggle("is-scrolled", window.scrollY > 16);
}

function getSiteBasePath() {
  return window.location.pathname.startsWith("/DEALIoT/") ? "/DEALIoT/" : "/";
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  const basePath = getSiteBasePath();
  navigator.serviceWorker.register(`${basePath}sw.js`, { scope: basePath }).catch(() => {});
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
updateHeaderShadow();
