import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { Analysis, Discover } from "./components/Catalogue";
import Recommendations from "./components/Recommendations";
import { useApi } from "./useApi";
import "./style.css";

const routes = [
  ["accueil", "Découvrir"],
  ["recommandations", "Recommandations"],
  ["analyse", "Analyse"]
];

function currentRoute() {
  const hash = window.location.hash.slice(1);
  return routes.some(([id]) => id === hash) ? hash : "accueil";
}

function App() {
  const [route, setRoute] = useState(currentRoute);
  const { data: stats, error } = useApi("stats");
  useEffect(() => {
    function updateRoute() {
      setRoute(currentRoute());
      window.scrollTo(0, 0);
    }
    window.addEventListener("hashchange", updateRoute);
    return () => window.removeEventListener("hashchange", updateRoute);
  }, []);
  return <>
    <header className="top">
      <div className="top-inner">
        <a className="brand" href="#accueil"><span className="brand-mark" aria-hidden="true">▶</span>CinéScope</a>
        <nav aria-label="Navigation principale">
          {routes.map(([id, label]) =>
            <a key={id} href={"#" + id} aria-current={route === id ? "page" : undefined}>{label}</a>)}
        </nav>
      </div>
    </header>
    <main>
      <div hidden={route !== "accueil"}><Discover stats={stats} error={error} /></div>
      <div hidden={route !== "recommandations"}><Recommendations /></div>
      <div hidden={route !== "analyse"}><Analysis stats={stats} error={error} /></div>
    </main>
    <footer><span>CinéScope</span><a href="https://grouplens.org/datasets/movielens/100k/">Données GroupLens <span aria-hidden="true">↗</span></a></footer>
  </>;
}

createRoot(document.getElementById("root")).render(<App />);
