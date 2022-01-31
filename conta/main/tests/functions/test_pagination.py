import pytest
from main.functions import lista_paginas, get_pagination

class TestListaPaginas:
    @pytest.mark.parametrize('paginas, actual, num, result', [
        (2, 1, 3, [1, 2]),
        (2, 2, 5, [1, 2]),
        (2, 1, 1, [1, 2]),
        (5, 3, 1, [1, 2, 3, 4, 5]),
    ])
    def test_lista_paginas_lt_10(self, paginas, actual, num, result):
        pagination = lista_paginas(paginas, actual, num)
        assert pagination == result


    @pytest.mark.parametrize('paginas, actual, num, result', [
        (12, 6, 1, [1, 0, 5, 6, 7, 0, 12]),
        (17, 12, 2, [1, 0, 10, 11, 12, 13, 14, 0, 17]),
        (15, 8, 3, [1, 0, 5, 6, 7, 8, 9, 10, 11, 0, 15]),
        (50, 34, 4, [1, 0, 30, 31, 32, 33, 34, 35, 36, 37, 38, 0, 50]),
        (18, 10, 5, [1, 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 18]),
        (20, 9, 6, [1, 0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 20]),
    ])
    def test_lista_paginas_centered_in_the_middle(self, paginas, actual, num, result):
        pagination = lista_paginas(paginas, actual, num)
        assert pagination == result

    @pytest.mark.parametrize('paginas, actual, num, result', [
        (20, 17, 2, [1, 0, 15, 16, 17, 18, 19, 20]),
        (20, 17, 4, [1, 0, 13, 14, 15, 16, 17, 18, 19, 20]),
        (20, 4, 3, [1, 2, 3, 4, 5, 6, 7, 0, 20]),
        (20, 4, 2, [1, 2, 3, 4, 5, 6, 0, 20]),
    ])
    def test_lista_paginas_shifted_to_an_extreme(self, paginas, actual, num, result):
        pagination = lista_paginas(paginas, actual, num)
        assert pagination == result
