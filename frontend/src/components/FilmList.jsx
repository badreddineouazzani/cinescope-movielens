export const number = new Intl.NumberFormat("fr-FR");
const decimal = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 3 });

const genres = {
  Action: "Action", Adventure: "Aventure", Animation: "Animation", Children: "Jeunesse",
  Comedy: "Comédie", Crime: "Policier", Documentary: "Documentaire", Drama: "Drame",
  Fantasy: "Fantastique", Film_Noir: "Film noir", Horror: "Horreur", Musical: "Comédie musicale",
  Mystery: "Mystère", Romance: "Romance", Sci_Fi: "Science-fiction", Thriller: "Thriller",
  War: "Guerre", Western: "Western", unknown: "Genre inconnu"
};

export function genreLabel(value) {
  return genres[value] ?? value;
}

export default function FilmList({ films, empty = "Aucun film pour cette sélection.", votesOnly = false }) {
  if (!films.length) return <p className="empty">{empty}</p>;
  return <ol className="ranking">
    {films.map((film, index) => <li key={film.id}>
      <span className="rank">{String(index + 1).padStart(2, "0")}</span>
      <div>
        <div className="film-title">{film.title}</div>
        <div className="genres">{film.genres.map(genreLabel).join(" · ")}</div>
      </div>
      <div className="score">
        <strong>{votesOnly ? number.format(film.votes) : film.rating === null ? "—" : decimal.format(film.rating) + " / 5"}</strong>
        <small>{votesOnly ? "votes" : number.format(film.votes) + " votes"}</small>
      </div>
    </li>)}
  </ol>;
}
