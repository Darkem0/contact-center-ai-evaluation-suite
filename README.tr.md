# Contact Center AI Evaluation Suite

Bu depo, **sentetik** bir destek diyaloğunu sekiz tipli ve deterministik görev paketiyle değerlendirir; kanıta bağlı JSON raporunu CLI veya yerel FastAPI uç noktasından üretir.

Amaç, belirsiz bir puan üretmek yerine gözlenen ifadeleri, desteklenmeyen iddiaları ve yetersiz kanıtı ayrı tutan bir ürün akışı göstermektir. Varsayılan yol, ayrı yönetişimden geçmiş yerel bir model eklenmeden önce yapılandırılmış çıktı sözleşmelerini denemek için kullanılabilir.

## Çalıştırma

```bash
python -m pip install -e ".[dev]"
python -m contact_center_eval.cli demo --output examples/demo-report.json
pytest -q
```

API gerektiğinde başlatılabilir:

```bash
python -m contact_center_eval.cli serve
# {"turns": [...]} gövdesini http://127.0.0.1:8000/v1/evaluate adresine POST edin.
```

## Beklenen çıktı

Gerçek demo [`fixtures/synthetic_dialogue.json`](fixtures/synthetic_dialogue.json) girdisini okur ve [`examples/demo-report.json`](examples/demo-report.json) oluşturur. Rapor sekiz görevi, dönüş bazlı kanıt alıntılarını, yapılandırılmış çıktı doğrulamasını ve diyaloğun bir sonuca yetmediği yerde açık `insufficient_evidence` sonucunu içerir.

```json
{
  "schema_version": "contact-center-eval.v2",
  "mode": "deterministic-local",
  "structured_output_valid": true
}
```

## Gerçek, mock ve isteğe bağlı kısımlar

- **Gerçek ve çalışır:** Pydantic şemaları, deterministik işleme, CLI, FastAPI sözleşmesi, fixture’lar, rapor üretimi ve testler.
- **Tasarım gereği mock:** ifade düzeyindeki görev kuralları ve çıktıları sentetik örnektir; müşteri veya çalışan değerlendirmesi değildir.
- **İsteğe bağlı:** `LocalLLMAdapter`, ayrı değerlendirilmiş yerel model için bir protokoldür. Varsayılan demo ve CI model indirmez, ücretli API kullanmaz.

## Dahil görev paketleri

1. Çağrı özeti ve çözüm
2. NPS kök neden analizi (anket puanı değil, genel sinyal özeti)
3. Temsilci aksiyonları ve eğitim ihtiyaçları
4. Takım lideri koçluk analizi
5. Yasak ifade tespiti
6. Olgusallık ve senaryo uyumu inceleme sinyalleri
7. Küfür ile hakaret sınıflandırması
8. Aktarım ve sonuç tespiti

Her görev `complete` veya `insufficient_evidence`, kısa gerekçe, kaynak dönüş alıntıları ve tipli sonuç üretir. Kaynak doğruluğu yoksa motor olgusallığı onaylamaz.

## Ürün yüzeyi

```text
fixtures/                kamuya güvenli sentetik diyalog girdileri
src/contact_center_eval/ şemalar, deterministik motor, CLI, FastAPI API
examples/                üretilmiş demo raporu
tests/                   normal, bozuk, şema ve API testleri
```

[`Dockerfile`](Dockerfile) yerel API’yi başlatır. Akış için [mimari diyagramına](docs/ARCHITECTURE.md), komutla oluşturulan çıktı için [örnek rapora](examples/demo-report.json) bakın.

## API örneği

```bash
curl -X POST http://127.0.0.1:8000/v1/evaluate \
  -H "content-type: application/json" \
  --data @examples/api-request.json
```

API istek sarmalayıcısı [`examples/api-request.json`](examples/api-request.json) dosyasındadır; CLI fixture’ın üst seviye dizisini doğrudan kabul eder.

## Güvenli veri sınırı

Yalnızca sentetik veriler veya izin, lisans, saklama ve kullanım amacı bakımından uygun veri setleri kullanın. Çağrı kaydı, müşteri tanımlayıcısı, müşteri transkripti, işveren promptu, müşteriye özel taksonomi, özel puanlama kuralı veya üretim iddiası eklemeyin.

Genişletmeden önce [Mimari](docs/ARCHITECTURE.md), [Provenance](docs/PROVENANCE.md), [Sınırlamalar](docs/LIMITATIONS.md) ve [Güvenlik](SECURITY.md) belgelerini okuyun.
