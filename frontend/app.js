const number = new Intl.NumberFormat("fr-FR");
const decimal = new Intl.NumberFormat("fr-FR", {maximumFractionDigits: 3});
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

function renderList(target, rows, scoreFormat, emptyMessage = "Aucun film pour cette sélection.") {
  if (!rows.length) {
    message(target, emptyMessage);
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

const genreLabels = {
  Action: "Action", Adventure: "Aventure", Animation: "Animation", Children: "Jeunesse",
  Comedy: "Comédie", Crime: "Policier", Documentary: "Documentaire", Drama: "Drame",
  Fantasy: "Fantastique", Film_Noir: "Film noir", Horror: "Horreur", Musical: "Comédie musicale",
  Mystery: "Mystère", Romance: "Romance", Sci_Fi: "Science-fiction", Thriller: "Thriller",
  War: "Guerre", Western: "Western"
};

async function loadRecommendationFilters() {
  try {
    const {genres, decades} = await api("recommendation-filters");
    const options = genres.map(value => [genreLabels[value] ?? value, value]);
    options.sort(([left], [right]) => left.localeCompare(right, "fr"));
    $("recommendation-genre").append(...options.map(([label, value]) => new Option(label, value)));
    $("recommendation-decade").append(...decades.map(decade => new Option("Années " + decade, decade)));
  } catch {
    $("recommendation-genre").disabled = true;
    $("recommendation-decade").disabled = true;
    const status = $("filter-status");
    status.textContent = "Les filtres sont indisponibles. Rechargez la page pour réessayer.";
    status.hidden = false;
  }
}

const resultFilters = $("recommendation-filters");
const genreFilter = $("recommendation-genre");
const decadeFilter = $("recommendation-decade");
let recoRequest;
let activeMovieId;

async function loadRecommendations(movieId, showLoading = false) {
  recoRequest?.abort();
  const request = new AbortController();
  recoRequest = request;

  const results = $("recommendations");
  const params = {movie_id: movieId};
  if (genreFilter.value) params.genre = genreFilter.value;
  if (decadeFilter.value) params.decade = decadeFilter.value;
  if (showLoading) message(results, "Recherche en cours…");
  results.setAttribute("aria-busy", "true");

  try {
    const result = await api("recommendations", params, request.signal);
    if (request.signal.aborted) return;
    const emptyMessage = params.genre || params.decade
      ? "Aucun film similaire avec ces filtres. Essayez un autre genre ou une autre décennie."
      : "Aucun film similaire pour ce titre.";
    renderList(results, result.movies, community, emptyMessage);
    resultFilters.hidden = false;
  } catch (error) {
    if (error.name !== "AbortError") message(results, error.message, "error");
  } finally {
    if (recoRequest === request) results.removeAttribute("aria-busy");
  }
}

$("reco-form").addEventListener("submit", event => {
  event.preventDefault();
  const movieId = $("film").value;
  if (!movieId) return;
  if (movieId !== activeMovieId) {
    resultFilters.hidden = true;
    genreFilter.value = "";
    decadeFilter.value = "";
    activeMovieId = movieId;
  }
  loadRecommendations(movieId, true);
});

resultFilters.addEventListener("change", () => loadRecommendations(activeMovieId));

function route() {
  const routes = ["accueil","recommandations","analyse"];
  const requested = location.hash.slice(1);
  const current = routes.includes(requested) ? requested : routes[0];
  document.querySelectorAll("[data-page]").forEach(page => {page.hidden = page.id !== current;});
  document.querySelectorAll("[data-route]").forEach(link => {
    if (link.dataset.route === current) link.setAttribute("aria-current","page");
    else link.removeAttribute("aria-current");
  });
  window.scrollTo(0,0);
}
window.addEventListener("hashchange",route);
route();
loadPopular();
loadStats();
loadRecommendationFilters();
$("query").value = "Toy Story";
search("Toy Story", 1);
