

```python
import sys
import numpy as np
import sys
print(sys.version)

from YALL.utilities.ipynb.displays import *
from YALL.utilities.ipynb.filters import *
from YALL.utilities.ipynb.hdf import *
from YALL.utilities.tabulate import tabulate

from declarative import (
  OverridableObject, mproperty
)

import sympy
from YALL.utilities.ipynb.displays import *
from YALL.utilities.ipynb.ipy_sympy import *
import scipy.linalg
```

    3.5.3 (default, Apr 24 2017, 13:32:13) 
    [GCC 6.3.1 20161221 (Red Hat 6.3.1-1)]
    Sympy version:  1.0



```python
alpha = sympy.Matrix(sympy.var('alpha_1, alpha_2'))
a, b, c, d = sympy.var('a, b, c, d', commutative = False)
Sa, Sb, Sc, Sd = sympy.var('Sa, Sb, Sc, Sd', commutative = False)
T = sympy.Matrix([[a,b], [c, d]])
T_s = sympy.Matrix([[1-Sa,-Sb], [-Sc, 1-Sd]])
T

y, yc = sympy.var('y, y_c')
Q = sympy.Matrix([[1,0 * y * c.conjugate()], [-y.conjugate() * c, 1]])
Q_s = sympy.Matrix([[1,y * -Sc.conjugate()], [y.conjugate() * Sc, 1]])

subs_list = [(a, 1 - Sa), (b, -Sb), (c, -Sc), (d, 1-Sd)]
Q_s = Q.subs(subs_list)
T_s = T.subs(subs_list)

display(Q)

T_prime = Q * T
T_prime_s = Q_s * T_s
alpha_prime = Q * alpha

display(alpha_prime)
display(T_prime)
```


$$\left[\begin{matrix}1 & 0\\- \overline{y} c & 1\end{matrix}\right]$$



$$\left[\begin{matrix}\alpha_{1}\\- \alpha_{1} \overline{y} c + \alpha_{2}\end{matrix}\right]$$



$$\left[\begin{matrix}a & b\\- \overline{y} c a + c & - \overline{y} c b + d\end{matrix}\right]$$



```python

```


```python
display(alpha_prime.subs(subs_list))
display(Q_s * T_s)
S_prime = sympy.eye(2) - T_prime_s
S_prime.simplify()
display(S_prime)
```


$$\left[\begin{matrix}\alpha_{1}\\\alpha_{1} \overline{y} Sc + \alpha_{2}\end{matrix}\right]$$



$$\left[\begin{matrix}1 - Sa & - Sb\\\overline{y} Sc \left(1 - Sa\right) - Sc & - \overline{y} Sc Sb + 1 - Sd\end{matrix}\right]$$



$$\left[\begin{matrix}Sa & Sb\\- \overline{y} Sc \left(1 - Sa\right) + Sc & \overline{y} Sc Sb + Sd\end{matrix}\right]$$



```python

```


```python

```
