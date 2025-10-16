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
    if request.method == "POST":
        jenis = request.form.get("jenis")
        harga = request.form.get("harga")
        print("Received a POST request")
        print("Form Data:", request.form)
    else:
        jenis = None
        harga = None

    if harga == "bawah":
        filtered = df[df["harga"] <= 20000]
    elif harga == "atas":
        filtered = df[df["harga"] > 20000]
    else:
        filtered = df.copy()

    if jenis:
        filtered = filtered[filtered["jenis"].str.contains(jenis, case=False, na=False)]

    # ✅ Posisi awal peta agak ke selatan biar tampilan pas
    start_coords = [-8.2, 112.5]  # sebelumnya -7.5, 112.5
    start_zoom = 7
    m = folium.Map(
        location=start_coords,
        zoom_start=start_zoom,
        tiles=None,
        control_scale=True,
        scrollWheelZoom=True
    )

    # Basemap
    folium.TileLayer("CartoDB positron", name="CartoDB Positron", show=False).add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="CartoDB Dark Matter", show=False).add_to(m)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=True).add_to(m)

    # Tambahkan marker
    for _, row in filtered.iterrows():
        html_popup = f"""
        <div style="width:250px">
            <h4>{row['nama_wisata']}</h4>
            <img src='/static/images/{row['gambar']}' width='220px'><br>
            <p><b>Lokasi:</b> {row['lokasi']}<br>
            <b>Harga Tiket:</b> Rp{row['harga']:,}<br>
            <b>Fasilitas:</b> {row['fasilitas']}<br>
            <b>Jalur Trekking:</b> {row['jalur']}<br>
            <a href='/static/info/{row["info_link"]}' target='_blank'>More info</a></p>
        </div>
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(html_popup, max_width=300, sticky=True),
            tooltip=row["nama_wisata"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    map_html = m._repr_html_()

    return render_template("layout.html", map_html=map_html, kategori_wisata=jenis, harga=harga)

if __name__ == "__main__":
    app.run(debug=True)
