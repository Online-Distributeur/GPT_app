# GPT_app
Set up you .env file with KEYSTORE_KEY_OD, KEYSTORE_APP, OPENAI_KEY

install dependencies

run python file

voorbeeld config file Translations:
{
    "CLIENTS": {
        "VINYL": {
            "PRIMARY": {
                "ID": 273092,
                "LANGUAGE": [
                    "nl"
                ] 
            },
            "services": [
                {
                    "name": "my_gpt_content",
                    "type": "gpt_content",
                    "properties": {
                        "use_brand": false,
                        "use_shopsync": false,
                        "shopsync_client": false,
                        "translate_to": ["de","fr"],
                        "ToDo_category_id": 11977379,
                        "done_cat_id": 11962437,
                        "prompt": {
                            "nl":
                        "Je bent de copywriter voor de webshop Vloerkledenopvinyl en je wil de beste beschrijving van een product maken. Het doel van de beschrijving is goed scoren bij Google, maar het is ook belangrijk dat de klanten die dit lezen enthousiast worden van het product. Webshop Vloerkledenopvinyl maakt unieke vloerkleden, placemats, keukenlopers en inductiebeschermers gemaakt van vinyl. De producten worden allemaal in een eigen werkplaats in Nederland gemaakt van gerecycled polyester. Unieke eigenschappen van vinyl zijn een lange levensduur, slijtvast en makkelijk schoon te maken. Schrijf een unieke productbeschrijving van min. 600 en max. 800 tekens voor webshop Vloerkledenopvinyl in HTML-formaat en verwerk daarin het volgende: 1. Artikel is: {product_name} 2. Productcategorie: {main_cat} 3. Toon: informerend en overtuigend 4. Voeg na de unieke productbeschrijving van max. 800 karakters de volgende lijst in bulletpoints toe in HTML-formaat: Specificaties: - Slijtvast - Onverwoestbaar - Geschikt voor binnen en buiten - Hygiënisch - Makkelijk te reinigen - Vochtbestendig - Kleurvast - Brandveilig - Makkelijk oprolbaar"
                        }
                    }
                }
            ]
        }
    }
}

voorbeeld config file duplicate content checken en multiple languages:
{
    "CLIENTS": {
        "ONLYMX": {
            "PRIMARY": {
                "ID": 216986,
                "LANGUAGE": [
                    "en","nl","de","fr","es","it"
                ] 
            },
            "services": [
                {
                    "name": "my_gpt_content",
                    "type": "gpt_content",
                    "properties": {
                        "ToDo_category_id": "",
                        "done_cat_id": "",
                        "use_brand": false,
                        "translate_to": false,
                        "use_shopsync": "true",
                        "shopsync_folder": "/Users/timmatser/Dev/shopsync/",
                        "shopsync_client": "MUNITED_ONLYMX",
                        "prompt": {
                            "en": "Rewrite this product description and use HTML formatting: {product_content}",
                            "nl": "Herschrijf deze producttekst en gebruik hierbij HTML opmaak: {product_content}",
                            "de": "Mache diese Produktbeschreibung neu und verwende HTML-Formatierung: {product_content}",
                            "fr": "Réécrivez cette description de produit et utilisez la mise en forme HTML: {product_content}",
                            "es": "Reescribe esta descripción del producto y utiliza el formato HTML: {product_content}",
                            "it": "Riscrivi questa descrizione del prodotto e utilizza la formattazione HTML: {product_content}"
                        }
                        }
                    }
            ]
        }
    }
}