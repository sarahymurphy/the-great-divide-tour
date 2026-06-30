import pandas as pd
from pathlib import Path
from datetime import date

import folium

from shiny import App, ui, render

import matplotlib as mpl
import numpy as np
import base64

# rsconnect deploy shiny '/Users/sarahymurphy/Library/Mobile Documents/com~apple~CloudDocs/Projects/noahkahan-2026tour' --name aimlessghost --title noahkahan-2026tour

BASE_DIR = Path(__file__).parent
www_dir = BASE_DIR / "www"
static_assets={"/": www_dir}

def _load_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Load a CSV and raise a helpful error if it's missing.

    Keeps behaviour identical but gives a clearer message during failures.
    """
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path.resolve()}")
    return pd.read_csv(path, **kwargs)


def _svg_to_data_uri(path: Path) -> str:
    """Convert a local SVG file to a data URI for reliable in-app map icons."""
    if not path.exists():
        raise FileNotFoundError(f"Required icon file not found: {path.resolve()}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _image_to_data_uri(path: Path) -> str:
    """Convert a local PNG/JPG image to a data URI for reliable table cell backgrounds."""
    if not path.exists():
        raise FileNotFoundError(f"Required image file not found: {path.resolve()}")

    ext = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    if ext not in mime_types:
        raise ValueError(f"Unsupported image type for data URI: {path}")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_types[ext]};base64,{encoded}"


def _build_pin_data_uri(inner_svg_data_uri: str, pin_fill: str = "#4A9C59") -> str:
    """Build a pointer-style SVG map pin with a centered inner icon."""
    pin_svg = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='36' height='52' viewBox='0 0 36 52'>
    <defs>
        <filter id='shadow' x='-20%' y='-20%' width='140%' height='160%'>
            <feDropShadow dx='0' dy='2' stdDeviation='1.5' flood-color='#00000055'/>
        </filter>
    </defs>
    <path d='M18 1C8.6 1 1 8.6 1 18c0 12.6 15.6 31.1 16.3 31.9.4.5 1.1.5 1.5 0C19.4 49.1 35 30.6 35 18 35 8.6 27.4 1 18 1z'
                fill='{pin_fill}' stroke='#27492f' stroke-width='1.2' filter='url(#shadow)'/>
    <circle cx='18' cy='18' r='10.2' fill='#ffffff'/>
    <image href='{inner_svg_data_uri}' x='9.6' y='9.6' width='16.8' height='16.8'/>
</svg>
""".strip()
    encoded = base64.b64encode(pin_svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


df_path = BASE_DIR / "noahkahan-2026tour.csv"
loc_path = BASE_DIR / "locations.csv"
bug_icon_path = BASE_DIR / "img" / "bug-solid-full.svg"
bugs_icon_path = BASE_DIR / "img" / "bugs-solid-full.svg"
bug_slash_icon_path = BASE_DIR / "img" / "bug-slash-solid-full.svg"
cape_elizabeth_img_path = BASE_DIR / "img" / "cape-elizabeth.png"
stick_season_img_path = BASE_DIR / "img" / "stick-season.png"
great_divide_img_path = BASE_DIR / "img" / "the-great-divide.jpg"

bug_icon_url = _svg_to_data_uri(bug_icon_path)
bugs_icon_url = _svg_to_data_uri(bugs_icon_path)
bug_slash_icon_url = _svg_to_data_uri(bug_slash_icon_path)
bug_map_icon_url = _build_pin_data_uri(bug_icon_url, pin_fill="#3F4034")
bugs_map_icon_url = _build_pin_data_uri(bugs_icon_url, pin_fill="#261A0F")
cape_elizabeth_img_url = _image_to_data_uri(cape_elizabeth_img_path)
stick_season_img_url = _image_to_data_uri(stick_season_img_path)
great_divide_img_url = _image_to_data_uri(great_divide_img_path)

df = _load_csv(df_path)
show_cols = df.columns[2:].tolist()
df["mean"] = df[show_cols].mean(axis=1).round(2)
df["count"] = df[show_cols].count(axis=1).astype(int)
df = df.sort_values(by="mean", ignore_index=True)
cmap = mpl.colormaps["plasma"]

# Take colors at regular intervals spanning the colormap (kept for future use)
colors = cmap(np.linspace(0, 1, len(df)))


ldf = _load_csv(loc_path, sep=",", quotechar="'", skipinitialspace=True)
app_ui = ui.page_fluid(
    ui.panel_title(
        ui.tags.div(
            "Noah Kahan  -  The Great Divide Tour  -  Summer 2026",
            id="app-main-title",
        ),
        window_title="The Great Divide Tour",
    ),
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,100..900&family=League+Gothic&display=swap",

        ),
        ui.tags.link(rel="icon", type="image/svg+xml", href="favicon.svg")

        
    ),
    ui.tags.style(
        """
        :root {{
            --bs-body-font-family: 'Fraunces', serif;
            --bs-font-sans-serif: 'Fraunces', serif;
            --heading-font-family: 'League Gothic', sans-serif;
            --body-font-color: rgb(40, 39, 35);
        }}

        *, *::before, *::after {{
            font-family: 'Fraunces', serif !important;
        }}

        body,
        .card-body,
        .card-body div,
        .card-body span,
        .card-body p,
        .card-body li,
        .card-body label,
        #app-main-title {{
            color: var(--body-font-color) !important;
        }}

        #app-main-title {{
            font-family: var(--heading-font-family) !important;
            text-align: center;
            padding-top: 24px;
            padding-bottom: 8px;
            font-size: clamp(2.6rem, 4.2vw, 4.2rem);
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            width: 100%;
        }}

        #setlist_spreadsheet table thead th:nth-child(n+3),
        #setlist_spreadsheet table thead th:nth-child(n+3) > div {{
            text-align: center !important;
        }}

        #setlist_spreadsheet table thead th:nth-child(1) > div {{
            color: transparent !important;
        }}

        #setlist_spreadsheet table thead th:nth-child(1),
        #setlist_spreadsheet table thead th:nth-child(1) > div,
        #setlist_spreadsheet table tbody td:nth-child(1) {{
            width: 30px !important;
            min-width: 30px !important;
            max-width: 30px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            text-align: center !important;
        }}

        #setlist_spreadsheet table tbody tr {{
            height: 30px !important;
            max-height: 30px !important;
        }}

        #setlist_spreadsheet table tbody td {{
            overflow: hidden !important;
            white-space: nowrap !important;
            text-overflow: ellipsis !important;
            max-height: 30px !important;
        }}

        #setlist_spreadsheet .album-cell-stick-season,
        #setlist_spreadsheet .album-cell-great-divide,
        #setlist_spreadsheet .album-cell-cape-elizabeth {{
            color: transparent !important;
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}

        #setlist_spreadsheet .album-cell-stick-season {{
            background-image: url('{stick_season_album_img}');
        }}

        #setlist_spreadsheet .album-cell-great-divide {{
            background-image: url('{great_divide_album_img}');
        }}

        #setlist_spreadsheet .album-cell-cape-elizabeth {{
            background-image: url('{cape_elizabeth_album_img}');
        }}

        .card-header {{
            font-family: var(--heading-font-family) !important;
            font-weight: 700 !important;
            font-size: clamp(1.45rem, 2.1vw, 2.1rem);
            letter-spacing: 0.04em;
            text-transform: uppercase;
            background-color: rgb(246, 208, 113) !important;
            color: rgb(40, 39, 35) !important;
        }}

        .card-body {{
            background-color: rgb(245, 240, 225) !important;
        }}

        #footer_card .card-body {{
            font-size: 0.8rem;
            text-align: center;
        }}

        .footer-league-gothic,
        .footer-league-gothic * {{
            font-family: 'League Gothic', sans-serif !important;
            font-size: 1.25rem;
            letter-spacing: 0.75rem;
            text-transform: uppercase;
            font-weight: 780 !important;
            text-align: center;
            font-style: normal;
        }}

        h1, h2, h3, h4, h5, h6,
        table thead th,
        table thead th > div {{
            font-family: var(--heading-font-family) !important;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}

        h1 {{ font-size: clamp(2.4rem, 3.4vw, 3.4rem); }}
        h2 {{ font-size: clamp(2rem, 2.8vw, 2.8rem); }}
        h3 {{ font-size: clamp(1.65rem, 2.3vw, 2.3rem); }}
        h4 {{ font-size: clamp(1.4rem, 2vw, 2rem); }}
        h5 {{ font-size: clamp(1.2rem, 1.6vw, 1.6rem); }}
        h6 {{ font-size: clamp(1.05rem, 1.3vw, 1.3rem); }}

        table thead th,
        table thead th > div {{
            font-size: clamp(1.05rem, 1.35vw, 1.25rem);
            text-align: center !important;
        }}

        #location_spreadsheet table thead th:nth-child(1),
        #location_spreadsheet table thead th:nth-child(1) > div {{
            color: transparent !important;
        }}

        #location_spreadsheet table thead th,
        #location_spreadsheet table tbody td {{
            background-color: rgb(244, 244, 244) !important;
            color: rgb(40, 39, 35) !important;
        }}

        #location_spreadsheet .location-spotlight {{
            background-color: rgb(246, 236, 214) !important;
            color: rgb(40, 39, 35) !important;
        }}

        #location_spreadsheet table thead th:nth-child(1),
        #location_spreadsheet table tbody td:nth-child(1) {{
            width: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}

        #location_spreadsheet .status-past,
        #location_spreadsheet .status-future {{
            color: transparent !important;
            background-repeat: no-repeat;
            background-position: center;
            background-size: 12px 12px;
        }}

        #location_spreadsheet .status-past {{
            background-image: url('{past_icon}');
        }}

        #location_spreadsheet .status-future {{
            background-image: url('{future_icon}');
        }}
        """.format(
            past_icon=bug_slash_icon_url,
            future_icon=bug_icon_url,
            stick_season_album_img=stick_season_img_url,
            great_divide_album_img=great_divide_img_url,
            cape_elizabeth_album_img=cape_elizabeth_img_url,
        )
    ),
    ui.card(
        ui.card_header("Setlist Spreadsheet"),
        ui.card_body(
            ui.tags.div(
                ui.HTML(
                    "Numbers in the table represent where a song appeared in each show's setlist. "
                    "A blank cell means the song was not performed at that show. "
                    "The Mean column indicates the song's average setlist position across all shows. "
                    "Setlists from <a href='https://www.setlist.fm/search?artist=7bcdeef4&tour=6bdabaa2'>setlist.fm</a>."
                ),
                style="font-size: 0.75rem;",
            ),
            ui.tags.div(
                "Click on a column header to sort the table by that column.",
                style="font-size: 0.75rem;",
            ),
        ),
        ui.output_data_frame("setlist_spreadsheet"),
        ui.HTML(
            "<font size=0.75rem><center><i>Ray-Bans on your face, you've been drivin' all day. But you're here, and we're so grateful you are</i></center></font>"
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Tour Locations"),
            ui.output_data_frame("location_spreadsheet"),
            ui.HTML(
                    "<font size=0.75rem><center><i>Ooh, this towns for the record now</i></center></font>"
                ),
        ),
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Tour Map"),
                ui.HTML(
                    "<font size=0.75rem><center><i>This ain't Watertown, I'm on alien ground. I'm a collеge kid with my windows down</i></center></font>"
                ),
                ui.output_ui("map"),
            ),
            ui.card(
                ui.card_header("Spotify Playlist"),
                ui.HTML(
                    '<iframe data-testid="embed-iframe" style="border-radius:12px" '
                    'src="https://open.spotify.com/embed/playlist/0Hx3jZFFsQEYOk9nBPcms7?utm_source=generator&si=e4200a65f9ca4dbc" '
                    'width="100%" height="175" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; '
                    'encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
                ),
                ui.HTML(
                    "<font size=0.75rem><center><i>and I spent the whole night singin' \"Oh, my, my, what a time to be alive\"</i></center></font>"
                ),
            ),
            width=1,
            heights_equal="row",
        ),
        col_widths=(6, 6),
    ),
    ui.card(
        ui.HTML(
            "<font size=0.75rem><center><i>Last August angst and a pointless night. Oh, and the feeling of being alive for the first time in a long time</i></center></font>"
        ),
        ui.card_body("Last Updated: {}".format(date.today().strftime("%B %d, %Y"))),

        id="footer_card",
    ),
            ui.HTML(
            "<div class='footer-league-gothic'>Experience is everything</div>"
        ),
    theme=ui.Theme("lux"),
)


def server(input, output, session):

    @render.ui
    def map():
        map_center = [ldf.latitude.mean(), ldf.longitude.mean()]
        folium_map = folium.Map(
            location=map_center, zoom_start=4, tiles="OpenStreetMap"
        )

        duplicate_locations = set(
            tuple(values)
            for values in ldf[ldf.duplicated(subset=["city", "venue"], keep=False)][
                ["city", "venue"]
            ].to_numpy()
        )

        for l in ldf.index:
            popup_html = (
                "<b>Show Number</b>: "
                + str(ldf.iloc[l]["show"])
                + "<br><b>Location</b>: "
                + ldf.iloc[l]["city"]
                + "<br><b>Date</b>: "
                + ldf.iloc[l]["date"]
                + "<br><b>Venue</b>: "
                + ldf.iloc[l]["venue"]
            )
            location_key = (ldf.iloc[l]["city"], ldf.iloc[l]["venue"])
            icon_url = (
                bugs_map_icon_url
                if location_key in duplicate_locations
                else bug_map_icon_url
            )
            folium.Marker(
                location=[ldf.iloc[l].latitude, ldf.iloc[l].longitude],
                icon=folium.features.CustomIcon(
                    icon_image=icon_url,
                    icon_size=(30, 44),
                    icon_anchor=(15, 43),
                    popup_anchor=(0, -40),
                ),
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=ldf.iloc[l]["city"],
            ).add_to(folium_map)

        folium_map.fit_bounds(
            [
                [ldf.latitude.min(), ldf.longitude.min()],
                [ldf.latitude.max(), ldf.longitude.max()],
            ]
        )

        legend_html = f"""
        <div style='display:flex; flex-direction:column; gap:8px; font-size:0.85rem; margin-top:6px;'>
            <div style='display:flex; align-items:center; gap:10px;'>
                <img src='{bug_icon_url}' alt='Single bug icon' width='18' height='18' />
                <span>= one show at that location.</span>
            </div>
            <div style='display:flex; align-items:center; gap:10px;'>
                <img src='{bugs_icon_url}' alt='Multi bug icon' width='18' height='18' />
                <span>= multiple shows at that location.</span>
            </div>
        </div>
        """

        return ui.HTML(
            f"<div style='width:100%;'><div>{folium_map._repr_html_()}</div>{legend_html}</div>"
        )

    @render.data_frame
    def location_spreadsheet():
        ldf_cp = ldf.copy()
        ldf_cp.date = pd.to_datetime(ldf_cp.date, format="%m/%d/%y")
        today = date.today()
        ldf_cp["status_icon"] = ""
        first_boston_rows = np.where(ldf_cp["show"].eq(7))[0].tolist()
        past_rows = np.where(ldf_cp["date"].dt.date < today)[0].tolist()
        future_rows = np.where(ldf_cp["date"].dt.date >= today)[0].tolist()
        ldf_cp["date"] = ldf_cp["date"].dt.strftime("%m/%d")
        return render.DataGrid(
            ldf_cp[
                [
                    "status_icon",
                    "show",
                    "date",
                    "city",
                    "venue",
                ]
            ],
            height="fit-content",
            width="fit-content",
            styles=[
                {"style": {"font-size": 11, "font-weight": "300"}},
                {
                    "cols": [4],
                    "style": {"width": "1700px"},
                },
                {
                    "cols": [3],
                    "style": {"width": "1100px"},
                },
                {
                    "cols": [2],
                    "style": {
                        "width": "46px",
                        "min-width": "46px",
                        "max-width": "46px",
                        "text-align": "center",
                        "white-space": "nowrap",
                        "padding-left": "0px",
                        "padding-right": "0px",
                    },
                },
                {
                    "cols": [1],
                    "style": {
                        "width": "48px",
                        "min-width": "48px",
                        "max-width": "48px",
                        "text-align": "center",
                        "white-space": "nowrap",
                        "padding-left": "0px",
                        "padding-right": "0px",
                    },
                },
                {
                    "cols": [0],
                    "style": {"width": "36px", "text-align": "center"},
                },
                {
                    "rows": first_boston_rows,
                    "cols": [0, 1, 2, 3, 4],
                    "class": "location-spotlight",
                },
                {
                    "rows": past_rows,
                    "cols": [0],
                    "class": "status-past",
                },
                {
                    "rows": future_rows,
                    "cols": [0],
                    "class": "status-future",
                },
            ],
        )

    @render.data_frame
    def setlist_spreadsheet():
        album_colors = {
            "Stick Season": {"bg": "#C2C8A0", "bg_light": "#E9ECD8", "text": "#3F4034"},
            "The Great Divide": {
                "bg": "#D9C4B8",
                "bg_light": "#F1E5DE",
                "text": "#261A0F",
            },
            "Cape Elizabeth": {
                "bg": "#8FD2DA",
                "bg_light": "#D8F0F3",
                "text": "#012326",
            },
        }

        song_col = next((col for col in df.columns if str(col).lower() == "song"), None)
        album_col = next(
            (col for col in df.columns if str(col).lower() == "album"), None
        )
        mean_col = next((col for col in df.columns if str(col).lower() == "mean"), None)
        times_played_col = next(
            (col for col in df.columns if str(col).lower() == "count"), None
        )

        metric_cols = [col for col in df.columns if col not in {song_col, album_col}]
        if mean_col in metric_cols and times_played_col in metric_cols:
            metric_cols.remove(times_played_col)
            metric_cols.insert(metric_cols.index(mean_col) + 1, times_played_col)

        ordered_cols = [
            col for col in [album_col, song_col] if col is not None
        ] + metric_cols
        display_df = df.loc[:, ordered_cols].copy()

        key_cols = {"mean", "song", "album", "count"}
        key_col_idxs = [
            idx for idx, col in enumerate(ordered_cols) if str(col).lower() in key_cols
        ]
        light_col_idxs = [
            idx
            for idx, col in enumerate(ordered_cols)
            if str(col).lower() not in key_cols
        ]
        centered_cols = [
            idx
            for idx, col in enumerate(ordered_cols)
            if str(col).lower() not in {"song", "album"}
        ]
        song_col_idx = next(
            (idx for idx, col in enumerate(ordered_cols) if str(col).lower() == "song"),
            None,
        )
        album_col_idx = next(
            (
                idx
                for idx, col in enumerate(ordered_cols)
                if str(col).lower() == "album"
            ),
            None,
        )
        album_cell_classes = {
            "Stick Season": "album-cell-stick-season",
            "The Great Divide": "album-cell-great-divide",
            "Cape Elizabeth": "album-cell-cape-elizabeth",
        }

        album_styles = []
        for album, colors in album_colors.items():
            rows = np.where(df["Album"].eq(album))[0].tolist()
            if rows:
                album_styles.append(
                    {
                        "rows": rows,
                        "cols": key_col_idxs,
                        "style": {
                            "background-color": colors["bg"],
                            "color": colors["text"],
                            "font-weight": "300",
                        },
                    }
                )
                album_styles.append(
                    {
                        "rows": rows,
                        "cols": light_col_idxs,
                        "style": {
                            "background-color": colors["bg_light"],
                        },
                    }
                )
                if album_col_idx is not None and album in album_cell_classes:
                    album_styles.append(
                        {
                            "rows": rows,
                            "cols": [album_col_idx],
                            "class": album_cell_classes[album],
                        }
                    )

        return render.DataGrid(
            display_df,
            height="fit-content",
            width="fit-content",
            styles=[
                {
                    "style": {
                        "font-size": 11,
                        "font-weight": "300",
                        "color": "rgb(40, 39, 35)",
                    }
                },
                {
                    "cols": [0],
                    "style": {
                        "width": "44px",
                        "min-width": "44px",
                        "max-width": "44px",
                        "padding-left": "0px",
                        "padding-right": "0px",
                    },
                },
                {"cols": [1], "style": {"width": "420px"}},
                {"cols": [2], "style": {"width": "90px"}},
                {"cols": centered_cols, "style": {"text-align": "center"}},
                *album_styles,
                *(
                    [{"cols": [song_col_idx], "style": {"font-weight": "700"}}]
                    if song_col_idx is not None
                    else []
                ),
            ],
        )


app = App(app_ui, server, static_assets=static_assets)
