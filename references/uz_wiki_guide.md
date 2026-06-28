# Oʻzbek Vikipediyasi — yozuv qoʻllanmasi (agent uchun)

Bu fayldagi andoza nomlari uz.wikipedia.org API orqali **tasdiqlangan** (2026-06-28).
Yangi maqola yozayotganda faqat shu yerdagi andozalardan foydalaning; nomlarni oʻzingiz
"oʻylab topmang". Manbalarni (`<ref>`) `cite_source` vositasi orqali yarating.

## Maqola tuzilishi (skelet)

```wikitext
{{<infobox kerak boʻlsa>}}
'''<Mavzu nomi>''' — <bir jumlali taʼrif>.<ref>...</ref>

<Kirish (lead) — 1–3 abzas, eng muhim faktlar, manbalar bilan>

== <Boʻlim sarlavhasi> ==
<matn>...<ref>...</ref>

== Yana qarang ==
* [[<aloqador maqola>]]

== Manbalar ==
{{Manbalar}}

[[Turkum:<tegishli turkum>]]
[[Turkum:<yana turkum>]]
```

- Standart boʻlim nomlari: **Yana qarang** (See also), **Manbalar** (References),
  **Adabiyotlar** (Further reading), **Havolalar** yoki **Tashqi havolalar** (External links).
- Maqola juda qisqa (stub) boʻlsa, eng oxiriga (turkumlardan oldin) `{{Chala}}` qoʻying.

## Ichki havolalar (wikilink) — MUHIM

Matnda boshqa maqolalarga oid muhim atamalarni `[[...]]` bilan havola qiling. Bu Vikipediyaning
asosiy talabi — havolasiz maqola "yetim" boʻladi.

- Geografik joylar, shaxslar, tashkilotlar, tushunchalar, sanalar/voqealar — birinchi marta
  uchraganda havola qiling: `[[Toshkent]]`, `[[Sirdaryo]]`, `[[Chorvoq suv ombori]]`, `[[Metropoliten]]`.
- Quvur (`|`) bilan koʻrinadigan matnni oʻzgartirish mumkin: `[[Sirdaryo|Sirdaryoga]]`.
- **Faqat birinchi marta** havola qiling; har takrorda emas. Ortiqcha havola (over-linking) ham yomon.
- Havola qilingan maqola/atama uz.wiki'da boʻlishi ehtimoli boʻlsa havola qiling; ishonchsiz boʻlsangiz
  `check_exists` bilan tekshiring (lekin qizil havola — mavjud boʻlmagan maqolaga — ham normal, agar atama munosib boʻlsa).

## Manbalar (`<ref>`) mexanikasi

- Manba matn ichida qoʻyiladi va `{{Manbalar}}` (== Manbalar == boʻlimida) uni roʻyxatga chiqaradi.
- **Tinish belgisi (nuqta, vergul) `<ref>` dan KEYIN qoʻyiladi** — bu uz.wiki uslubi:
  - ✅ toʻgʻri: `... muhim fakt<ref>{{Veb manbasi|...}}</ref>.`
  - ❌ notoʻgʻri: `... muhim fakt.<ref>{{Veb manbasi|...}}</ref>`
- **Nomli (takroriy) manba** — bir manbani bir necha marta ishlatish:
  - **birinchi marta toʻliq taʼrif bilan**, matn ICHIDA: `<ref name="bbc2024">{{Veb manbasi|...}}</ref>`
  - keyingi marta qisqa shaklda: `<ref name="bbc2024" />`
  - ⚠️ Toʻliq `<ref name="...">{{...}}</ref>` taʼrifi kamida bir marta matn ichida boʻlishi SHART.
    Uni maqoladan tashqarida (alohida roʻyxatda) qoldirmang — aks holda manba "buzilgan" boʻladi.
    Agar har joyda `<ref name="x" />` ishlatib, hech qayerda toʻliq taʼrif boʻlmasa — xato.
- `== Manbalar ==` ostida doim `{{Manbalar}}` boʻlishi shart (aks holda manbalar koʻrinmaydi).
- Eslatma/izohlar uchun alohida `{{Eslatmalar}}` andozasi bor (ixtiyoriy).

## Iqtibos andozalari (tasdiqlangan nomlar)

Bularning hammasi inglizcha CS1 parametrlarini qabul qiladi (`url`, `title`, `author`/`last`+`first`,
`date`, `publisher`, `work`, `access-date`, `language`, `isbn`, `pages`, `doi`, ...).

| Manba turi | Andoza | Asosiy parametrlar |
|---|---|---|
| Veb-sahifa | `{{Veb manbasi}}` | url, title, author, website/work, publisher, date, access-date, language |
| Kitob | `{{Kitob manbasi}}` | title, last, first, publisher, year/date, isbn, pages, location |
| Yangilik | `{{Yangiliklar manbasi}}` | url, title, last, first, work, publisher, date, access-date |
| Jurnal/ilmiy | `{{Cite journal}}` | title, last, first, journal, year, volume, pages, doi |

`{{Veb manbasi}}` oʻzbekcha parametrlarni ham qabul qiladi (`sarlavha`, `muallif`, `sana`,
`qaralgan sana`, `til`), lekin **barcha andozalarda ishlashi uchun inglizcha nomlardan foydalaning**.

### Misol
```wikitext
<ref>{{Veb manbasi |url=https://example.org/maqola |title=Maqola sarlavhasi |author=Ism Familiya |website=Example |date=2024-05-01 |access-date=2026-06-28 |language=en}}</ref>
```

## Andoza/turkum topish va tekshirish (jonli)

Qoʻllanmada yoʻq andoza (masalan infobox) kerak boʻlsa yoki nomga ishonchingiz boʻlmasa:
- **`find_template("<kalit soʻz>")`** — uz.wiki'dan mavjud andozani topadi (masalan "daryo"
  → `{{Daryo bilgiqutisi}}`). Nomni oʻzingiz oʻylab topmang.
- **`template_info("<andoza>")`** — andoza mavjudligini tasdiqlaydi va parametrlarini beradi.
- **`check_exists([...])`** — turkum/maqola/andoza mavjudligini tekshiradi.

## Turkumlar (kategoriyalar)

- Maqola oxirida: `[[Turkum:<nom>]]`. Kamida bittasi boʻlsin.
- Turkum nomini **doim `check_exists` bilan tekshiring** — mavjud boʻlmaganini qoʻshmang
  (uz.wiki'da koʻp turkum "...dagi daryolar" kabi oʻziga xos nomlanadi).

## Muhim eslatmalar

- Til: oʻzbekcha (lotin). Atoqli otlarni oʻzbek imlosiga moslang.
- Faqat tekshirilgan, ishonchli manbalarni keltiring; har bir muhim faktga manba bering.
- Reklama/targʻibot ohangidan saqlaning — neytral, ensiklopedik uslub.
