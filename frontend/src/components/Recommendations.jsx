import { useEffect, useState } from "react";
import { fetchApi } from "../api";
import { useApi } from "../useApi";
import FilmList, { genreLabel } from "./FilmList";

export default function Recommendations() {
  const [query, setQuery] = useState("Toy Story");
  const [search, setSearch] = useState({ query: null, films: [], error: null });
  const [movieId, setMovieId] = useState("");
  const [selection, setSelection] = useState(null);
  const [response, setResponse] = useState({ selection: null, films: null, error: null });
  const { data: options, error: filtersError } = useApi("recommendation-filters");

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      fetchApi("movies", { q: query, limit: 30 }, controller.signal).then(films => {
        if (controller.signal.aborted) return;
        setSearch({ query, films, error: null });
        setMovieId(String(films[0]?.id ?? ""));
      }).catch(error => {
        if (!controller.signal.aborted) setSearch({ query, films: [], error: error.message });
      });
    }, 150);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  useEffect(() => {
    if (!selection) return;
    const controller = new AbortController();
    const { movie, genre, decade } = selection;
    const params = { movie_id: movie };
    if (genre) params.genre = genre;
    if (decade) params.decade = decade;
    fetchApi("recommendations", params, controller.signal).then(({ movies }) => {
      if (!controller.signal.aborted) setResponse({ selection, films: movies, error: null });
    }).catch(error => {
      if (!controller.signal.aborted) setResponse({ selection, films: null, error: error.message });
    });
    return () => controller.abort();
  }, [selection]);

  const searching = search.query !== query;
  const loading = selection !== response.selection;
  const showFilters = selection && selection.movie === response.selection?.movie;
  const genres = options?.genres.map(genre => ({ genre, label: genreLabel(genre) }))
    .sort((first, second) => first.label.localeCompare(second.label, "fr"));

  function submit(event) {
    event.preventDefault();
    if (!searching && movieId) {
      setSelection(previous => previous?.movie === movieId
        ? { ...previous }
        : { movie: movieId, genre: "", decade: "" });
    }
  }

  return <section>
    <div className="page-head">
      <h1>Films similaires</h1>
      <p>Choisissez un film que vous aimez pour découvrir des titres du même genre.</p>
    </div>
    <div className="recommend-grid">
      <form className="controls" onSubmit={submit}>
        <label htmlFor="query">Rechercher par titre</label>
        <input id="query" type="search" placeholder="Ex. Toy Story" autoComplete="off"
          maxLength={120} value={query} onChange={event => setQuery(event.target.value)} />
        <label htmlFor="film">Film</label>
        <select id="film" value={searching ? "" : movieId} required disabled={searching || !search.films.length}
          onChange={event => setMovieId(event.target.value)}>
          {searching || !search.films.length
            ? <option value="">{searching ? "Recherche…" : "Aucun film trouvé"}</option>
            : search.films.map(film => <option key={film.id} value={film.id}>{film.title}</option>)}
        </select>
        {!searching && search.error && <p role="status" className="error">{search.error}</p>}
        <button className="primary" type="submit" disabled={searching || !search.films.length}>
          Afficher les films <span aria-hidden="true">→</span>
        </button>
      </form>
      <section className="reco-results">
        <h2>Films suggérés</h2>
        <div id="recommendations" aria-live="polite" aria-busy={loading}>
          {!selection && <p className="empty">Choisissez un film pour lancer la recherche.</p>}
          {loading && !showFilters && <p className="empty">Recherche en cours…</p>}
          {showFilters && response.error && <p className="error">{response.error}</p>}
          {showFilters && response.films && <FilmList films={response.films}
            empty={response.selection.genre || response.selection.decade
              ? "Aucun film similaire avec ces filtres. Essayez un autre genre ou une autre décennie."
              : "Aucun film similaire pour ce titre."} />}
        </div>
        {showFilters && <fieldset className="result-filters">
          <legend>Filtrer les résultats</legend>
          <div className="result-filter-fields">
            <div>
              <label htmlFor="recommendation-genre">Genre</label>
              <select id="recommendation-genre" value={selection.genre} disabled={!options}
                onChange={event => setSelection({ ...selection, genre: event.target.value })}>
                <option value="">Tous les genres</option>
                {genres?.map(({ genre, label }) => <option key={genre} value={genre}>{label}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="recommendation-decade">Décennie de sortie</label>
              <select id="recommendation-decade" value={selection.decade} disabled={!options}
                onChange={event => setSelection({ ...selection, decade: event.target.value })}>
                <option value="">Toutes les décennies</option>
                {options?.decades.map(decade => <option key={decade} value={decade}>Années {decade}</option>)}
              </select>
            </div>
          </div>
          {filtersError && <p className="error" role="status">{filtersError}</p>}
        </fieldset>}
      </section>
    </div>
  </section>;
}
