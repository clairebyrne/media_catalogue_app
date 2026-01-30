import streamlit as st
import pandas as pd
import random

st.set_page_config(
    page_title="All the films ... ",
    layout="wide"
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    text_cols = ["name", "overview", "cast_top5", "genre"]
    for col in text_cols:
        df[col] = df[col].astype(str)

    df["release_year"] = pd.to_datetime(
        df["release_date"], errors="coerce"
    ).dt.year

    df = df.drop_duplicates(['location', 'name', 'release_date', 'overview','genre', 'vote_average', 'vote_count', 'popularity','cast_top5', 'trailer', 'poster'])

    return df

@st.dialog("Movie details")
def show_movie_details(movie):
    if movie["poster"]!= 'No poster available':
        st.image(movie["poster"], width=250)

    st.markdown(f"**Release year:** {int(movie['release_year'])}")
    st.markdown(f"**Genre:** {movie['genre']}")
    st.markdown(f"**Director:** {movie['director']}")
    st.markdown(f"**Runtime:** {movie['runtime']}")
    st.markdown(f"**Rating:** ⭐ {movie['vote_average']}")
    st.markdown(f"**Find it in:** :file_folder: {movie['location']}")

    st.markdown("### Overview")
    st.write(movie["overview"])

    if movie["cast_top5"]:
        st.markdown(f"**Cast:** {movie['cast_top5']}")

    if movie["trailer"]!="No trailer available":
        st.video(movie["trailer"])

def extract_genres(df: pd.DataFrame) -> list[str]:
    genres = (
        df["genre"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .unique()
    )
    return sorted(genres)

# ---------- Load data ----------
df = load_data("media_df.csv")
# get list of all genres
all_genres = extract_genres(df)

st.title("🎬 The films")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

pick_random = st.sidebar.button("🎲 Pick something for me")

search_text = st.sidebar.text_input(
    "Search title / overview / cast / director"
)

min_rating = st.sidebar.slider(
    "Minimum rating",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.5
)

years = df["release_year"].dropna().astype(int)
year_range = st.sidebar.slider(
    "Release year",
    int(years.min()),
    int(years.max()),
    (int(years.min()), int(years.max()))
)
st.sidebar.subheader("🎭 Genre")
selected_genres = st.sidebar.multiselect(
    "",
    options=all_genres,
    default=[],
    help="Show movies matching any selected genre"
)

st.sidebar.text('This application uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB.', )
st.sidebar.image('resources/tmdb_logo.png', width=100)

# ---------- Filtering logic ----------
filtered = df.copy()

if search_text:
    s = search_text.lower()
    filtered = filtered[
        filtered["name"].str.lower().str.contains(s, na=False)
        | filtered["overview"].str.lower().str.contains(s, na=False)
        | filtered["cast_top5"].str.lower().str.contains(s, na=False)
        | filtered["director"].str.lower().str.contains(s, na=False)
    ]

filtered = filtered[
    (filtered["vote_average"] >= min_rating)
    & (filtered["release_year"] >= year_range[0])
    & (filtered["release_year"] <= year_range[1])
]

if selected_genres:
    filtered = filtered[
        filtered["genre"].apply(
            lambda g: any(
                genre in g for genre in selected_genres
            )
        )
    ]

if pick_random:
    st.session_state["random_pick"] = (
        filtered.sample(1).iloc[0]
        if not filtered.empty
        else None
    )

st.caption(f"{len(filtered)} movies")

# ---------- random select display ---------- 

if "random_pick" in st.session_state and st.session_state["random_pick"] is not None:
    movie = st.session_state["random_pick"]

    st.markdown("## 🎬 Tonight’s pick")
    cols = st.columns([1, 3])

    with cols[0]:
        if movie["poster"]!= 'No poster available':
            st.image(movie["poster"], use_container_width=True)

    with cols[1]:
        st.markdown(f"### {movie['name']} ({int(movie['release_year'])})")
        st.markdown(f"⭐ {movie['vote_average']} · {movie['genre']}")
        st.markdown(f"**Find it in:** :file_folder: {movie['location']}")
        st.write(movie["overview"])
        st.write(f"**Cast**: {movie['cast_top5']}")
        st.write(f"**Director:** {movie['director']}")
        st.write(f"**Runtime:** {movie['runtime']}")
        
        if movie["trailer"]!="No trailer available":
            st.video(movie["trailer"])

    st.divider()


# ---------- Grid display ----------
cols_per_row = 4
rows = [
    filtered.iloc[i:i + cols_per_row]
    for i in range(0, len(filtered), cols_per_row)
]

for row in rows:
    cols = st.columns(cols_per_row)
    for col, (_, movie) in zip(cols, row.iterrows()):
        with col:
            if movie["poster"]!= 'No poster available':
                st.image(movie["poster"], use_container_width=True)

            st.markdown(
                f"**{movie['name']}** ({int(movie['release_year']) if pd.notna(movie['release_year']) else '—'})"
            )
            st.caption(
                f"⭐ {movie['vote_average']}  ·  {movie['genre']}  ·  {movie['runtime']}"
            )
            st.caption(f"{movie['director']}")

            if st.button("Details", key=f"details_{movie.name}"):
                show_movie_details(movie)
