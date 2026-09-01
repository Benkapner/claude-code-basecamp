# Testing Patterns

## TDD Cycle

**RED** (write failing test) → **GREEN** (minimal code to pass) → **REFACTOR** (improve while green). Target 80%+ coverage.

## Testing Patterns

```python
# DataFrame testing
import pandas.testing as tm

def test_feature_engineering():
    input_df = pd.DataFrame({"price": [100, 200], "quantity": [2, 3]})
    result = add_total_column(input_df)
    expected = pd.DataFrame({"price": [100, 200], "quantity": [2, 3], "total": [200, 600]})
    tm.assert_frame_equal(result, expected)
```

```python
# Model reproducibility
def test_model_reproducibility(sample_df):
    model_1 = train_model(sample_df, random_state=42)
    model_2 = train_model(sample_df, random_state=42)
    X = sample_df[["feature_1"]]
    assert (model_1.predict(X) == model_2.predict(X)).all()
```

## Hard Limits

- **ALWAYS** set `random_state=42` for reproducibility
- **NEVER** hit real external APIs in unit tests — mock them
- **Test behavior, not internals** — assert outputs, not private attributes
- **Independent tests** — each test sets up its own data
- **Test edge cases** — None, empty DataFrame, NaN, inf
- Target **80%+ coverage**
