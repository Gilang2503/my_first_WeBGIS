from flask import Flask, render_template, request
import folium
import pandas as pd

app = Flask(__name__)
df = pd.read_csv("static/data_wisata.csv")

@app.route("/", methods=["GET", "POST"])
def home():
    return map_view()

@app.route("/map", methods=["GET", "POST"])
def map_view():
    # Ambil filter dari POST atau dari URL (GET)
    if request.method == "POST":
        jenis = request.form.get("jenis")
        harga = request.form.get("harga")
    else:
        jenis = request.args.get("jenis")
        harga = request.args.get("harga")

    if harga == "bawah":
        filtered = df[df["harga"] <= 20000]
    elif harga == "atas":
        filtered = df[df["harga"] > 20000]
    else:
        filtered = df.copy()

    if jenis:
        filtered = filtered[filtered["jenis"].str.contains(jenis, case=False, na=False)]

    start_coords = [-8.2, 112.5]
    start_zoom = 7
    m = folium.Map(
        location=start_coords,
        zoom_start=start_zoom,
        tiles=None,
        control_scale=True,
        scrollWheelZoom=True
    )

    folium.TileLayer("CartoDB positron", name="CartoDB Positron", show=False).add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="CartoDB Dark Matter", show=False).add_to(m)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=True).add_to(m)

    # Simpan parameter ke URL agar bisa dibawa ke halaman info
    query_params = []
    if jenis:
        query_params.append(f"jenis={jenis}")
    if harga:
        query_params.append(f"harga={harga}")
    query_string = "&".join(query_params)
    filter_url = f"/?{query_string}" if query_string else "/"

    for _, row in filtered.iterrows():
        html_popup = f"""
        <div style="width:250px">
            <h4>{row['nama_wisata']}</h4>
            <img src='/static/images/{row['gambar']}' width='220px'><br>
            <p><b>Lokasi:</b> {row['lokasi']}<br>
            <b>Harga Tiket:</b> Rp{row['harga']:,}<br>
            <b>Fasilitas:</b> {row['fasilitas']}<br>
            <b>Jalur Trekking:</b> {row['jalur']}<br>
            <a href='/static/info/{row["info_link"]}?{query_string}' target="_self">More info</a></p>
        </div>
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=html_popup,
            tooltip=row["nama_wisata"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    map_html = m.get_root().render()
    return render_template("layout.html", map_html=map_html, kategori_wisata=jenis, harga=harga)

if __name__ == "__main__":
    app.run(debug=True)
