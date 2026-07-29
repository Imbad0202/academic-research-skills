ARM-MATERIAL-POINTER: arm-a.zh-TW.md

arm-c 使用與 arm-a 完全相同的素材（逐位元組相同）。本 arm 請實體化
`arms/arm-a.zh-TW.md`，不要串接本檔。

arm-c 與 arm-a 只有一件事不同：使用者在 Stage 3' deferral checkpoint 上給出的答案。
該答案不是稿件素材、不對任何 verifier call 可見，因此與其他 ground truth 一併保留為
held-out。「何時」可以供答，由本集合 README 的量測步驟 4 與本情境的 held-out 裁決鍵規範；
本檔刻意不複述該規則，因為多一份平行敘述就是多一個會漂移的地方。

共用素材是刻意的設計而非疏漏：這兩個 arm 的存在，就是要檢驗「回答之前的 emission 完全
相同」以及「唯一移動決策的是被記錄下來的那個答案」。若維護兩份各自獨立的副本，兩份會
漂移並毀掉這個不變量，所以只有一份檔案加上這個指標。
