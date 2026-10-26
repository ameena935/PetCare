/* PetCare frontend – vanilla JS, talks to the Express REST API at /pets */
(() => {
  "use strict";

  const API = "/pets";
  const SPECIES = ["dog", "cat", "bird", "rabbit", "other"];
  const EMOJI = { dog: "🐶", cat: "🐱", bird: "🐦", rabbit: "🐰", other: "🐾" };

  const state = { pets: [], filter: "all", sort: "newest", editingId: null, loading: true };
  const $ = (id) => document.getElementById(id);

  /* ---------- helpers ---------- */
  function el(tag, props = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
      if (value === undefined || value === null || value === false) continue;
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
      else node.setAttribute(key, value === true ? "" : value);
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      node.append(child.nodeType ? child : document.createTextNode(child));
    }
    return node;
  }

  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
  const fmtDate = (iso) =>
    iso ? new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "–";
  const fmtAge = (age) => (age === 0 ? "Under 1 yr" : plural(age, "yr"));
  const GROUP = { dog: "dogs", cat: "cats", bird: "birds", rabbit: "rabbits", other: "other pets" };

  /* ---------- toasts ---------- */
  function toast(message, type = "success") {
    const node = el(
      "div",
      { class: `toast ${type}`, role: type === "error" ? "alert" : "status" },
      el("p", {}, el("strong", { text: type === "error" ? "Something went wrong" : "Done" }), message),
      el("button", { type: "button", "aria-label": "Dismiss", text: "×", onclick: () => close() })
    );
    function close() {
      node.classList.add("leaving");
      setTimeout(() => node.remove(), 200);
    }
    $("toasts").append(node);
    setTimeout(close, type === "error" ? 6500 : 3500);
  }

  /* ---------- API layer ---------- */
  async function api(path = "", options = {}) {
    let res;
    try {
      res = await fetch(API + path, {
        headers: { "Content-Type": "application/json" },
        ...options,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });
    } catch {
      throw new Error("Cannot reach the server. Check that it is running and try again.");
    }
    let data = null;
    try { data = await res.json(); } catch { /* non-JSON body */ }
    if (!res.ok) {
      const msg = (data && data.message) || `Request failed (${res.status})`;
      throw new Error(msg.replace(/^Pet validation failed:\s*/, ""));
    }
    return data;
  }

  const fetchPets = () => api("");
  const createPet = (pet) => api("", { method: "POST", body: pet });
  const updatePet = (id, changes) => api(`/${id}`, { method: "PUT", body: changes });
  const deletePet = (id) => api(`/${id}`, { method: "DELETE" });

  async function loadPets() {
    try {
      state.pets = await fetchPets();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      state.loading = false;
      render();
    }
  }

  /* ---------- actions ---------- */
  async function toggleAdoption(pet) {
    try {
      const updated = await updatePet(pet._id, { adopted: !pet.adopted });
      replacePet(updated);
      toast(updated.adopted
        ? `${updated.name} is now marked as adopted.`
        : `${updated.name} is available for adoption again.`);
    } catch (err) { toast(err.message, "error"); }
  }

  async function removePet(pet) {
    try {
      const res = await deletePet(pet._id);
      state.pets = state.pets.filter((p) => p._id !== pet._id);
      if (state.editingId === pet._id) resetForm();
      render();
      toast(res.message || `${pet.name} was removed.`);
    } catch (err) { toast(err.message, "error"); }
  }

  function replacePet(updated) {
    state.pets = state.pets.map((p) => (p._id === updated._id ? updated : p));
    render();
  }

  /* ---------- metrics ---------- */
  function countUp(node, to) {
    const from = Number(node.dataset.count || 0);
    node.dataset.count = to;
    if (from === to || matchMedia("(prefers-reduced-motion: reduce)").matches) { node.textContent = to; return; }
    const start = performance.now(), dur = 600;
    const tick = (now) => {
      const t = Math.min((now - start) / dur, 1);
      node.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function renderMetrics() {
    const total = state.pets.length;
    const adopted = state.pets.filter((p) => p.adopted).length;
    const available = total - adopted;
    countUp($("mTotal"), total);
    countUp($("mAdopted"), adopted);
    countUp($("mAvailable"), available);

    const tally = (list) => list.reduce((acc, p) => ((acc[p.species] = (acc[p.species] || 0) + 1), acc), {});
    const adoptedTally = tally(state.pets.filter((p) => p.adopted));
    const useAdopted = Object.keys(adoptedTally).length > 0;
    const counts = useAdopted ? adoptedTally : tally(state.pets);
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    $("mPopular").textContent = top ? cap(top[0]) : "–";
    $("mPopularNote").textContent = top
      ? useAdopted ? `${plural(top[1], "adoption")} so far` : `${plural(top[1], "pet")} registered`
      : "no pets yet";

    const pct = total ? Math.round((adopted / total) * 100) : 0;
    $("rateRing").style.setProperty("--pct", pct);
    $("rateRing").setAttribute("aria-label", `${pct}% of pets adopted`);
    $("rateValue").textContent = `${pct}%`;
    $("rateText").textContent = state.loading
      ? "Loading shelter data…"
      : total
        ? `${adopted} of ${plural(total, "pet")} have found a home.`
        : "No pets registered yet. Add the first one below.";
  }

  /* ---------- showcase ---------- */
  function visiblePets() {
    let list = state.pets.filter((p) => state.filter === "all" || p.species === state.filter);
    if (state.sort === "age") list = [...list].sort((a, b) => a.age - b.age);
    else if (state.sort === "name") list = [...list].sort((a, b) => a.name.localeCompare(b.name));
    else list = [...list].sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    return list;
  }

  function petCard(pet) {
    return el(
      "article",
      { class: "card", "data-species": pet.species },
      el("div", { class: "card-art", "aria-hidden": "true" }, EMOJI[pet.species] || EMOJI.other,
        el("span", { class: `badge ${pet.adopted ? "badge-adopted" : "badge-available"}`, text: pet.adopted ? "Adopted" : "Available" })),
      el("div", { class: "card-body" },
        el("h3", { text: pet.name }),
        el("p", { class: "card-meta", text: `${cap(pet.species)}, ${fmtAge(pet.age)}` }),
        pet.adopted && pet.adoptedOn ? el("p", { class: "card-meta", text: `Adopted ${fmtDate(pet.adoptedOn)}` }) : null,
        el("div", { class: "card-actions" },
          el("button", { class: "btn btn-ghost btn-sm", type: "button", text: pet.adopted ? "Mark available" : "Mark adopted", onclick: () => toggleAdoption(pet) }),
          el("button", { class: "btn btn-ghost btn-sm", type: "button", text: "Edit", onclick: () => startFormEdit(pet) })
        )
      )
    );
  }

  function renderShowcase() {
    const grid = $("petGrid");
    grid.replaceChildren();
    if (state.loading) {
      for (let i = 0; i < 4; i++) grid.append(el("div", { class: "skeleton" }));
      $("showcaseCount").textContent = "Loading pets…";
      return;
    }
    const list = visiblePets();
    const group = state.filter === "all" ? "" : ` ${GROUP[state.filter]}`;
    $("showcaseCount").textContent = `Showing ${list.length}${group} of ${plural(state.pets.length, "registered pet")}`;
    if (!list.length) {
      grid.append(el("div", { class: "empty" },
        el("strong", { text: state.pets.length ? "No pets in this group" : "The shelter register is empty" }),
        state.pets.length ? "Try another species filter." : "Use the form below to register the first pet."));
      return;
    }
    list.forEach((p) => grid.append(petCard(p)));
  }

  /* ---------- registry table ---------- */
  let inlineEditId = null;

  function viewRow(pet) {
    let confirming = false, timer;
    const del = el("button", { class: "btn btn-danger btn-sm", type: "button", text: "Delete" });
    del.addEventListener("click", () => {
      if (!confirming) {
        confirming = true;
        del.textContent = "Confirm delete";
        del.classList.add("confirming");
        timer = setTimeout(() => { confirming = false; del.textContent = "Delete"; del.classList.remove("confirming"); }, 3000);
      } else {
        clearTimeout(timer);
        removePet(pet);
      }
    });
    return el("tr", {},
      el("td", { class: "name-cell", text: pet.name }),
      el("td", {}, el("span", { class: "cap", text: pet.species })),
      el("td", { text: fmtAge(pet.age) }),
      el("td", {}, el("span", { class: `badge ${pet.adopted ? "badge-adopted" : "badge-available"}`, text: pet.adopted ? "Adopted" : "Available" })),
      el("td", { class: "date", text: fmtDate(pet.createdAt || pet.arrivedOn) }),
      el("td", {}, el("div", { class: "row-actions" },
        el("button", { class: "btn btn-ghost btn-sm", type: "button", text: "Edit", onclick: () => { inlineEditId = pet._id; renderTable(); } }),
        el("button", { class: "btn btn-ghost btn-sm", type: "button", text: pet.adopted ? "Mark available" : "Mark adopted", onclick: () => toggleAdoption(pet) }),
        del))
    );
  }

  function editRow(pet) {
    const name = el("input", { type: "text", value: pet.name, maxlength: "60", "aria-label": "Name" });
    const species = el("select", { "aria-label": "Species" }, SPECIES.map((s) => el("option", { value: s, text: cap(s), selected: s === pet.species })));
    const age = el("input", { type: "number", min: "0", max: "30", step: "1", value: pet.age, "aria-label": "Age in years" });
    const save = async () => {
      try {
        const updated = await updatePet(pet._id, { name: name.value, species: species.value, age: age.value === "" ? undefined : Number(age.value) });
        inlineEditId = null;
        replacePet(updated);
        toast(`${updated.name} was updated.`);
      } catch (err) { toast(err.message, "error"); }
    };
    const onKey = (e) => { if (e.key === "Enter") save(); if (e.key === "Escape") { inlineEditId = null; renderTable(); } };
    [name, age].forEach((i) => i.addEventListener("keydown", onKey));
    setTimeout(() => name.focus(), 0);
    return el("tr", { class: "is-editing" },
      el("td", {}, name), el("td", {}, species), el("td", {}, age),
      el("td", {}, el("span", { class: `badge ${pet.adopted ? "badge-adopted" : "badge-available"}`, text: pet.adopted ? "Adopted" : "Available" })),
      el("td", { class: "date", text: fmtDate(pet.createdAt || pet.arrivedOn) }),
      el("td", {}, el("div", { class: "row-actions" },
        el("button", { class: "btn btn-primary btn-sm", type: "button", text: "Save", onclick: save }),
        el("button", { class: "btn btn-ghost btn-sm", type: "button", text: "Cancel", onclick: () => { inlineEditId = null; renderTable(); } })))
    );
  }

  function renderTable() {
    const body = $("tableBody");
    body.replaceChildren();
    if (state.loading) {
      body.append(el("tr", {}, el("td", { colspan: "6", text: "Loading pets…" })));
      return;
    }
    if (!state.pets.length) {
      body.append(el("tr", {}, el("td", { colspan: "6", text: "No pets registered yet. Add one using the form." })));
      return;
    }
    const rows = [...state.pets].sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    rows.forEach((p) => body.append(p._id === inlineEditId ? editRow(p) : viewRow(p)));
  }

  /* ---------- form ---------- */
  const form = $("petForm");

  function resetForm() {
    state.editingId = null;
    form.reset();
    $("formTitle").textContent = "Register a pet";
    $("formHint").textContent = "Fill in the details and save. The pet appears in the showcase straight away.";
    $("saveBtn").textContent = "Save pet";
    $("cancelEdit").hidden = true;
    document.querySelector(".registry-form").classList.remove("editing");
    form.querySelectorAll(".invalid").forEach((n) => n.classList.remove("invalid"));
  }

  function startFormEdit(pet) {
    state.editingId = pet._id;
    $("fName").value = pet.name;
    $("fSpecies").value = pet.species;
    $("fAge").value = pet.age;
    form.elements.adopted.value = String(pet.adopted);
    $("formTitle").textContent = `Edit ${pet.name}`;
    $("formHint").textContent = "Change the details and save, or cancel to leave this record as it is.";
    $("saveBtn").textContent = "Update pet";
    $("cancelEdit").hidden = false;
    document.querySelector(".registry-form").classList.add("editing");
    $("registry").scrollIntoView({ behavior: "smooth" });
    $("fName").focus({ preventScroll: true });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    form.querySelectorAll(".invalid").forEach((n) => n.classList.remove("invalid"));
    const name = $("fName").value.trim();
    const ageRaw = $("fAge").value;
    if (!name) { $("fName").classList.add("invalid"); $("fName").focus(); return toast("Enter the pet's name.", "error"); }
    if (ageRaw === "" || Number(ageRaw) < 0 || Number(ageRaw) > 30) {
      $("fAge").classList.add("invalid"); $("fAge").focus();
      return toast("Enter an age between 0 and 30.", "error");
    }
    const payload = { name, species: $("fSpecies").value, age: Number(ageRaw), adopted: form.elements.adopted.value === "true" };
    const btn = $("saveBtn");
    btn.disabled = true;
    try {
      if (state.editingId) {
        const updated = await updatePet(state.editingId, payload);
        replacePet(updated);
        toast(`${updated.name} was updated.`);
      } else {
        const created = await createPet(payload);
        state.pets.unshift(created);
        render();
        toast(`${created.name} was registered.`);
      }
      resetForm();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      btn.disabled = false;
    }
  });

  $("cancelEdit").addEventListener("click", resetForm);

  /* ---------- filters & sort ---------- */
  $("chips").addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    state.filter = chip.dataset.species;
    document.querySelectorAll(".chip").forEach((c) => {
      const on = c === chip;
      c.classList.toggle("is-active", on);
      c.setAttribute("aria-pressed", String(on));
    });
    renderShowcase();
  });
  $("sortSelect").addEventListener("change", (e) => { state.sort = e.target.value; renderShowcase(); });

  function render() {
    renderMetrics();
    renderShowcase();
    renderTable();
  }

  render();
  loadPets();
})();
