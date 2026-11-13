import { useState } from "react";
import { useApi } from "../useApi";
import FilmList, { number } from "./FilmList";

export function Discover({ stats, error }) {
  const [votes, setVotes] = useState("20");
  const { data: films, error: rankingError } = useApi("popular", "min_votes=" + votes);
  return <section>
    <div className="hero">
      <div className="hero-content">
        <span className="dataset-tag">MovieLens 100K</span>
        <h1>Quel film regarder<br /><em>ce soir&nbsp;?</em></h1>
        <p>Explorez les films les mieux notés ou trouvez des titres proches de vos favoris.</p>
        <a className="primary" href="#recommandations">Trouver un film <span aria-hidden="true">→</span></a>
      </div>
      <div className="hero-photo" role="img" aria-label="Salle de cinéma aux fauteuils rouges" />
    </div>
    <dl className="stats" aria-label="Chiffres du catalogue">
      {[["movies", "Films"], ["ratings", "Notes"], ["users", "Utilisateurs"]].map(([key, label]) =>
        <div key={key}><dt>{label}</dt><dd>{stats ? number.format(stats[key]) : "—"}</dd></div>)}
    </dl>
    {error && <p className="error" role="status">{error}</p>}
    <section className="section">
      <div className="section-head">
        <h2>Les mieux notés</h2>
        <label className="threshold">Votes minimum
          <select value={votes} onChange={event => setVotes(event.target.value)}>
            {[10, 20, 50, 100, 200].map(value => <option key={value}>{value}</option>)}
          </select>
        </label>
      </div>
      <div aria-live="polite">
        {rankingError && <p className="error">{rankingError}</p>}
        {films ? <FilmList films={films} /> : !rankingError && <p className="empty">Chargement…</p>}
      </div>
    </section>
  </section>;
}

export function Analysis({ stats, error }) {
  const max = stats ? Math.max(...stats.distribution.map(row => row.count), 1) : 1;
  return <section>
    <div className="page-head">
      <h1>Analyse du catalogue</h1>
      <p>Distribution des notes et films les plus souvent évalués.</p>
    </div>
    {error && <p className="error" role="status">{error}</p>}
    {!stats && !error && <p className="empty">Chargement…</p>}
    {stats && <>
      <section className="section">
        <h2>Distribution des notes</h2>
        <div className="chart">
          {stats.distribution.map(row => <div className="bar-row" key={row.rating}>
            <span>{row.rating}/5</span>
            <div className="bar-track"><div className="bar" style={{ width: row.count / max * 100 + "%" }} /></div>
            <strong>{number.format(row.count)}</strong>
          </div>)}
        </div>
      </section>
      <section className="section">
        <h2>Les plus notés</h2>
        <FilmList films={stats.most_rated} votesOnly />
      </section>
    </>}
  </section>;
}
