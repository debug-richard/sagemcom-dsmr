# Beispiel Sagemcom T210-D-r auslesen via Kundenschnittstelle

> **WARNUNG**  
> Dieses Beispiel ist nur für den Sagemcom T210-D **-r** **(STRICH "R")** gültig!  
> Der Sagemcom T210-D (ohne -r) nutzt ein anderes Protokoll.

Der **Sagemcom T210-D-r** wird unter anderem von der "Energienetze Steiermark" verbaut,
das Beispiel sollte aber für alle Netzbetreiber gültig sein.

## Anschluss
Der physikalische Anschluss erfolgt über den P1 Standard, einer RJ12 Buchse die sich unter dem grünen Deckel befindet.
Standardmäßig ist dieser deaktiviert und muss über das Portal der "Energienetze Steiermark" https://www.e-netze.at aktiviert werden.  
Dies entspricht **NICHT** dem Portal der "Energie Steiermark" oder eines anderen Stromversorgers!

Nach der Aktivierung kann man, sehr versteckt, die Sicherheitsschlüssel "GLOBAL UNICAST ENCRYPTION KEY (GUEK)" und "GLOBAL AUTHENTICATION KEY (GAK)"
im Portal finden.  

Für den Anschluss an einen PC/Raspberry Pi/etc.. wird ein **spezielles** USB zu RJ12 Seriell Kabel benötigt.  
Man kann sich das Kabel theoretisch auch selber bauen.  
Getestet ist dieses Kabel:  
https://www.amazon.de/dp/B08FB741QM/ref=pe_27091401_487024491_TE_item


## Auslesen der Daten
Das Projekt ist in Python geschrieben und stellt nur ein Beispiel da.

Es gibt drei Skripte/Module die wichtig sind:

**decode.py**: Bibliothek zum Entschlüsseln und Serialisieren der Daten  
**serialtest.py**: Liest Daten von der seriellen Schnittstelle und zeigt diese entschlüsselt an  
**justdecode.py**: Entschlüsselt einen HEX-String und zeigt ihn an

### Installation/Ausführen
Zuerst müssen die Schlüssel und die zu entschlüsselnden Daten in die Skripte eingetragen werden.  

```python
python3 -m venv venv/
source ./venv/bin/activate
pip3 install -r pre-requirements.txt
CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 install -r requirements.txt
python3 justdecode.py
```
```json
{                                                                                                                                                                                                                                            
  "1-3:0.2.8": {                                                                                                                                                                                                                             
    "DSMR Version": "50"                                                                                                                                                                                                                     
  },                                                                                                                                                                                                                                         
  "0-0:1.0.0": {                                                                                                                                                                                                                             
    "Zeitstempel": {                                                                                                                                                                                                                         
      "year": "22",                                                                                                                                                                                                                          
      "month": "10",                                                                                                                                                                                                                         
      "day": "06",                                                                                                                                                                                                                           
      "hour": "06",                                                                                                                                                                                                                          
      "minute": "15",
      "second": "50"
    }
  },
  "1-0:1.8.0": {
    "Wirkenergie Lieferung (Lieferung an Kunden) (+A)": {
      "value": 6545766,
      "unit": "Wh"
    }
  },
  "1-0:1.8.1": {
    "Wirkenergie Lieferung (Lieferung an Kunden) (+A) Tarif 1": {
      "value": 5017120,
      "unit": "Wh"
    }
  },
  "1-0:1.8.2": {
    "Wirkenergie Lieferung (Lieferung an Kunden) (+A) Tarif 2": {
      "value": 1528646,
      "unit": "Wh"
    }
  },
  "1-0:1.7.0": {
    "Momentane Wirkleistung Bezug (+A)": {
      "value": 286,
      "unit": "W"
    }
  },
  "1-0:3.8.0": {
    "Blindenergie Lieferung (+R)": {
      "value": 747,
      "unit": "varh"
    }
  },
  "1-0:3.8.1": {
    "Blindenergie Lieferung (+R) Tarif 1": {
      "value": 0,
      "unit": "varh"
    }
  },
  "1-0:3.8.2": {
    "Blindenergie Lieferung (+R) Tarif 2": {
      "value": 747,
      "unit": "varh"
    }
  },
  "1-0:3.7.0": {
    "Momentane Blindleistung Bezug (+R)": {
      "value": 0,
      "unit": "var"
    }
  },
  "1-0:2.8.0": {
    "Wirkenergie Bezug (Lieferung an EV) (-A)": {
      "value": 58,
      "unit": "Wh"
    }
  },
  "1-0:2.8.1": {
    "Wirkenergie Bezug (Lieferung an EV) (-A) Tarif 1": {
      "value": 0,
      "unit": "Wh"
    }
  },
  "1-0:2.8.2": {
    "Wirkenergie Bezug (Lieferung an EV) (-A) Tarif 2": {
      "value": 58,
      "unit": "Wh"
    }
  },
  "1-0:2.7.0": {
    "Momentane Wirkleistung Lieferung (-A)": {
      "value": 0,
      "unit": "W"
    }
  },
  "1-0:4.8.0": {
    "Blindenergie Bezug (-R)": {
      "value": 3897726,
      "unit": "varh"
    }
  },
  "1-0:4.8.1": {
    "Blindenergie Bezug (-R) Tarif 1": {
      "value": 2692848,
      "unit": "varh"
    }
  },
  "1-0:4.8.2": {
    "Blindenergie Bezug (-R) Tarif 2": {
      "value": 1204878,
      "unit": "varh"
    }
  },
  "1-0:4.7.0": {
    "Momentane Blindleistung Lieferung (-R)": {
      "value": 166,
      "unit": "var"
    }
  }
}
```
```text
Wird aktuell geliefert: {'Momentane Wirkleistung Bezug (+A)': {'value': 286, 'unit': 'W'}}
Wird aktuell eingespeist: {'Momentane Wirkleistung Lieferung (-A)': {'value': 0, 'unit': 'W'}}
Wurde geliefert (Zählerstand): {'Wirkenergie Lieferung (Lieferung an Kunden) (+A)': {'value': 6545766, 'unit': 'Wh'}}
Wurde eingespeist (Zählerstand): {'Wirkenergie Bezug (Lieferung an EV) (-A)': {'value': 58, 'unit': 'Wh'}}
```

## Beschreibung des Kommunikationsprotokolls
Die Daten können seriell ausgelesen werden (Baud 115200, 8N1).
Eine Information wird alle 5 Sekunden geschickt und ist 511 Byte lang.

Ich habe das Protokoll größtenteils Reverse-Engineered da es mehrere Standards kombiniert, die nicht öffentlich einsehbar sind...  
Der Netzbetreiber interessiert sich auch nicht dafür.

Physikalisch basiert der Anschluss auf dem "Dutch Smart Meter Requirements v5.0.2 (DSMR)" Standard.  
Der Datenframe ist DLMS Standard und mit COSEM-Security 0 verschlüsselt.
Die entschlüsselten Daten entsprechen grundsätzlich dem DSMR Standard/COSEM Objekte und sind in ASCII codiert.

**Beispiel:**
db0853414735000040598201f230000000490574a075a1e4a508c6bdfeb6ffbc3fe1229baefe04ef7d29e74d47c0f3e73ec79536b86e2b74867eeb730a2abd703e7707c8addd7b5a9c7a25028adba4aa6b1611e83709db66da3590b60bf5ed09f2d94cc5aa836a7c63947d193e0b700b0d35a2026c3afc662d112a00a4b4e5b88b95acfd09d6e19f3aa7143e4a5a5b844b9084fde27a503dab045bc5f11ded3692da47ba4f6136c536c7093c51dac465ad6930130fa39b981c3b7240beba23a50b0357efd6e8949b74c9fba80416933111c47c21634380cfb6011a8797c0bb0fdec58e5c9d786befb925addd0d17ae5aa09c441177e8417b67673b6b960e8b7cd5913a429231b90c90178bd0225940dd925648dd3c85547ca5ef12c36d098bf09ee7ddaba72a7a9c56d8d714d33e8228769eac887772cbb77753908efe62ff0262bcada194d2261c38fc19cdce0ed6a17fac85f9d11e3bf67e2a5503b1891a47029aac8005e24b0293c6a0a591fc6feb1f10dd5534154ba07903ad5bd8c1dd4517d80c5433de8d8213c0fc7d75fd02a885b5ecc9d23f202a09a68f3d6729f4442191d00e07390fa134945eb597ff634537dec003e05d4601d5049a97dc11b2f3dbcdc2052159cd5c0134210abe3a21788abe5122726ed12ae0880dbb46ce90142036d327b22a58c35ae7263d57e161812333ef07e2ca940cc6ed809a657a10

Der Header sieht wie folgt aus:
db0853414735000040598201f23000000049

**db**: [DLMS Tag, "general-glo-cipher"](https://github.com/pwitab/dlms-cosem/blob/06f6af444d6f80a2b41e1ea402d5b7f2372edd6e/dlms_cosem/protocol/xdlms/general_global_cipher.py#L14)

**08**: Länge des "System Title"

**53 41 47 35 00 00 40 59**: "System Title", wird für die Entschlüsselung gebraucht, die ersten 3 Byte sind der Herstellercode in ASCII, der Rest ist unbekannt

**82**: [Länge der folgenden Längenbytes](https://github.com/pwitab/dlms-cosem/blob/739f81a58e5f07663a512d4a128851333a0ed5e6/dlms_cosem/a_xdr.py#L33)

**01 f2**: Länge des verschlüsselten Inhalts

**30**: [Security Level 0x30 = Auth+Enc](https://github.com/pwitab/dlms-cosem/blob/06f6af444d6f80a2b41e1ea402d5b7f2372edd6e/dlms_cosem/security.py#L31)

**00 00 00 49**: "Frame counter", wird für die Entschlüsselung gebraucht, ändert sich ständig

**05 74 a0 75...**: Verschlüsselter Payload

**...07 e2 ca 94 0c c6 ed 80 9a 65 7a 10**: Authentication Tag

Die Daten sind mit AES-GCM verschlüsselt. Siehe Code für Details.

# Dokumente
https://www.e-netze.at/downloads-data/pdf.aspx?pdf=EN_Update%20Kundenschnittstelle%20Smart%20Meter_ID3282_WEB_RGB.pdf

https://www.netbeheernederland.nl/_upload/Files/Slimme_meter_15_a727fce1f1.pdf
