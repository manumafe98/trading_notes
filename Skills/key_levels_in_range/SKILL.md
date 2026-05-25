---
name: key-levels-in-range
description: >
  Identifies which price levels from ICT Killzones and Key Levels indicators
  fall within a given price range between a starting price and a take-profit
  price. Use this skill when the user provides a from price and a take profit
  price and wants to know which key levels (PDH, PDL, PWH, PWL, PMH, PML, ASH,
  ASL, LDH, LDL, etc.) sit between them. Also use when the user asks about
  levels in a price range, obstacles between two prices, or confluences in a
  price zone.
---

# Key Levels In Range

Fetches price levels from ICT Killzones and Key Levels indicators on the active TradingView chart, filters them to only those within a given from-price → take-profit range, and returns the matching level names.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `current_day_of_the_week` | string | yes | Full day name: `"Sunday"`, `"Monday"`, `"Tuesday"`, `"Wednesday"`, `"Thursday"`, `"Friday"`, `"Saturday"` |
| `from_price` | number | yes | Starting price of the range (e.g., Candle Entry, ORB High, ORB Low) |
| `take_profit_price` | number | yes | Take profit price of the trade |

## Instructions

### Step 1 — Fetch indicator tables

Call `mcp_tradingview_data_get_pine_tables` twice (in parallel):

```
Tool: mcp_tradingview_data_get_pine_tables
Parameters: { study_filter: "ICT Killzones" }

Tool: mcp_tradingview_data_get_pine_tables
Parameters: { study_filter: "Key Levels" }
```

### Step 2 — Parse rows into label → price map

For each table response, iterate over the `rows` array. Skip the first row (header). Split each row by ` | ` to extract:
- Column 0 → `label` (e.g., `"WED ASH"`, `"PDH"`)
- Column 1 → `price` (parse as float, e.g., `29968.75`)
- Column 2 → `mitigated` (e.g., `"YES"` or `"NO"`)

**Exclude any row where mitigated = "YES"**. Only keep unmitigated levels.

Build a combined map of `{ label: price }` from both tables.

### Step 3 — Determine the price range

```
range_low  = min(from_price, take_profit_price)
range_high = max(from_price, take_profit_price)
```

### Step 4 — Filter levels within range

From the combined label → price map, keep only entries where:

```
price >= range_low AND price <= range_high
```

The `>=` and `<=` (inclusive) ensure that levels with an exact match to range bounds are included.

### Step 5 — Clean up killzone day prefixes

Map the `current_day_of_the_week` parameter to its 3-letter uppercase prefix:

| Day | Prefix |
|-----|--------|
| Sunday | SUN |
| Monday | MON |
| Tuesday | TUE |
| Wednesday | WED |
| Thursday | THU |
| Friday | FRI |
| Saturday | SAT |

For each filtered label that starts with a 3-letter day prefix followed by a space:
- If the prefix **matches** the current day → **remove it** (e.g., `"WED ASH"` → `"ASH"`)
- If the prefix **does not match** → **keep it as-is** (e.g., `"TUE ASH"` stays `"TUE ASH"`)

Key Levels labels (`PDH`, `PDL`, `PWH`, `PWL`, `PMH`, `PML`) have no day prefix and are always kept unchanged.

### Step 6 — Return result

Return only the cleaned labels as a JSON array:

```json
["ASL", "TUE ASH", "LDH", "PWH"]
```

## Example

**Inputs:**
- `current_day_of_the_week` = `"Wednesday"`
- `from_price` = `29800`
- `take_profit_price` = `29400`

**Step 3:** `min(29800, 29400) = 29400`, `max(29800, 29400) = 29800` → Range = `[29400, 29800]`.

**Step 4:** Suppose the MCP tools return:

| Label | Price | Mitigated | In Range? | Included? |
|-------|-------|-----------|-----------|-----------|
| WED ASH | 29968.75 | NO | ❌ above | No |
| WED ASL | 29789.50 | YES | ✅ | **No — mitigated** |
| TUE ASH | 29560.00 | YES | ✅ | **No — mitigated** |
| TUE ASL | 29328.75 | NO | ❌ below | No |
| THU LDH | 29914.50 | NO | ❌ above | No |
| THU LDL | 29755.00 | YES | ✅ | **No — mitigated** |
| WED LDH | 29714.75 | YES | ✅ | **No — mitigated** |
| WED LDL | 29560.00 | YES | ✅ | **No — mitigated** |
| TUE LDH | 29551.50 | YES | ✅ | **No — mitigated** |
| TUE LDL | 29399.00 | YES | ❌ below | No |
| PDH | 29830 | YES | ❌ above | No |
| PDL | 29328.75 | NO | ❌ below | No |
| PWH | 29632.75 | YES | ✅ | **No — mitigated** |
| PWL | 27867.75 | NO | ❌ below | No |

In this example, all in-range levels happen to be mitigated, so the result would be:
```json
[]
```

If `WED ASL` and `PWH` were NOT mitigated, the result would be:
```json
["ASL", "PWH"]
```
(`WED ASL` → `ASL` because the WED prefix matches Wednesday)

## Guidelines

- Always call both MCP tools — the chart must have both ICT Killzones and Key Levels indicators active
- If either tool returns no data or an error, report the issue to the user
- The day prefix cleanup only applies to killzone labels (those with a 3-letter day prefix like MON, TUE, etc.)
- Returns an empty array `[]` if no unmitigated levels fall within the range
