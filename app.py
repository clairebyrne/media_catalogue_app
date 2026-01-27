import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="My Movie Library",
    layout="wide"
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    text_cols = ["name", "overview", "cast"]
    for col in text_cols:
        df[col] = df[col].astype(str)

    df["release_year"] = pd.to_datetime(
        df["release_date"], errors="coerce"
    ).dt.year

    return df

@st.dialog("Movie details")
def show_movie_details(movie):
    st.image(movie["poster"], width=250)

    st.markdown(f"**Release year:** {int(movie['release_year'])}")
    st.markdown(f"**Genre:** {movie['genre']}")
    st.markdown(f"**Rating:** ⭐ {movie['vote_average']}")

    st.markdown("### Overview")
    st.write(movie["overview"])

    if movie["cast"]:
        st.markdown(f"**Cast:** {movie['cast']}")

    if movie["trailer"]!="No trailer available":
        st.video(movie["trailer"])


# ---------- Load data ----------
df = load_data("media_df.csv")

st.title("🎬 Movie Library")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

search_text = st.sidebar.text_input(
    "Search title / overview / cast"
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

# ---------- Filtering logic ----------
filtered = df.copy()

if search_text:
    s = search_text.lower()
    filtered = filtered[
        filtered["name"].str.lower().str.contains(s, na=False)
        | filtered["overview"].str.lower().str.contains(s, na=False)
        | filtered["cast"].str.lower().str.contains(s, na=False)
    ]

filtered = filtered[
    (filtered["vote_average"] >= min_rating)
    & (filtered["release_year"] >= year_range[0])
    & (filtered["release_year"] <= year_range[1])
]

st.caption(f"{len(filtered)} movies")

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
            if pd.notna(movie["poster"]):
                st.image(movie["poster"], use_container_width=True)

            st.markdown(
                f"**{movie['name']}** ({int(movie['release_year']) if pd.notna(movie['release_year']) else '—'})"
            )
            st.caption(
                f"⭐ {movie['vote_average']}  ·  {movie['genre']}"
            )

            if st.button("Details", key=f"details_{movie.name}"):
                show_movie_details(movie)



            # with st.expander("Details"):
            #     st.write(movie["overview"])

            #     if pd.notna(movie["cast"]):
            #         st.markdown(f"**Cast:** {movie['cast']}")

            #     if pd.notna(movie["trailer"]):
            #         st.markdown(
            #             f"[▶ Watch trailer]({movie['trailer']})"
            #         )
