---
type: regex
target: last_message
match: contains
weight: 0.5
---
\bos\b[\s\S]{0,120}(unused|not used|never used|沒有?被?用|未被?使用|用不到|多餘)|(unused|not used|never used|沒有?被?用|未被?使用|用不到|多餘)[\s\S]{0,120}\bos\b
