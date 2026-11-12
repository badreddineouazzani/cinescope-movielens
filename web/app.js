const number = new Intl.NumberFormat("fr-FR");
const decimal = new Intl.NumberFormat("fr-FR", {maximumFractionDigits: 3});
const percent = new Intl.NumberFormat("fr-FR", {style:"percent",maximumFractionDigits:2});
const $ = id => document.getElementById(id);
const element = (tag, text, css) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (css) node.className = css;
  return node;
};

async function api(path, params = {}, signal) {
  const suffix = new URLSearchParams(params);
  const response = await fetch("/api/" + path + "?" + suffix, {signal});
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : "Impossible de charger ces données.");
  }
  return response.json();
}

function message(target, text, css = "empty") {
  target.replaceChildren(element("p", text, css));
}

function renderList(target, rows, scoreFormat) {
  if (!rows.length) {
    message(target, "Aucun film pour cette sélection.");
    return;
  }
  const list = element("ol", undefined, "ranking");
  rows.forEach((film, index) => {
    const item = element("li");
    const details = element("div");
    details.append(element("div", film.title, "film-title"),
      element("div", film.genres.map(g => g.replaceAll("_", " ")).join(" · "), "genres"));
    const [value, label] = scoreFormat(film);
    const score = element("div", undefined, "score");
    score.append(element("strong", value), element("small", label));
    item.append(element("span", String(index + 1).padStart(2,"0"), "rank"), details, score);
    list.append(item);
  });
  target.replaceChildren(list);
}
const community = film => [
  film.rating === null ? "—" : decimal.format(film.rating) + " / 5",
  number.format(film.votes) + " votes"
];

let popularRequest;
async function loadPopular() {
  popularRequest?.abort();
  const request = new AbortController();
  popularRequest = request;
  try {
    renderList($("popular"), await api("popular", {min_votes:$("votes").value}, request.signal), community);
  } catch (error) {
    if (error.name !== "AbortError") message($("popular"), error.message, "error");
  }
}
$("votes").addEventListener("change", loadPopular);

function distribution(rows) {
  const max = Math.max(...rows.map(row => row.count));
  const chart = element("div", undefined, "chart");
  rows.forEach(row => {
    const group = element("div", undefined, "bar-row");
    const track = element("div", undefined, "bar-track");
    const bar = element("div", undefined, "bar");
    bar.style.width = (row.count / max * 100) + "%";
    track.append(bar);
    group.append(element("span", row.rating + "/5"),track,element("strong",number.format(row.count)));
    chart.append(group);
  });
  $("distribution").replaceChildren(chart);
}

async function loadStats() {
  try {
    const stats = await api("stats");
    document.querySelectorAll("[data-stat]").forEach(node => {
      node.textContent = number.format(stats[node.dataset.stat]);
    });
    distribution(stats.distribution);
    renderList($("most-rated"), stats.most_rated, film => [number.format(film.votes), "votes"]);
  } catch (error) {
    message($("distribution"), error.message, "error");
  }
}

let searchRequest;
async function search(query, preferred) {
  searchRequest?.abort();
  const request = new AbortController();
  searchRequest = request;
  const film = $("film");
  try {
    const results = await api("movies", {q:query,limit:30}, request.signal);
    if (request.signal.aborted) return;
    film.replaceChildren();
    for (const result of results) {
      const option = element("option", result.title);
      option.value = result.id;
      film.append(option);
    }
    if (!results.length) film.append(element("option", "Aucun film trouvé"));
    if (!results.length) film.options[0].value = "";
    if (results.some(result => result.id === preferred)) film.value = preferred;
  } catch (error) {
    if (error.name !== "AbortError") message($("recommendations"), error.message, "error");
  }
}
let timer;
$("query").addEventListener("input", event => {
  clearTimeout(timer);
  searchRequest?.abort();
  $("film").replaceChildren();
  timer = setTimeout(() => search(event.target.value), 150);
});

function setMode() {
  const mode = $("mode").value;
  const content = mode !== "collaborative";
  const collaborative = mode !== "content";
  $("title-fields").hidden = !content;
  $("film").disabled = !content;
  $("profile-fields").hidden = !collaborative;
  $("profile").disabled = !collaborative;
  $("profile").required = collaborative;
}
$("mode").addEventListener("change", setMode);
setMode();

let recoRequest;
$("reco-form").addEventListener("submit", async event => {
  event.preventDefault();
  recoRequest?.abort();
  const request = new AbortController();
  recoRequest = request;
  const mode = $("mode").value;
  const params = {mode};
  if (mode !== "collaborative") params.movie_id = $("film").value;
  if (mode !== "content") params.user_id = $("profile").value;
  message($("recommendations"), "Recherche en cours…");
  try {
    const result = await api("recommendations", params, request.signal);
    if (request.signal.aborted) return;
    const formats = {
      content: film => [percent.format(film.score), "similarité"],
      collaborative: film => [decimal.format(film.score) + " / 5", "note prédite"],
      hybrid: film => [decimal.format(film.score), "score de fusion"]
    };
    renderList($("recommendations"), result.movies, formats[mode]);
  } catch (error) {
    if (error.name !== "AbortError") message($("recommendations"), error.message, "error");
  }
});

function metricTable(target, rows, keys, format) {
  if (!rows.length) {
    message(target, "Exécutez evaluate.py pour calculer les résultats.");
    return;
  }
  const scroll = element("div", undefined, "table-scroll");
  const table = element("table");
  const header = table.createTHead().insertRow();
  keys.forEach(key => header.append(element("th", key)));
  const body = table.createTBody();
  rows.forEach(row => {
    const tr = body.insertRow();
    keys.forEach(key => tr.append(element("td", format(row[key], key))));
  });
  scroll.append(table);
  target.replaceChildren(scroll);
}

async function evaluate() {
  try {
    const results = await api("evaluation");
    metricTable($("rating-metrics"),results.ratings,["modèle","RMSE","MAE","notes test"],
      (value,key) => key === "modèle" ? value : key === "notes test" ? number.format(value) : decimal.format(value));
    metricTable($("rank-metrics"),results.ranking,["modèle","Precision@10","utilisateurs test"],
      (value,key) => key === "modèle" ? value : key === "Precision@10" ? percent.format(value) : number.format(value));
  } catch (error) {
    message($("rating-metrics"), error.message, "error");
  }
}

function route() {
  const routes = ["accueil","recommandations","analyse","evaluation"];
  const requested = location.hash.slice(1);
  const current = routes.includes(requested) ? requested : routes[0];
  document.querySelectorAll("[data-page]").forEach(page => {page.hidden = page.id !== current;});
  document.querySelectorAll("[data-route]").forEach(link => {
    if (link.dataset.route === current) link.setAttribute("aria-current","page");
    else link.removeAttribute("aria-current");
  });
  if (current === "evaluation") evaluate();
  window.scrollTo(0,0);
}
window.addEventListener("hashchange",route);
route();
loadPopular();
loadStats();
$("query").value = "Toy Story";
search("Toy Story", 1);
