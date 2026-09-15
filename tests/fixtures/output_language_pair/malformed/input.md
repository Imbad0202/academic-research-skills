# Fixture — malformed value

Two Schema-4 excerpts whose `output_language_pair` key is *present* but unusable: `null`,
and a non-string (list) value. Neither collapses into the legacy state.

```yaml
title: "Adaptation strategies of private universities under enrollment decline"
output_language_pair: null
abstract:
  english: "Declining enrollment poses existential challenges for private higher education institutions in Taiwan."
  chinese: "在少子化趨勢下，臺灣私立大學面臨招生困境。"
keywords:
  en: [higher education, enrollment decline, private university, institutional strategy, Taiwan]
  zh_tw: [高等教育, 招生困境, 私立大學, 校務策略, 臺灣]
```

```yaml
title: "Adaptation strategies of private universities under enrollment decline"
output_language_pair: [zh-tw-en]
abstract:
  english: "Declining enrollment poses existential challenges for private higher education institutions in Taiwan."
  chinese: "在少子化趨勢下，臺灣私立大學面臨招生困境。"
keywords:
  en: [higher education, enrollment decline, private university, institutional strategy, Taiwan]
  zh_tw: [高等教育, 招生困境, 私立大學, 校務策略, 臺灣]
```
