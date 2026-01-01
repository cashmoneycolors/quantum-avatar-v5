class SignageGenerator:
    def generate_html(self):
        html = """
        <html>
        <head><title>Amriswil Markt</title></head>
        <body>
        <div id="content">Angebot der Stunde: Sucuk CHF 5.99</div>
        <script>
        var contents = [
            "Angebot der Stunde: Sucuk CHF 5.99",
            "Wetter in Amriswil: Sonnig, 20°C",
            "Heutiges Rezept: Menemen"
        ];
        var i = 0;
        setInterval(function() {
            document.getElementById('content').innerHTML = contents[i];
            i = (i + 1) % contents.length;
        }, 5000);
        </script>
        </body>
        </html>
        """
        with open("signage.html", "w") as f:
            f.write(html)
