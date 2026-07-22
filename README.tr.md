# Contact Center AI Evaluation Suite

Sentetik diyaloglar ve deterministik kurallarla konuşmalı destek iş akışlarını değerlendiren, yerel-öncelikli temiz-oda referans uygulamasıdır. İşveren kodu, müşteri taksonomisi, özel istem, çağrı kaydı, üretim şeması veya üretim performans iddiası içermez.

## Gösterdiği alanlar

- NPS benzeri kök neden ve memnuniyetsizlik sinyalleri;
- çağrı özeti, çözüm ve aktarma tespiti;
- temsilci aksiyon, koçluk ve eğitim sinyalleri;
- genel hukuk metni, yasak ifade, olgusal tutarlılık, sigorta kalitesi ve küfür riski kontrolleri;
- yapılandırılmış JSON için şema doğrulama ve görünür hata yönetimi.

```bash
python -m pip install -e ".[dev]"
python -m contact_center_eval.demo
pytest
```

Demo yalnızca sentetik örneği okur. Gerçek çağrı, müşteri tanımlayıcısı, müşteri adı, özel istem veya iç politika eklemeyin. Ayrıntılar için [mimari](docs/ARCHITECTURE.md) ve [sınırlamalar](docs/LIMITATIONS.md) belgelerine bakın.
