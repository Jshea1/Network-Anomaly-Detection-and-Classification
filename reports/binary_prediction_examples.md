# Binary Prediction Examples

These examples show how the binary anomaly detection model labeled test-set traffic as either `Normal` or `Attack`.
The evidence section lists a few Decision Tree rules that were active for that prediction.

## Sample 4

- Actual label: `Normal`
- Predicted label: `Normal`
- Model confidence: `0.9271`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` > `0.0949` (actual `0.1284`)
  - `numeric__ct_dst_src_ltm` > `1.5000` (actual `40.0000`)
  - `numeric__dbytes` <= `1479.0000` (actual `268.0000`)

## Sample 5

- Actual label: `Normal`
- Predicted label: `Normal`
- Model confidence: `0.9271`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` > `0.0949` (actual `0.1729`)
  - `numeric__ct_dst_src_ltm` > `1.5000` (actual `40.0000`)
  - `numeric__dbytes` <= `1479.0000` (actual `268.0000`)

## Sample 6

- Actual label: `Normal`
- Predicted label: `Normal`
- Model confidence: `0.9271`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` > `0.0949` (actual `0.1433`)
  - `numeric__ct_dst_src_ltm` > `1.5000` (actual `40.0000`)
  - `numeric__dbytes` <= `1479.0000` (actual `354.0000`)

## Sample 47911

- Actual label: `Attack`
- Predicted label: `Attack`
- Model confidence: `1.0000`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` <= `0.0949` (actual `0.0000`)
  - `numeric__smean` > `53.5000` (actual `100.0000`)
  - `numeric__smean` <= `160.5000` (actual `100.0000`)

## Sample 47912

- Actual label: `Attack`
- Predicted label: `Attack`
- Model confidence: `1.0000`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` <= `0.0949` (actual `0.0000`)
  - `numeric__smean` > `53.5000` (actual `100.0000`)
  - `numeric__smean` <= `160.5000` (actual `100.0000`)

## Sample 47913

- Actual label: `Attack`
- Predicted label: `Attack`
- Model confidence: `1.0000`
- Evidence:
  - `numeric__sttl` > `61.0000` (actual `254.0000`)
  - `numeric__tcprtt` <= `0.0949` (actual `0.0000`)
  - `numeric__smean` > `53.5000` (actual `100.0000`)
  - `numeric__smean` <= `160.5000` (actual `100.0000`)
