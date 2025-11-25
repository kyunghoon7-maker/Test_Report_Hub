import pytest
from example_app import add, div


def test_add_ok():
    assert add(2, 3) == 5


def test_div_ok():
    assert div(10, 2) == 5


def test_div_zero():
    with pytest.raises(ZeroDivisionError):
        div(1, 0)  # 의도적으로 0으로 나눔 → 에러 나야 PASS


def test_fail_intentionally():
    # 일부러 FAIL 내는 테스트
    assert add(1, 1) == 3