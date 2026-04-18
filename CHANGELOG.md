# CHANGELOG

## [v1.3.0] - 2026-04-19

### Değişiklikler (tradingview_indicator.pine)
- EMA8 çizgisi trend durumuna göre renkleniyor: long=yeşil, short=kırmızı
- Arka plan long bölgesinde silik yeşil, short bölgesinde silik kırmızı
- Ayrı close trend çizgisi kaldırıldı

---

## [v1.2.0] - 2026-04-19

### Değişiklikler (tradingview_indicator.pine)
- EMA8 rengi turuncu → beyaz
- plotshape okları kaldırıldı, sadece skor etiketleri (`▲ 7` / `▼ 5`) gösteriliyor
- alertcondition mesajı const string yapıldı (Pine Script kısıtı)
- plotshape ve label.new çok satırlı çağrılar tek satıra alındı (syntax fix)
- longScore/shortScore hesabı ternary ifadeye çevrildi (syntax fix)
- volumeFilterPassed if/else bloğu ternary operatöre çevrildi (syntax fix)
- Pine Script dosyasına dahili versiyon geçmişi bloğu eklendi

---

## [v1.1.0] - 2026-04-19

### Eklenenler
- `tradingview_indicator.pine` — scan_strategy_crypto algoritmasının Pine Script v5 karşılığı
  - Long/Short sinyalleri ok ve skor etiketiyle gösteriliyor
  - EMA8 çizgisi, hacim filtresi ve tüm parametreler ayarlanabilir
  - Alert condition tanımlı

---

## [v1.0.0] - 2026-04-19

### Eklenenler
- `CLAUDE.md` oluşturuldu — Claude Code için proje rehberi
- `20260419_backup/` dizini oluşturuldu — mevcut dosyaların yedeği
